import json
import tempfile
from pathlib import Path

from build_today import build_payload, safe_url, to_csv


def sample_item(n, genre="開発", url=None):
    return {
        "source": f"source-{n}", "label": f"情報源{n}", "genre": genre,
        "title": f"確認事項 {n}", "url": url or f"https://example.com/{n}",
        "published": f"2026-09-07T00:{n % 60:02d}:00+00:00", "score": 9 - n,
    }


def main():
    source = {
        "status": "fresh", "updatedAt": "2026-09-07T00:00:00+00:00", "errors": [],
        "items": [sample_item(n, "開発" if n < 4 else f"分類{n}") for n in range(8)] + [
            sample_item(9, "開発", "javascript:alert(1)"),
            {**sample_item(10, "災害"), "source": "usgs", "title": "M 2.0 - Alaska"},
        ],
    }
    payload = build_payload(source, "2026-09-07T01:00:00+00:00")
    assert payload["count"] == 5
    assert sum(item["genre"] == "開発" for item in payload["items"]) == 2
    required = {"title", "reason", "publishedAt", "observedAt", "source", "url"}
    assert all(required <= item.keys() for item in payload["items"])
    assert all(item["url"].startswith("https://") for item in payload["items"])
    assert all("Alaska" not in item["title"] for item in payload["items"])
    assert len(to_csv(payload).splitlines()) == 6

    empty = build_payload({"status": "unavailable", "items": [{"title": "URLなし"}]}, "2026-09-07T01:00:00+00:00")
    assert empty["status"] == "unavailable" and empty["items"] == []
    assert empty["message"] == "今日の確認事項はありません"
    assert safe_url("javascript:alert(1)") == ""

    root = Path(__file__).resolve().parents[1]
    page = (root / "latest" / "zero-token-army" / "index.html").read_text(encoding="utf-8")
    assert "data/today.json" in page and "data/today.csv" in page
    assert "textContent" in page and "aria-live" in page
    for index in (root / "index.html", root / "latest" / "index.html"):
        text = index.read_text(encoding="utf-8")
        assert "today.json" in text

    workflow = (root / ".github" / "workflows" / "free-info.yml").read_text(encoding="utf-8")
    assert "build_today.py" in workflow and "latest/data/today.json" in workflow and "latest/data/today.csv" in workflow
    print("Z2 checks passed: max five, genre cap, reasons/source/time, safe empty state, JSON/CSV, CG links")


if __name__ == "__main__":
    main()
