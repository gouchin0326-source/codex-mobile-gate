import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_free_info.py"
SPEC = importlib.util.spec_from_file_location("fetch_free_info", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    sources = json.loads((ROOT / "data" / "news_sources.json").read_text(encoding="utf-8"))
    source_ids = {row["id"] for row in sources}
    assert {"openai", "google-gemini", "anthropic-claude"} <= source_ids

    sitemap = b'''<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://www.anthropic.com/news/claude-test</loc><lastmod>2026-09-12</lastmod></url>
      <url><loc>https://www.anthropic.com/company</loc><lastmod>2026-09-13</lastmod></url>
    </urlset>'''
    claude_source = next(row for row in sources if row["id"] == "anthropic-claude")
    parsed = MODULE.parse_sitemap(claude_source, sitemap)
    assert len(parsed) == 1
    assert parsed[0]["provider"] == "claude"
    assert parsed[0]["published"] == "2026-09-12"

    sample = [
        {"source": "openai", "provider": "chatgpt", "label": "OpenAI", "genre": "AI", "title": "OpenAI update", "summary": "release", "url": "https://openai.com/news/test", "published": "2026-09-13", "score": 5},
        {"source": "google-gemini", "provider": "gemini", "label": "Gemini", "genre": "AI", "title": "Gemini update", "summary": "release", "url": "https://blog.google/test", "published": "2026-09-13", "score": 5},
        parsed[0],
    ]
    sample.extend({"source": f"filler-{index}", "label": "Filler", "genre": "AI", "title": f"High score {index}", "summary": "release", "url": f"https://example.test/{index}", "published": "2026-09-13", "score": 5} for index in range(25))
    payload = MODULE.build_ai_payload(sample, "2026-09-13T00:00:00+00:00")
    watch = payload["providerWatch"]
    assert [row["id"] for row in watch["providers"]] == ["chatgpt", "gemini", "claude"]
    assert all(row["latest"] for row in watch["providers"])
    assert watch["localGuardrail"]["active"]["dailyTotal"] == 6
    assert watch["localGuardrail"]["recommendedPilot"]["dailyTotal"] == 12
    assert watch["monitoringPolicy"]["mode"] == "independent-dual-observation"
    assert len(watch["monitoringPolicy"]["importantChanges"]) >= 6
    print("AI provider watch checks passed: official feeds, three providers, plan baselines, guardrail comparison")


if __name__ == "__main__":
    main()
