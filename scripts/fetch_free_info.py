import email.utils
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "news_sources.json"
OUT = ROOT / "latest" / "data" / "free-info.json"
BRIEF = ROOT / "latest" / "data" / "codexgate-news-brief-2026-09-03.md"

KEYWORDS = {
    "重要": ["codex", "agent", "openai", "github", "security", "safety", "release", "api"],
    "制作": ["image", "video", "audio", "design", "canvas", "game"],
    "開発": ["developer", "github", "npm", "python", "javascript", "api"],
    "研究": ["paper", "arxiv", "model", "benchmark", "training"],
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CODEXGATE-FreeInfo/1.0"})
    with urllib.request.urlopen(req, timeout=25) as res:
        return res.read()


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:220]


def parse_date(value):
    if not value:
        return ""
    try:
        return email.utils.parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception:
        return value[:40]


def score_item(title, summary, genre):
    s = f"{title} {summary}".lower()
    score = 1
    tags = [genre]
    for tag, words in KEYWORDS.items():
        if any(w in s for w in words):
            score += 1
            tags.append(tag)
    return min(score, 5), list(dict.fromkeys(tags))[:4]


def parse_rss(source, blob):
    root = ET.fromstring(blob)
    channel_items = root.findall(".//item")
    if not channel_items:
        channel_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    items = []
    for item in channel_items[:8]:
        title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or ""
        link = item.findtext("link") or ""
        atom_link = item.find("{http://www.w3.org/2005/Atom}link")
        if atom_link is not None:
            link = atom_link.attrib.get("href", link)
        desc = item.findtext("description") or item.findtext("summary") or item.findtext("{http://www.w3.org/2005/Atom}summary") or ""
        date = item.findtext("pubDate") or item.findtext("updated") or item.findtext("{http://www.w3.org/2005/Atom}updated") or ""
        title = clean(title)
        summary = clean(desc)
        score, tags = score_item(title, summary, source["genre"])
        items.append({
            "source": source["id"],
            "label": source["label"],
            "genre": source["genre"],
            "title": title,
            "summary": summary,
            "url": link,
            "published": parse_date(date),
            "score": score,
            "tags": tags,
        })
    return items


def parse_json(source, blob):
    data = json.loads(blob)
    items = []
    for f in data.get("features", [])[:8]:
        p = f.get("properties", {})
        title = clean(p.get("title", ""))
        summary = clean(p.get("place", ""))
        score, tags = score_item(title, summary, source["genre"])
        items.append({
            "source": source["id"],
            "label": source["label"],
            "genre": source["genre"],
            "title": title,
            "summary": summary,
            "url": p.get("url", source["url"]),
            "published": datetime.fromtimestamp((p.get("time") or 0) / 1000, timezone.utc).isoformat() if p.get("time") else "",
            "score": score,
            "tags": tags,
        })
    return items


def main():
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    collected = []
    errors = []
    for source in sources:
        try:
            blob = fetch(source["url"])
            if source["type"] == "json":
                collected.extend(parse_json(source, blob))
            else:
                collected.extend(parse_rss(source, blob))
        except Exception as exc:
            errors.append({"source": source["id"], "error": str(exc)[:160]})
    collected.sort(key=lambda x: (x["score"], x["published"]), reverse=True)
    top = collected[:24]
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "updatedAt": now,
        "mode": "free-fetch",
        "codexTokenUse": "0 when run by GitHub Actions",
        "sources": sources,
        "items": top,
        "errors": errors,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# CODEXGATE News Brief", "", f"- 更新: {now}", "- 取得: GitHub Actions/Python", "- Codex: 0%想定（自動実行時）", ""]
    for item in top[:10]:
        lines.append(f"- [{item['genre']}] {item['title'][:70]}")
    BRIEF.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
