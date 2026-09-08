from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    page = (root / "latest" / "kodekichi" / "index.html").read_text(encoding="utf-8")
    required = [
        "コデ吉", "第1形態 めばえ", "自由制作をもう一巡", "成果の棚",
        "星空", "庭園", "都市", "ポスター", "モザイク", "ピクセル",
        "冒険", "子守歌", "祭り", "宇宙", "雨音", "不思議",
        "習慣", "カウンター", "タイマー", "メモ", "カンバン", "クイズ",
        "toBlob", "audio/wav", "text/html", "text/markdown", "localStorage",
        "holidays.json", "free-info.json", "today.json", "weather-info.json",
        "cg-kodekichi-v2", 'localStorage.removeItem(OLD)', "learningDays",
        "aria-live", "min-height:44px", "prefers-reduced-motion", "推測では補いません",
        "CODEKICHI /", "品質門", "setTimeout(()=>runMission()",
    ]
    assert all(value in page for value in required)
    assert "api.openai.com" not in page and "Authorization" not in page
    assert sum(page.count(f'"{name}"') for name in ("image", "music", "app", "research")) >= 8
    assert "days:3,skills:8" in page and "days:30,skills:24" in page
    for index in (root / "index.html", root / "latest" / "index.html"):
        assert "kodekichi/index.html" in index.read_text(encoding="utf-8")
    print("Kodekichi v2 checks passed: reset, 24 recipes, autonomous make-test-shelf, slow daily growth, exports, zero model API")


if __name__ == "__main__":
    main()
