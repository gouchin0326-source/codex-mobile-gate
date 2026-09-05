import importlib.util
import json
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("fetch_free_info.py")
SPEC = importlib.util.spec_from_file_location("fetch_free_info", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def weather_source():
    return [{
        "id": "weather-test",
        "label": "試験天気",
        "genre": "天気",
        "type": "weather",
        "url": "https://api.example.test/forecast?current=x",
    }]


def valid_weather():
    return json.dumps({
        "current": {"time": "2026-09-05T08:00", "temperature_2m": 20, "wind_speed_10m": 2},
        "hourly": {
            "time": ["2026-09-05T08:00"],
            "temperature_2m": [20],
            "relative_humidity_2m": [50],
            "apparent_temperature": [20],
            "precipitation_probability": [0],
            "precipitation": [0],
            "wind_speed_10m": [2],
        },
        "daily": {
            "time": ["2026-09-05"],
            "weather_code": [1],
            "temperature_2m_max": [25],
            "temperature_2m_min": [18],
            "precipitation_sum": [0],
        },
    }).encode()


def run():
    now = "2026-09-05T00:00:00+00:00"
    original_fetch = MODULE.fetch
    original_weather_out = MODULE.WEATHER_OUT
    original_social_out = MODULE.SOCIAL_OUT
    original_health_out = MODULE.HEALTH_OUT
    original_social_sources = MODULE.SOCIAL_SOURCES
    try:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.WEATHER_OUT = root / "weather.json"
            MODULE.SOCIAL_OUT = root / "social.json"
            MODULE.HEALTH_OUT = root / "health.json"

            MODULE.fetch = lambda _url, *_args, **_kwargs: (_ for _ in ()).throw(OSError("offline"))
            empty = MODULE.build_weather_payload(weather_source(), now)
            require(empty["status"] == "unavailable", "all-source failure must be unavailable")
            require(empty["risk"]["level"] == "unknown", "all-source failure must not be normal")
            require(empty["lastSuccessAt"] is None, "failed attempt must not create a success time")

            previous = {
                "lastSuccessAt": "2026-09-04T00:00:00+00:00",
                "locations": [{"source": "weather-test", "current": {}, "hourly": [], "daily": []}],
                "sourceStates": [{"id": "weather-test", "lastSuccessAt": "2026-09-04T00:00:00+00:00"}],
            }
            MODULE.WEATHER_OUT.write_text(json.dumps(previous), encoding="utf-8")
            stale = MODULE.build_weather_payload(weather_source(), now)
            require(stale["status"] == "stale", "previous data must be retained as stale")
            require(stale["locations"][0]["stale"] is True, "fallback row must be marked stale")
            require(stale["lastSuccessAt"] == previous["lastSuccessAt"], "failure must preserve last success")

            def good_fetch(url, *_args, **_kwargs):
                if url == MODULE.JMA_TOYAMA_WARNING:
                    return b'{"areaTypes":[]}'
                if url == MODULE.JMA_NOWCAST_TARGETS:
                    return b"[]"
                return valid_weather()

            MODULE.fetch = good_fetch
            fresh = MODULE.build_weather_payload(weather_source(), now)
            require(fresh["status"] == "fresh", "valid sources must be fresh")
            require(fresh["risk"]["level"] == "normal", "valid empty warning and mild forecast may be normal")
            require(fresh["lastSuccessAt"] == now, "fresh data must update last success")

            MODULE.fetch = lambda url, *args, **kwargs: b"[]" if url == MODULE.JMA_TOYAMA_WARNING else good_fetch(url, *args, **kwargs)
            schema_error = MODULE.build_weather_payload(weather_source(), now)
            require(schema_error["risk"]["level"] == "unknown", "bad warning schema must not become normal")
            require(schema_error["status"] == "stale", "partial schema failure must be stale")

            MODULE.SOCIAL_SOURCES = [{"id": "social-test", "platform": "Mastodon", "type": "mastodon", "url": "https://example.test"}]
            MODULE.SOCIAL_OUT.write_text(json.dumps({
                "lastSuccessAt": "2026-09-04T00:00:00+00:00",
                "items": [{"source": "social-test", "title": "日本語の前回情報", "regionScore": 1}],
                "sourceStates": [{"id": "social-test", "lastSuccessAt": "2026-09-04T00:00:00+00:00"}],
            }, ensure_ascii=False), encoding="utf-8")
            MODULE.fetch = lambda _url, *_args, **_kwargs: (_ for _ in ()).throw(OSError("offline"))
            social = MODULE.build_social_payload(now)
            require(social["status"] == "stale", "social fallback must be stale")
            require(social["items"][0]["stale"] is True, "social fallback item must be marked stale")
            require(social["lastSuccessAt"] == "2026-09-04T00:00:00+00:00", "social failure must preserve last success")

            health = MODULE.build_health_payload(now, {"updatedAt": now, "items": [], "errors": []}, {"updatedAt": now, "items": []}, stale)
            weather_health = next(x for x in health["datasets"] if x["id"] == "weather-info")
            require(health["level"] == "warning", "stale weather must warn in health")
            require(weather_health["status"] == "stale", "health must expose dataset status")
    finally:
        MODULE.fetch = original_fetch
        MODULE.WEATHER_OUT = original_weather_out
        MODULE.SOCIAL_OUT = original_social_out
        MODULE.HEALTH_OUT = original_health_out
        MODULE.SOCIAL_SOURCES = original_social_sources
    print("Z0 checks passed")


if __name__ == "__main__":
    run()
