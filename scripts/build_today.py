import csv
import io
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
FREE_INFO = ROOT / "latest" / "data" / "free-info.json"
TODAY = ROOT / "latest" / "data" / "today.json"
TODAY_CSV = ROOT / "latest" / "data" / "today.csv"
MAX_ITEMS = 5
MAX_PER_GENRE = 2
FRESH_WINDOW = timedelta(hours=36)


def clean_text(value, limit=240):
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def safe_url(value):
    try:
        parts = urlsplit(str(value or ""))
    except ValueError:
        return ""
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def reason_for(item):
    genre = clean_text(item.get("genre") or item.get("platform"), 30) or "情報"
    if item.get("stale"):
        return f"{genre}の前回取得値です。更新停止の可能性を確認"
    score = item.get("score", 0)
    if isinstance(score, (int, float)) and score >= 3:
        return f"{genre}の新着で、設定した重要語と一致"
    return f"{genre}の新着を確認"


def parse_time(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def build_payload(source, observed_at=None):
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()
    observed_dt = parse_time(observed_at) or datetime.now(timezone.utc)
    if not isinstance(source, dict):
        source = {}
    dataset_status = source.get("status", "unavailable")
    candidates = []
    seen_urls = set()
    for position, item in enumerate(source.get("items") or []):
        if not isinstance(item, dict):
            continue
        title = clean_text(item.get("title"))
        url = safe_url(item.get("url"))
        if not title or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        genre = clean_text(item.get("genre") or item.get("platform"), 30) or "情報"
        published = clean_text(item.get("published") or item.get("publishedAt"), 50)
        published_dt = parse_time(published)
        if not published_dt or observed_dt - published_dt > FRESH_WINDOW or published_dt - observed_dt > timedelta(hours=1):
            continue
        if genre == "災害" and clean_text(item.get("source"), 50) == "usgs" and not re.search(r"Japan|日本|富山|石川|新潟", title, re.I):
            continue
        score = item.get("score", 0)
        score = score if isinstance(score, (int, float)) else 0
        candidates.append({
            "id": f"{clean_text(item.get('source'), 50) or 'source'}:{position}",
            "genre": genre,
            "title": title,
            "reason": reason_for(item),
            "publishedAt": published or None,
            "observedAt": clean_text(source.get("lastSuccessAt") or source.get("updatedAt"), 50) or observed_at,
            "source": clean_text(item.get("label") or item.get("source"), 80) or "情報源",
            "url": url,
            "score": score,
            "stale": bool(item.get("stale") or dataset_status != "fresh"),
            "processing": "rule-based",
            "_publishedTs": published_dt.timestamp(),
        })

    candidates.sort(key=lambda row: (row["genre"] in {"災害", "天気"}, row["score"], row["_publishedTs"]), reverse=True)
    picked = []
    genre_counts = {}
    for row in candidates:
        if genre_counts.get(row["genre"], 0) >= MAX_PER_GENRE:
            continue
        picked.append(row)
        genre_counts[row["genre"]] = genre_counts.get(row["genre"], 0) + 1
        if len(picked) == MAX_ITEMS:
            break
    for row in picked:
        row.pop("_publishedTs", None)

    status = "fresh" if dataset_status == "fresh" and picked else ("stale" if picked else "unavailable")
    return {
        "updatedAt": observed_at,
        "sourceUpdatedAt": source.get("lastSuccessAt") or source.get("updatedAt"),
        "status": status,
        "mode": "today-rule-based",
        "codexTokenUse": "0 when run by GitHub Actions",
        "count": len(picked),
        "message": "今日の確認事項はありません" if not picked else "最大5件をルールで選択",
        "limits": {"maxItems": MAX_ITEMS, "maxPerGenre": MAX_PER_GENRE},
        "items": picked,
        "errors": source.get("errors") or [],
    }


def to_csv(payload):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["genre", "title", "reason", "publishedAt", "observedAt", "source", "url", "status"])
    for item in payload["items"]:
        writer.writerow([
            item["genre"], item["title"], item["reason"], item["publishedAt"] or "",
            item["observedAt"], item["source"], item["url"], "stale" if item["stale"] else "fresh",
        ])
    return stream.getvalue()


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else FREE_INFO
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else TODAY
    csv_path = Path(sys.argv[3]) if len(sys.argv) > 3 else TODAY_CSV
    try:
        source = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        source = {"status": "unavailable", "items": [], "errors": [{"source": "free-info", "error": "input-unavailable"}]}
    payload = build_payload(source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path.write_text(to_csv(payload), encoding="utf-8-sig")
    print(f"today items={payload['count']} status={payload['status']}")


if __name__ == "__main__":
    main()
