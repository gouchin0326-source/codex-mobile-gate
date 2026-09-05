import json
import tempfile
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

from free_fetch_runtime import FetchController, FetchPolicyError, SourceReuse


class FakeResponse:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, limit):
        return self.body[:limit]


def expect(exception, function):
    try:
        function()
    except exception as exc:
        return exc
    raise AssertionError(f"expected {exception.__name__}")


def write_config(path, max_run=20, max_bytes=32):
    path.write_text(json.dumps({
        "version": 2,
        "budgets": {
            "maxRequestsPerRun": max_run,
            "maxRequestsPerDay": 3,
            "maxBytesPerDay": 64,
            "defaultMaxBytesPerResponse": max_bytes,
            "maxConcurrency": 3,
            "timeoutSeconds": 10,
        },
        "sources": [
            {"id": "alpha", "enabled": True, "intervalMinutes": 60, "ttlMinutes": 120, "maxBytes": max_bytes, "allowedHosts": ["example.com"]},
            {"id": "beta", "enabled": True, "intervalMinutes": 60, "ttlMinutes": 120, "maxBytes": max_bytes, "allowedHosts": ["example.org"]},
        ],
    }), encoding="utf-8")


def main():
    now = datetime(2026, 9, 5, 0, 0, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config = root / "sources.json"
        state = root / "state.json"
        write_config(config)
        requests = []

        def first_open(request, timeout):
            requests.append((request, timeout))
            return FakeResponse(b"fresh", headers={"ETag": '"v1"', "Last-Modified": "Fri, 05 Sep 2026 00:00:00 GMT"})

        controller = FetchController(config, state, now, opener=first_open)
        assert controller.fetch("alpha", "https://example.com/feed", has_previous=False) == b"fresh"
        assert requests[0][1] == 10
        controller.save()
        saved = json.loads(state.read_text(encoding="utf-8"))
        assert saved["daily"]["httpRequests"] == 1
        assert saved["daily"]["responseBytes"] == 5
        assert saved["lastRun"]["aiRequests"] == 0

        not_due = FetchController(config, state, now + timedelta(minutes=30), opener=lambda *_a, **_k: None)
        assert not_due.has_due_sources() is True  # beta has never run
        reuse = expect(SourceReuse, lambda: not_due.fetch("alpha", "https://example.com/feed", has_previous=True))
        assert reuse.reason == "not-due"
        assert not_due.run_requests == 0

        conditional = []

        def not_modified(request, timeout):
            conditional.append(request)
            raise urllib.error.HTTPError(request.full_url, 304, "Not Modified", {}, None)

        revalidate = FetchController(config, state, now + timedelta(minutes=61), opener=not_modified)
        reuse = expect(SourceReuse, lambda: revalidate.fetch("alpha", "https://example.com/feed", has_previous=True))
        assert reuse.reason == "not-modified"
        header_names = {key.lower(): value for key, value in conditional[0].header_items()}
        assert header_names["if-none-match"] == '"v1"'
        assert "if-modified-since" in header_names
        assert revalidate.public_state("alpha", True)["status"] == "fresh"

        def rate_limited(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 429, "Too Many Requests", {"Retry-After": "120"}, None)

        limited = FetchController(config, state, now + timedelta(minutes=62), force=True, opener=rate_limited)
        expect(urllib.error.HTTPError, lambda: limited.fetch("beta", "https://example.org/feed", has_previous=True))
        retry_at = limited.public_state("beta", True)["retryAfterAt"]
        assert retry_at == (now + timedelta(minutes=64)).isoformat()
        stopped = FetchController(config, state, now + timedelta(minutes=63), opener=lambda *_a, **_k: None)
        stopped.state = limited.state
        reuse = expect(SourceReuse, lambda: stopped.fetch("beta", "https://example.org/feed", has_previous=True))
        assert reuse.reason == "retry-after"

        budget_config = root / "budget.json"
        budget_state = root / "budget-state.json"
        write_config(budget_config, max_run=1)
        budget = FetchController(budget_config, budget_state, now, opener=lambda *_a, **_k: FakeResponse(b"ok"))
        budget.fetch("alpha", "https://example.com/a")
        expect(FetchPolicyError, lambda: budget.fetch("beta", "https://example.org/b"))

        size_config = root / "size.json"
        write_config(size_config, max_bytes=4)
        oversized = FetchController(size_config, root / "size-state.json", now, opener=lambda *_a, **_k: FakeResponse(b"12345"))
        expect(FetchPolicyError, lambda: oversized.fetch("alpha", "https://example.com/a"))
        expect(FetchPolicyError, lambda: oversized.fetch("alpha", "http://example.com/a"))
        expect(FetchPolicyError, lambda: oversized.fetch("alpha", "https://evil.example/a"))

    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "free-info.yml").read_text(encoding="utf-8")
    assert "concurrency:" in workflow
    assert "timeout-minutes:" in workflow
    assert "data/free_info_state.json" in workflow
    assert "Verify Pages source route" in workflow
    print("Z1 checks passed: cadence/TTL, conditional GET, 429 backoff, budgets, allowlist, workflow")


if __name__ == "__main__":
    main()
