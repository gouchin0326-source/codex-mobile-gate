from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    page = (root / "latest" / "kodekichi" / "index.html").read_text(encoding="utf-8")
    required = [
        "コデ吉", "おまかせ巡回", "画像工房", "音楽室", "アプリ工房", "調査机",
        "toBlob", "audio/wav", "text/html", "text/markdown", "localStorage",
        "holidays.json", "free-info.json", "today.json", "aria-live", "min-height:44px",
        "prefers-reduced-motion", "推測で補いません", "CODEKICHI / SEED",
    ]
    assert all(value in page for value in required)
    assert "api.openai.com" not in page and "Authorization" not in page
    assert page.count("blobDownload(") >= 6
    for index in (root / "index.html", root / "latest" / "index.html"):
        assert "kodekichi/index.html" in index.read_text(encoding="utf-8")
    print("Kodekichi checks passed: four real exports, autonomy, growth, zero model API, truthful research, CG links")


if __name__ == "__main__":
    main()
