import email.utils
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path


class SourceReuse(Exception):
    """The caller must reuse its previously parsed payload."""

    def __init__(self, source_id, reason):
        super().__init__(f"{source_id}: {reason}")
        self.source_id = source_id
        self.reason = reason


class FetchPolicyError(RuntimeError):
    pass


def parse_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


class FetchController:
    def __init__(self, config_path, state_path, now, force=False, opener=None):
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        self.now = now.astimezone(timezone.utc)
        self.force = force
        self.opener = opener or urllib.request.urlopen
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.sources = {row["id"]: row for row in self.config["sources"] if row.get("enabled", True)}
        self.state = self._load_state()
        self.run_requests = 0
        self.run_bytes = 0

    def _load_state(self):
        default = {"version": 1, "daily": {}, "sources": {}}
        if not self.state_path.exists():
            return default
        try:
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return default
            loaded.setdefault("version", 1)
            loaded.setdefault("daily", {})
            loaded.setdefault("sources", {})
            return loaded
        except (OSError, ValueError):
            return default

    def _daily(self):
        day = self.now.date().isoformat()
        daily = self.state.setdefault("daily", {})
        if daily.get("date") != day:
            daily.clear()
            daily.update({"date": day, "httpRequests": 0, "responseBytes": 0})
        return daily

    def _source_state(self, source_id):
        return self.state.setdefault("sources", {}).setdefault(source_id, {})

    def _validate_url(self, source, url):
        parsed = urllib.parse.urlparse(url)
        allowed_hosts = set(source.get("allowedHosts") or [])
        if parsed.scheme != "https" or not parsed.hostname or parsed.hostname not in allowed_hosts:
            raise FetchPolicyError(f"blocked URL for {source['id']}: HTTPS host is not allowlisted")

    def _is_due(self, source, state):
        retry_at = parse_utc(state.get("retryAfterAt"))
        if retry_at and self.now < retry_at:
            return False, "retry-after"
        if self.force:
            return True, "force"
        attempted = parse_utc(state.get("lastAttemptAt"))
        if not attempted:
            return True, "first-run"
        interval = timedelta(minutes=max(1, int(source["intervalMinutes"])))
        if self.now - attempted < interval:
            return False, "not-due"
        return True, "due"

    def _check_budget(self, source):
        budgets = self.config["budgets"]
        daily = self._daily()
        if self.run_requests >= int(budgets["maxRequestsPerRun"]):
            raise FetchPolicyError("per-run request budget exhausted")
        if int(daily.get("httpRequests", 0)) >= int(budgets["maxRequestsPerDay"]):
            raise FetchPolicyError("daily request budget exhausted")
        if int(daily.get("responseBytes", 0)) >= int(budgets["maxBytesPerDay"]):
            raise FetchPolicyError("daily byte budget exhausted")
        return min(int(source.get("maxBytes") or budgets["defaultMaxBytesPerResponse"]), int(budgets["maxBytesPerDay"]))

    def has_due_sources(self):
        budgets = self.config["budgets"]
        daily = self._daily()
        if int(daily.get("httpRequests", 0)) >= int(budgets["maxRequestsPerDay"]):
            return False
        if int(daily.get("responseBytes", 0)) >= int(budgets["maxBytesPerDay"]):
            return False
        return any(self._is_due(source, self._source_state(source_id))[0] for source_id, source in self.sources.items())

    def _count_request(self):
        daily = self._daily()
        self.run_requests += 1
        daily["httpRequests"] = int(daily.get("httpRequests", 0)) + 1

    def _count_bytes(self, count):
        daily = self._daily()
        self.run_bytes += count
        daily["responseBytes"] = int(daily.get("responseBytes", 0)) + count

    def _retry_after(self, value):
        if not value:
            return self.now + timedelta(minutes=60)
        try:
            return self.now + timedelta(seconds=max(60, int(value)))
        except (TypeError, ValueError):
            try:
                parsed = email.utils.parsedate_to_datetime(value).astimezone(timezone.utc)
                return max(parsed, self.now + timedelta(minutes=1))
            except (TypeError, ValueError, OverflowError):
                return self.now + timedelta(minutes=60)

    def fetch(self, source_id, url, has_previous=False):
        source = self.sources.get(source_id)
        if not source:
            raise FetchPolicyError(f"source is not configured: {source_id}")
        self._validate_url(source, url)
        state = self._source_state(source_id)
        due, reason = self._is_due(source, state)
        if not due:
            raise SourceReuse(source_id, reason)
        max_bytes = self._check_budget(source)
        headers = {"User-Agent": "CODEXGATE-FreeInfo/2.0"}
        if state.get("etag"):
            headers["If-None-Match"] = state["etag"]
        if state.get("lastModified"):
            headers["If-Modified-Since"] = state["lastModified"]
        request = urllib.request.Request(url, headers=headers)
        state["lastAttemptAt"] = self.now.isoformat()
        self._count_request()
        try:
            with self.opener(request, timeout=int(self.config["budgets"].get("timeoutSeconds", 10))) as response:
                final_url = response.geturl() if hasattr(response, "geturl") else url
                self._validate_url(source, final_url)
                blob = response.read(max_bytes + 1)
                self._count_bytes(len(blob))
                if len(blob) > max_bytes:
                    raise FetchPolicyError(f"response exceeds {max_bytes} byte limit")
                state.update({
                    "status": "fresh",
                    "lastSuccessAt": self.now.isoformat(),
                    "contentUpdatedAt": self.now.isoformat(),
                    "consecutiveFailures": 0,
                    "errorCode": None,
                    "retryAfterAt": None,
                    "etag": response.headers.get("ETag") or state.get("etag"),
                    "lastModified": response.headers.get("Last-Modified") or state.get("lastModified"),
                    "lastHttpStatus": getattr(response, "status", 200),
                })
                return blob
        except urllib.error.HTTPError as exc:
            if exc.code == 304:
                state.update({
                    "status": "fresh" if has_previous else "unavailable",
                    "lastSuccessAt": self.now.isoformat() if has_previous else state.get("lastSuccessAt"),
                    "consecutiveFailures": 0,
                    "errorCode": None if has_previous else "304-without-cache",
                    "lastHttpStatus": 304,
                })
                if has_previous:
                    raise SourceReuse(source_id, "not-modified")
                raise FetchPolicyError("304 received without previous parsed payload")
            state["lastHttpStatus"] = exc.code
            state["consecutiveFailures"] = int(state.get("consecutiveFailures", 0)) + 1
            state["status"] = "stale" if has_previous else "unavailable"
            state["errorCode"] = f"http-{exc.code}"
            if exc.code == 429:
                state["retryAfterAt"] = self._retry_after(exc.headers.get("Retry-After")).isoformat()
            raise
        except Exception as exc:
            state["consecutiveFailures"] = int(state.get("consecutiveFailures", 0)) + 1
            state["status"] = "stale" if has_previous else "unavailable"
            state["errorCode"] = type(exc).__name__
            raise

    def public_state(self, source_id, has_previous=False):
        source = self.sources.get(source_id, {})
        state = dict(self._source_state(source_id))
        last_success = parse_utc(state.get("lastSuccessAt"))
        ttl = timedelta(minutes=int(source.get("ttlMinutes") or 0))
        if last_success and ttl and self.now - last_success > ttl:
            status = "stale" if has_previous else "unavailable"
        else:
            status = state.get("status") or ("stale" if has_previous else "unavailable")
        return {
            "id": source_id,
            "status": status,
            "lastSuccessAt": state.get("lastSuccessAt"),
            "lastAttemptAt": state.get("lastAttemptAt"),
            "retryAfterAt": state.get("retryAfterAt"),
            "errorCode": state.get("errorCode"),
        }

    def save(self):
        self.state["updatedAt"] = self.now.isoformat()
        self.state["lastRun"] = {"httpRequests": self.run_requests, "responseBytes": self.run_bytes}
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
