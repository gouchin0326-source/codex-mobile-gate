from datetime import datetime, timezone

import fetch_free_info as target


def fake_fetch(_url, _source_id, has_previous=False):
    return b'{"workflow_runs":[{"name":"pages build and deployment","status":"in_progress"},{"name":"free-info","status":"completed","conclusion":"success","created_at":"2026-09-07T00:00:00Z"}]}'


def payload(updated_at):
    return {"updatedAt": updated_at, "lastSuccessAt": updated_at, "status": "fresh", "items": [{}], "errors": []}


def main():
    original_fetch = target.fetch
    original_exists = target.HEALTH_OUT.exists
    target.fetch = fake_fetch
    try:
        fresh = target.build_health_payload(
            "2026-09-07T00:14:59+00:00", payload("2026-09-07T00:00:00+00:00"), payload("2026-09-07T00:00:00+00:00"),
            {"updatedAt": "2026-09-07T00:00:00+00:00", "lastSuccessAt": "2026-09-07T00:00:00+00:00", "status": "fresh", "locations": [{}], "errors": []},
        )
        assert fresh["refresh"]["onTime"] is True
        assert fresh["level"] == "normal"
        assert all(run["name"] == "free-info" for run in fresh["runs"])

        late = target.build_health_payload(
            "2026-09-07T00:15:01+00:00", payload("2026-09-07T00:00:00+00:00"), payload("2026-09-07T00:00:00+00:00"),
            {"updatedAt": "2026-09-07T00:00:00+00:00", "lastSuccessAt": "2026-09-07T00:00:00+00:00", "status": "fresh", "locations": [{}], "errors": []},
        )
        assert late["refresh"]["onTime"] is False
        assert late["level"] == "warning"
        assert late["lines"][0] == "CG: 15\u5206\u4ee5\u4e0a\u66f4\u65b0\u306a\u3057"
    finally:
        target.fetch = original_fetch
    print("CG refresh checks passed: 15-minute freshness and free-info-only run state")


if __name__ == "__main__":
    main()
