import email.utils
import html
import json
import re
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "news_sources.json"
SCHEDULE = ROOT / "data" / "free_info_schedule.json"
OUT = ROOT / "latest" / "data" / "free-info.json"
AI_OUT = ROOT / "latest" / "data" / "ai-info.json"
WEATHER_OUT = ROOT / "latest" / "data" / "weather-info.json"
HEALTH_OUT = ROOT / "latest" / "data" / "gate-health.json"
SOURCE_CATALOG_OUT = ROOT / "latest" / "data" / "free-source-catalog.json"
SOCIAL_OUT = ROOT / "latest" / "data" / "social-trends.json"
BRIEF = ROOT / "latest" / "data" / "codexgate-news-brief-2026-09-03.md"
JMA_TOYAMA_WARNING = "https://www.jma.go.jp/bosai/warning/data/warning/160000.json"
GITHUB_RUNS = "https://api.github.com/repos/gouchin0326-source/codex-mobile-gate/actions/runs?per_page=8"

KEYWORDS = {
    "重要": ["codex", "agent", "openai", "github", "security", "safety", "release", "api"],
    "制作": ["image", "video", "audio", "design", "canvas", "game"],
    "開発": ["developer", "github", "npm", "python", "javascript", "api"],
    "研究": ["paper", "arxiv", "model", "benchmark", "training"],
}

DECISION_HINTS = {
    "AI": "AI/Codex運用の変化を確認",
    "開発": "CG開発・GitHub運用へ反映候補",
    "研究": "すぐ実装せず観察",
    "天気": "今日の作業環境メモ",
    "地震": "影響がある時だけ確認",
}

SOCIAL_SOURCES = [
    {
        "id": "mastodon-ai",
        "label": "Mastodon #AI",
        "platform": "Mastodon",
        "type": "mastodon",
        "genre": "SNS",
        "url": "https://mstdn.jp/api/v1/timelines/tag/AI?limit=20",
    },
    {
        "id": "mastodon-codex",
        "label": "Mastodon #Codex",
        "platform": "Mastodon",
        "type": "mastodon",
        "genre": "SNS",
        "url": "https://mstdn.jp/api/v1/timelines/tag/Codex?limit=20",
    },
    {
        "id": "reddit-localllama",
        "label": "Reddit LocalLLaMA",
        "platform": "Reddit",
        "type": "rss",
        "genre": "SNS",
        "url": "https://www.reddit.com/r/LocalLLaMA/.rss",
    },
]


def load_schedule():
    default = {
        "cadenceMinutes": 10,
        "allowedCadenceMinutes": [10, 30, 60, 180, 360, 720, 1440],
        "adaptiveWeather": True,
        "weatherRiskCadenceMinutes": 10,
        "minCadenceMinutes": 10,
        "maxCadenceMinutes": 1440,
    }
    if not SCHEDULE.exists():
        return default
    data = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    default.update(data)
    if "cadenceMinutes" not in default and "cadenceHours" in default:
        default["cadenceMinutes"] = int(default["cadenceHours"]) * 60
    if "weatherRiskCadenceMinutes" not in default and "weatherRiskCadenceHours" in default:
        default["weatherRiskCadenceMinutes"] = int(default["weatherRiskCadenceHours"]) * 60
    allowed = set(default.get("allowedCadenceMinutes") or [10, 30, 60, 180, 360, 720, 1440])
    cadence = int(default.get("cadenceMinutes") or 10)
    default["cadenceMinutes"] = cadence if cadence in allowed else 10
    default["weatherRiskCadenceMinutes"] = max(10, int(default.get("weatherRiskCadenceMinutes") or 10))
    return default


def latest_updated_at():
    if not OUT.exists():
        return None
    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        return parse_utc(data.get("updatedAt"))
    except Exception:
        return None


def latest_weather_risk():
    if not WEATHER_OUT.exists():
        return "unknown"
    try:
        data = json.loads(WEATHER_OUT.read_text(encoding="utf-8"))
        return (data.get("risk") or {}).get("level") or "unknown"
    except Exception:
        return "unknown"


def effective_cadence_minutes(schedule):
    if schedule.get("adaptiveWeather") and latest_weather_risk() not in {"normal", "unknown"}:
        return min(int(schedule["cadenceMinutes"]), int(schedule["weatherRiskCadenceMinutes"]))
    return int(schedule["cadenceMinutes"])


def should_fetch(now_dt, schedule):
    if "--force" in sys.argv or str(__import__("os").environ.get("FREE_INFO_FORCE", "")).lower() == "true":
        return True, "force"
    updated = latest_updated_at()
    if not updated:
        return True, "no previous data"
    cadence = effective_cadence_minutes(schedule)
    age_minutes = (now_dt - updated).total_seconds() / 60
    return age_minutes >= cadence, f"age {age_minutes:.1f}m / cadence {cadence}m"

SOURCE_CATALOG = [
    {
        "id": "weather-toyama",
        "status": "active",
        "genre": "天気",
        "provider": "Open-Meteo",
        "method": "documented no-key JSON API",
        "url": "https://open-meteo.com/en/docs",
        "cadence": "6h",
        "value": "富山の気温/雨/風/週間予報をCGで即判断",
        "legalPoint": "公開API。本文スクレイピングなし。",
        "nextApp": "線状降水帯級の危険表示を強化",
        "score": 5,
    },
    {
        "id": "jma-warning-toyama",
        "status": "active",
        "genre": "防災",
        "provider": "気象庁",
        "method": "public warning JSON",
        "url": "https://www.data.jma.go.jp/developer/index.html",
        "cadence": "6h",
        "value": "警報/注意報をCGトップ警告へ反映",
        "legalPoint": "気象庁データ利用案内に沿って取得。",
        "nextApp": "警報時だけ更新頻度を上げる",
        "score": 5,
    },
    {
        "id": "ai-official-rss",
        "status": "active",
        "genre": "AI",
        "provider": "OpenAI/GitHub/arXiv",
        "method": "official/public RSS",
        "url": "https://info.arxiv.org/help/rss.html",
        "cadence": "6h",
        "value": "AI/Codex開発に関係する一次情報を分類",
        "legalPoint": "RSSのタイトル/要約/URLのみ保存。記事全文複製なし。",
        "nextApp": "AI動向を重要度順の判断カードに圧縮",
        "score": 5,
    },
    {
        "id": "github-actions-health",
        "status": "active",
        "genre": "運用",
        "provider": "GitHub",
        "method": "public REST API",
        "url": "https://docs.github.com/en/rest/actions/workflow-runs",
        "cadence": "6h",
        "value": "CG自動更新の失敗/遅延を監視",
        "legalPoint": "公開リポジトリのActions API。",
        "nextApp": "失敗時にCGトップへ赤警告",
        "score": 4,
    },
    {
        "id": "earthquake-usgs",
        "status": "active",
        "genre": "防災",
        "provider": "USGS",
        "method": "public GeoJSON feed",
        "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php",
        "cadence": "6h",
        "value": "地震発生を低コストで蓄積",
        "legalPoint": "プログラム向けGeoJSON feed。",
        "nextApp": "日本周辺/富山影響だけ抽出",
        "score": 3,
    },
    {
        "id": "social-trends",
        "status": "active",
        "genre": "SNS",
        "provider": "Mastodon/Reddit",
        "method": "public timeline API + RSS",
        "url": "https://docs.joinmastodon.org/methods/timelines/",
        "cadence": "10m",
        "value": "AI/SNS動向を無料取得し、短い判断カードへ圧縮",
        "legalPoint": "公開API/RSS。全文保存せず短い抜粋とURL中心。",
        "nextApp": "急上昇語の推移とX代替監視",
        "score": 4,
    },
    {
        "id": "estat",
        "status": "candidate",
        "genre": "統計",
        "provider": "e-Stat",
        "method": "official API",
        "url": "https://www.e-stat.go.jp/api/",
        "cadence": "daily-weekly",
        "value": "人口/経済/地域統計をCG書庫に蓄積",
        "legalPoint": "API利用。キー要件あり。",
        "nextApp": "富山/全国の統計カード",
        "score": 4,
    },
    {
        "id": "bluesky-social",
        "status": "candidate",
        "genre": "SNS",
        "provider": "Bluesky",
        "method": "AT Protocol public API",
        "url": "https://bsky.network/docs/bluesky-api/",
        "cadence": "30m-1h",
        "value": "Bluesky公開投稿のAI動向取得",
        "legalPoint": "公式API利用。現環境では検索APIが403のため候補。",
        "nextApp": "取得可能endpointの再確認",
        "score": 3,
    },
    {
        "id": "local-archive-index",
        "status": "candidate",
        "genre": "ローカル知識",
        "provider": "Cドライブ",
        "method": "local file index",
        "url": "",
        "cadence": "daily",
        "value": "C:\\Codex配下の成果物/JSON/MDを索引化",
        "legalPoint": "自分のローカル成果物のみ。共有モデル/素材は編集禁止。",
        "nextApp": "CG書庫の自動索引",
        "score": 5,
    },
]


def build_source_catalog(now, sources, schedule):
    active = [x for x in SOURCE_CATALOG if x["status"] == "active"]
    candidate = [x for x in SOURCE_CATALOG if x["status"] == "candidate"]
    return {
        "updatedAt": now,
        "mode": "zero-token-source-catalog",
        "codexTokenUse": "0 when generated by GitHub Actions",
        "rule": "Use documented RSS/API/GeoJSON/local files. Do not scrape ordinary pages without permission.",
        "currentWorkflow": {
            "cadence": f"{effective_cadence_minutes(schedule)}m",
            "baseCadenceMinutes": schedule["cadenceMinutes"],
            "adaptiveWeather": bool(schedule.get("adaptiveWeather")),
            "weatherRiskCadenceMinutes": schedule.get("weatherRiskCadenceMinutes"),
            "file": ".github/workflows/free-info.yml",
            "settingFile": "data/free_info_schedule.json",
            "changeMethod": "GitHub Actions manual run input or edit JSON and push",
        },
        "counts": {
            "active": len(active),
            "candidate": len(candidate),
            "configuredSources": len(sources),
        },
        "active": sorted(active, key=lambda x: (-x["score"], x["genre"], x["id"])),
        "candidate": sorted(candidate, key=lambda x: (-x["score"], x["genre"], x["id"])),
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


def build_contexts(items):
    groups = {}
    for item in items:
        genre = item.get("genre") or "情報"
        groups.setdefault(genre, []).append(item)
    contexts = []
    for genre, rows in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
        rows = sorted(rows, key=lambda x: (x.get("score", 0), x.get("published", "")), reverse=True)
        top_titles = [r.get("title", "") for r in rows[:3] if r.get("title")]
        contexts.append({
            "genre": genre,
            "count": len(rows),
            "signal": " / ".join(top_titles)[:180],
            "decision": DECISION_HINTS.get(genre, "更新あり。必要時だけ確認"),
            "topUrl": rows[0].get("url", "") if rows else "",
            "score": max([r.get("score", 1) for r in rows] or [1]),
        })
    return contexts


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
            "platform": source.get("platform", source.get("genre", "")),
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


def parse_mastodon(source, blob):
    data = json.loads(blob)
    items = []
    for row in data[:12]:
        title = clean(row.get("content", ""))
        acct = ((row.get("account") or {}).get("acct") or "").strip()
        boosts = row.get("reblogs_count") or 0
        favs = row.get("favourites_count") or 0
        score, tags = score_item(title, acct, "SNS")
        items.append({
            "source": source["id"],
            "platform": source["platform"],
            "label": source["label"],
            "genre": "SNS",
            "author": acct,
            "title": title[:140],
            "summary": f"boost {boosts} / fav {favs}",
            "url": row.get("url") or "",
            "published": row.get("created_at") or "",
            "score": min(5, score + (1 if boosts or favs else 0)),
            "tags": tags,
        })
    return items


def parse_bluesky(source, blob):
    data = json.loads(blob)
    items = []
    for row in data.get("posts", [])[:12]:
        record = row.get("record") or {}
        text = clean(record.get("text", ""))
        author = (row.get("author") or {}).get("handle", "")
        score, tags = score_item(text, author, "SNS")
        items.append({
            "source": source["id"],
            "platform": source["platform"],
            "label": source["label"],
            "genre": "SNS",
            "author": author,
            "title": text[:140],
            "summary": f"reply {row.get('replyCount', 0)} / repost {row.get('repostCount', 0)} / like {row.get('likeCount', 0)}",
            "url": f"https://bsky.app/profile/{author}/post/{row.get('uri','').split('/')[-1]}" if author and row.get("uri") else "",
            "published": record.get("createdAt") or row.get("indexedAt") or "",
            "score": min(5, score + (1 if row.get("likeCount") else 0)),
            "tags": tags,
        })
    return items


def build_social_payload(now):
    items = []
    errors = []
    for source in SOCIAL_SOURCES:
        try:
            blob = fetch(source["url"])
            if source["type"] == "mastodon":
                items.extend(parse_mastodon(source, blob))
            elif source["type"] == "bluesky":
                items.extend(parse_bluesky(source, blob))
            else:
                items.extend(parse_rss(source, blob))
        except Exception as exc:
            errors.append({"source": source["id"], "platform": source["platform"], "error": str(exc)[:160]})
    items = sorted(items, key=lambda x: (x.get("score", 0), x.get("published", "")), reverse=True)[:36]
    platforms = {}
    for item in items:
        platforms.setdefault(item.get("platform", "SNS"), 0)
        platforms[item.get("platform", "SNS")] += 1
    top_words = {}
    for item in items:
        text = f"{item.get('title','')} {item.get('summary','')}".lower()
        for word in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text):
            if word in {"https", "http", "www", "com", "the", "and", "for", "with", "that"}:
                continue
            top_words[word] = top_words.get(word, 0) + 1
    trends = [{"word": k, "count": v} for k, v in sorted(top_words.items(), key=lambda x: (-x[1], x[0]))[:12]]
    return {
        "updatedAt": now,
        "mode": "zero-token-social-trends",
        "codexTokenUse": "0 when run by GitHub Actions",
        "policy": "public API/RSS only; no login bypass; no unauthorized scraping; short excerpts only",
        "cadence": "10m",
        "decision": "Xは有料寄り。Mastodon/Redditを主力、Blueskyは取得可否を監視。",
        "platformCounts": platforms,
        "trends": trends,
        "items": items,
        "sources": SOCIAL_SOURCES,
        "errors": errors,
    }


def parse_weather(source, blob):
    data = json.loads(blob)
    current = data.get("current", {})
    temp = current.get("temperature_2m")
    rain = current.get("precipitation")
    wind = current.get("wind_speed_10m")
    title = f"富山 {temp}℃ / 雨 {rain}mm / 風 {wind}km/h"
    score, tags = score_item(title, "", source["genre"])
    return [{
        "source": source["id"],
        "label": source["label"],
        "genre": source["genre"],
        "title": title,
        "summary": "Open-Meteo no-key weather fetch",
        "url": source["url"],
        "published": current.get("time", ""),
        "score": score,
        "tags": tags,
    }]


def build_ai_payload(items, now):
    ai_rows = [x for x in items if x.get("genre") in {"AI", "論文", "開発", "技術"}]
    ai_rows = sorted(ai_rows, key=lambda x: (x.get("score", 0), x.get("published", "")), reverse=True)[:24]
    focus = []
    for item in ai_rows[:8]:
        focus.append({
            "label": item.get("genre", "AI"),
            "title": item.get("title", ""),
            "why": "Codex/AI開発判断に関係" if item.get("score", 0) >= 3 else "観察枠",
            "source": item.get("label", ""),
            "url": item.get("url", ""),
        })
    groups = {}
    for item in ai_rows:
        groups.setdefault(item.get("genre", "AI"), []).append(item)
    cards = []
    for genre, rows in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
        top = sorted(rows, key=lambda x: (x.get("score", 0), x.get("published", "")), reverse=True)[:3]
        cards.append({
            "genre": genre,
            "count": len(rows),
            "decision": DECISION_HINTS.get(genre, "必要時だけ確認"),
            "signal": " / ".join([x.get("title", "") for x in top])[:220],
            "topUrl": top[0].get("url", "") if top else "",
            "score": max([x.get("score", 1) for x in rows] or [1]),
        })
    return {
        "updatedAt": now,
        "mode": "primary-rss-ai-context",
        "codexTokenUse": "0 when run by GitHub Actions",
        "policy": "official/public RSS only; no unauthorized scraping",
        "decision": "高scoreと開発影響だけ確認。本文読み込みは必要時のみ。",
        "topLine": focus[0]["title"] if focus else "AI一次情報なし",
        "cards": cards,
        "focus": focus,
        "items": ai_rows,
    }


def build_weather_payload(sources, now):
    weather_sources = [s for s in sources if s["type"] == "weather"]
    rows = []
    errors = []
    jma_warnings = []
    try:
        warning_data = json.loads(fetch(JMA_TOYAMA_WARNING))
        for area_type in warning_data.get("areaTypes", []):
            for area in area_type.get("areas", []):
                area_name = area.get("name", "")
                for warning in area.get("warnings", []):
                    status = warning.get("status", "")
                    kind = warning.get("kind", {}).get("name", "") if isinstance(warning.get("kind"), dict) else ""
                    if kind and status not in {"解除", "発表警報・注意報はなし"}:
                        jma_warnings.append({"area": area_name, "kind": kind, "status": status})
    except Exception as exc:
        errors.append({"source": "jma-toyama-warning", "error": str(exc)[:160]})

    for source in weather_sources:
        parsed = urllib.parse.urlparse(source["url"])
        qs = urllib.parse.parse_qs(parsed.query)
        qs["current"] = ["temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"]
        qs["hourly"] = ["temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m"]
        qs["daily"] = ["weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum"]
        qs["forecast_days"] = ["7"]
        hourly_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(qs, doseq=True)))
        try:
            data = json.loads(fetch(hourly_url))
            current = data.get("current", {})
            hourly = data.get("hourly", {})
            daily = data.get("daily", {})
            hours = []
            current_time = current.get("time", "")
            future_indexes = [i for i, t in enumerate(hourly.get("time", [])) if not current_time or t >= current_time]
            for i in future_indexes[:24]:
                t = hourly.get("time", [])[i]
                hours.append({
                    "time": t,
                    "temp": hourly.get("temperature_2m", [None] * 24)[i],
                    "humidity": hourly.get("relative_humidity_2m", [None] * 24)[i],
                    "feelsLike": hourly.get("apparent_temperature", [None] * 24)[i],
                    "rainProb": hourly.get("precipitation_probability", [None] * 24)[i],
                    "rain": hourly.get("precipitation", [None] * 24)[i],
                    "wind": hourly.get("wind_speed_10m", [None] * 24)[i],
                })
            days = []
            for i, t in enumerate(daily.get("time", [])[:7]):
                days.append({
                    "date": t,
                    "max": daily.get("temperature_2m_max", [None] * 7)[i],
                    "min": daily.get("temperature_2m_min", [None] * 7)[i],
                    "rain": daily.get("precipitation_sum", [None] * 7)[i],
                    "code": daily.get("weather_code", [None] * 7)[i],
                })
            rows.append({
                "source": source["id"],
                "label": source["label"],
                "location": "富山県",
                "updatedAt": now,
                "current": current,
                "hourly": hours,
                "daily": days,
                "decision": "雨確率と風を見て外出/作業判断",
                "url": hourly_url,
            })
        except Exception as exc:
            errors.append({"source": source["id"], "error": str(exc)[:160]})
    max_hourly_rain = max([x.get("rain") or 0 for row in rows for x in row.get("hourly", [])] or [0])
    max_rain_prob = max([x.get("rainProb") or 0 for row in rows for x in row.get("hourly", [])] or [0])
    max_wind = max([x.get("wind") or 0 for row in rows for x in row.get("hourly", [])] or [0])
    max_daily_rain = max([x.get("rain") or 0 for row in rows for x in row.get("daily", [])] or [0])
    risk_level = "normal"
    risk_label = "通常"
    risk_lines = ["富山: 通常", "警戒情報なし"]
    if jma_warnings:
        risk_level = "warning"
        risk_label = "警戒"
        kinds = "、".join(sorted({w["kind"] for w in jma_warnings})[:4])
        risk_lines = [f"富山: 気象庁 {kinds}", "詳細は天気アプリで確認"]
    elif max_hourly_rain >= 10 or max_daily_rain >= 50 or max_rain_prob >= 80 or max_wind >= 15:
        risk_level = "caution"
        risk_label = "注意"
        risk_lines = [f"富山: 雨{max_rain_prob}%/最大{max_hourly_rain}mm", f"風{max_wind}km/h・週間雨量最大{max_daily_rain}mm"]
    return {
        "updatedAt": now,
        "mode": "primary-api-weather-context",
        "codexTokenUse": "0 when run by GitHub Actions",
        "policy": "Open-Meteo documented no-key API + JMA warning JSON; no scraping",
        "risk": {
            "level": risk_level,
            "label": risk_label,
            "lines": risk_lines,
            "maxRainProbability": max_rain_prob,
            "maxHourlyRain": max_hourly_rain,
            "maxDailyRain": max_daily_rain,
            "maxWind": max_wind,
            "jmaWarnings": jma_warnings[:12],
        },
        "locations": rows,
        "errors": errors,
    }


def parse_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def build_health_payload(now, free_payload, ai_payload, weather_payload):
    errors = []
    runs = []
    try:
        data = json.loads(fetch(GITHUB_RUNS))
        for run in data.get("workflow_runs", [])[:8]:
            runs.append({
                "name": run.get("name", ""),
                "status": run.get("status", ""),
                "conclusion": run.get("conclusion", ""),
                "createdAt": run.get("created_at", ""),
                "updatedAt": run.get("updated_at", ""),
                "url": run.get("html_url", ""),
            })
    except Exception as exc:
        errors.append({"source": "github-actions", "error": str(exc)[:160]})
    now_dt = parse_utc(now) or datetime.now(timezone.utc)
    datasets = [
        {"id": "free-info", "label": "全体", "updatedAt": free_payload.get("updatedAt"), "errors": len(free_payload.get("errors", [])), "count": len(free_payload.get("items", []))},
        {"id": "ai-info", "label": "AI", "updatedAt": ai_payload.get("updatedAt"), "errors": 0, "count": len(ai_payload.get("items", []))},
        {"id": "weather-info", "label": "天気", "updatedAt": weather_payload.get("updatedAt"), "errors": len(weather_payload.get("errors", [])), "count": len(weather_payload.get("locations", []))},
    ]
    health_level = "normal"
    lines = ["CG: 自動更新正常", "Actions/JSONを監視中"]
    for ds in datasets:
        updated = parse_utc(ds.get("updatedAt"))
        ds["ageHours"] = round((now_dt - updated).total_seconds() / 3600, 1) if updated else None
        if ds["errors"] or ds["ageHours"] is None or ds["ageHours"] > 12:
            health_level = "warning"
    failed_runs = [r for r in runs if r.get("conclusion") in {"failure", "cancelled", "timed_out"}]
    active_runs = [r for r in runs if r.get("status") != "completed"]
    if failed_runs:
        health_level = "warning"
        lines = [f"CG: Actions失敗 {len(failed_runs)}件", "詳細はCG監視を確認"]
    elif active_runs:
        health_level = "caution"
        lines = ["CG: Actions実行中", "更新完了待ち"]
    elif health_level == "warning":
        lines = ["CG: データ更新に注意", "JSON鮮度/errorを確認"]
    return {
        "updatedAt": now,
        "mode": "operation-zero-gate-health",
        "codexTokenUse": "0 when run by GitHub Actions",
        "level": health_level,
        "lines": lines,
        "datasets": datasets,
        "runs": runs,
        "errors": errors,
    }


def main():
    schedule = load_schedule()
    now_dt = datetime.now(timezone.utc)
    due, reason = should_fetch(now_dt, schedule)
    if not due:
        print(f"skip free-info: {reason}")
        return
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    collected = []
    errors = []
    for source in sources:
        try:
            blob = fetch(source["url"])
            if source["type"] == "weather":
                collected.extend(parse_weather(source, blob))
            elif source["type"] == "json":
                collected.extend(parse_json(source, blob))
            else:
                collected.extend(parse_rss(source, blob))
        except Exception as exc:
            errors.append({"source": source["id"], "error": str(exc)[:160]})
    collected.sort(key=lambda x: (x["score"], x["published"]), reverse=True)
    top = []
    seen_sources = set()
    for item in collected:
        if item["source"] not in seen_sources:
            top.append(item)
            seen_sources.add(item["source"])
    for item in collected:
        if item not in top:
            top.append(item)
        if len(top) >= 32:
            break
    now = now_dt.isoformat()
    contexts = build_contexts(top)
    ai_payload = build_ai_payload(top, now)
    weather_payload = build_weather_payload(sources, now)
    payload = {
        "updatedAt": now,
        "mode": "free-fetch-context",
        "codexTokenUse": "0 when run by GitHub Actions",
        "freeMeaning": "Public RSS/API data is fetched by program, categorized, scored, and summarized into local static JSON. It is not a bookmark list and does not scrape ordinary web pages.",
        "accessPolicy": {
            "allowed": ["official RSS", "public JSON API", "public GeoJSON API", "provider documented no-key API"],
            "blocked": ["unauthorized scraping", "login bypass", "paywall extraction", "bulk copying article text"],
        },
        "levels": [
            {"id": "zero", "label": "完全無料", "cost": "Codex 0%", "route": "GitHub Actions + RSS/API + JSON"},
            {"id": "small", "label": "少量", "cost": "Codex少量", "route": "20行メモだけCodexで反映"},
            {"id": "external", "label": "外部AI節約", "cost": "Codex小", "route": "外部AIで調査/圧縮、Codexは実装"}
        ],
        "sources": sources,
        "schedule": {
            "cadenceMinutes": schedule["cadenceMinutes"],
            "effectiveCadenceMinutes": effective_cadence_minutes(schedule),
            "adaptiveWeather": bool(schedule.get("adaptiveWeather")),
            "weatherRiskCadenceMinutes": schedule.get("weatherRiskCadenceMinutes"),
        },
        "contexts": contexts,
        "items": top,
        "errors": errors,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    AI_OUT.write_text(json.dumps(ai_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    WEATHER_OUT.write_text(json.dumps(weather_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    HEALTH_OUT.write_text(json.dumps(build_health_payload(now, payload, ai_payload, weather_payload), ensure_ascii=False, indent=2), encoding="utf-8")
    SOURCE_CATALOG_OUT.write_text(json.dumps(build_source_catalog(now, sources, schedule), ensure_ascii=False, indent=2), encoding="utf-8")
    SOCIAL_OUT.write_text(json.dumps(build_social_payload(now), ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# CODEXGATE News Brief", "", f"- 更新: {now}", "- 取得: GitHub Actions/Python", "- Codex: 0%想定（自動実行時）", "- 方針: RSS/API取得→分類→採決メモ化。ブックマーク集ではない。", ""]
    for ctx in contexts[:8]:
        lines.append(f"- [{ctx['genre']}] {ctx['decision']} / {ctx['signal'][:70]}")
    BRIEF.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
