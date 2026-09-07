import json
from datetime import date
from pathlib import Path

from fetch_holidays import build_payload, parse_official_csv, to_csv, to_ics


def main():
    fixture = "国民の祝日・休日月日,国民の祝日・休日名称\n2026/9/21,敬老の日\n2026/9/22,休日\n2026/9/23,秋分の日\n".encode("cp932")
    rows = parse_official_csv(fixture)
    payload = build_payload(rows, date(2026, 9, 8), "2026-09-08T00:00:00+00:00")
    assert payload["nextHoliday"] == {"date": "2026-09-21", "name": "敬老の日", "daysUntil": 13}
    assert payload["asOf"] == "2026-09-08"
    assert payload["coverageThrough"] == "2026-09-23" and len(payload["items"]) == 3
    holiday_csv = to_csv(payload)
    assert len(holiday_csv.splitlines()) == 4 and "2026-09-21,敬老の日,13," in holiday_csv
    ics = to_ics(payload)
    assert "DTSTART;VALUE=DATE:20260921" in ics and "SUMMARY:敬老の日" in ics
    missing = build_payload(rows, date(2026, 9, 24), "2026-09-24T00:00:00+00:00")
    assert missing["status"] == "unavailable" and missing["nextHoliday"] is None and missing["items"] == []

    root = Path(__file__).resolve().parents[1]
    page = (root / "latest" / "zero-token-army" / "index.html").read_text(encoding="utf-8")
    for name in ("holidays.json", "holidays.csv", "holidays.ics"):
        assert name in page
    workflow = (root / ".github" / "workflows" / "free-info.yml").read_text(encoding="utf-8")
    assert "fetch_holidays.py" in workflow and "check_free_info_z3.py" in workflow
    policy = json.loads((root / "data" / "free_sources_v2.json").read_text(encoding="utf-8"))
    source = next(item for item in policy["sources"] if item["id"] == "cabinet-office-holidays")
    assert source["intervalMinutes"] == 10080 and source["allowedHosts"] == ["www8.cao.go.jp"]
    print("Z3 checks passed: official CP932 CSV, next holiday, coverage fail-closed, JSON/CSV/ICS, CG links")


if __name__ == "__main__":
    main()
