import csv
import io
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
REFERENCE_URL = "https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html"
JSON_PATH = ROOT / "latest" / "data" / "holidays.json"
CSV_PATH = ROOT / "latest" / "data" / "holidays.csv"
ICS_PATH = ROOT / "latest" / "data" / "holidays.ics"
CACHE_TTL = timedelta(days=7)


def parse_official_csv(raw):
    text = raw.decode("cp932")
    rows = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2:
            continue
        try:
            holiday_date = datetime.strptime(row[0].strip(), "%Y/%m/%d").date()
        except ValueError:
            continue
        name = row[1].strip()
        if name:
            rows.append({"date": holiday_date.isoformat(), "name": name})
    rows.sort(key=lambda item: item["date"])
    return rows


def build_payload(rows, today=None, updated_at=None):
    today = today or datetime.now().astimezone().date()
    updated_at = updated_at or datetime.now(timezone.utc).isoformat()
    published = [item for item in rows if item["date"] >= today.isoformat()]
    next_holiday = None
    if published:
        next_holiday = dict(published[0])
        next_holiday["daysUntil"] = (date.fromisoformat(next_holiday["date"]) - today).days
    return {
        "updatedAt": updated_at,
        "asOf": today.isoformat(),
        "status": "fresh" if next_holiday else "unavailable",
        "mode": "official-csv-rule-based",
        "codexTokenUse": 0,
        "source": "内閣府 国民の祝日CSV",
        "sourceUrl": SOURCE_URL,
        "referenceUrl": REFERENCE_URL,
        "coverageThrough": rows[-1]["date"] if rows else None,
        "message": "掲載範囲内の次の祝日" if next_holiday else "掲載範囲内に次の祝日はありません",
        "nextHoliday": next_holiday,
        "items": published,
        "errors": [],
    }


def to_csv(payload):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["date", "name", "daysUntil", "sourceUrl"])
    for item in payload["items"]:
        days = (date.fromisoformat(item["date"]) - date.fromisoformat(payload["asOf"])).days
        writer.writerow([item["date"], item["name"], days, payload["sourceUrl"]])
    return stream.getvalue()


def ics_escape(value):
    return str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def to_ics(payload):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CODEXGATE//Official Japan Holidays//JA", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:日本の祝日（内閣府）"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for item in payload["items"]:
        start = date.fromisoformat(item["date"])
        lines.extend([
            "BEGIN:VEVENT", f"UID:{start:%Y%m%d}-holiday@codexgate",
            f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{start.fromordinal(start.toordinal() + 1):%Y%m%d}",
            f"SUMMARY:{ics_escape(item['name'])}", f"URL:{payload['referenceUrl']}", "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def fetch_bytes():
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "CODEXGATE-Holiday/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read(524289)
    if len(raw) > 524288:
        raise ValueError("official CSV exceeds 512 KiB limit")
    return raw


def recent_cache(now=None):
    if os.getenv("FREE_INFO_FORCE", "").lower() == "true":
        return None
    now = now or datetime.now(timezone.utc)
    try:
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        updated = datetime.fromisoformat(payload["updatedAt"].replace("Z", "+00:00"))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if payload.get("status") == "fresh" and now - updated.astimezone(timezone.utc) < CACHE_TTL:
        return payload
    return None


def write_outputs(payload):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CSV_PATH.write_text(to_csv(payload), encoding="utf-8-sig")
    ICS_PATH.write_bytes(to_ics(payload).encode("utf-8"))


def main():
    cached = recent_cache()
    if cached:
        print(f"holidays status=fresh cachedUntil={cached.get('coverageThrough')}")
        return 0
    try:
        rows = parse_official_csv(fetch_bytes())
        if not rows:
            raise ValueError("official CSV has no valid holiday rows")
        payload = build_payload(rows)
    except Exception as exc:
        try:
            payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
            payload["status"] = "stale"
            payload["message"] = "取得できないため前回値を表示"
            payload["errors"] = [{"source": "cabinet-office-holidays", "error": type(exc).__name__}]
        except (OSError, json.JSONDecodeError):
            payload = build_payload([])
            payload["errors"] = [{"source": "cabinet-office-holidays", "error": type(exc).__name__}]
    write_outputs(payload)
    print(f"holidays status={payload['status']} next={payload.get('nextHoliday')}")
    return 0 if payload["status"] in {"fresh", "stale"} else 1


if __name__ == "__main__":
    sys.exit(main())
