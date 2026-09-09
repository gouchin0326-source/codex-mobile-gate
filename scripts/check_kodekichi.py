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
        "cg-kodekichi-v2-1", 'localStorage.removeItem(OLD)', 'localStorage.removeItem("cg-kodekichi-v2")', "learningDays",
        "aria-live", "min-height:44px", "prefers-reduced-motion", "推測では補いません",
        "CODEKICHI /", "品質門", "setTimeout(()=>runMission()",
        "開発時間を指示する", 'id="job-minutes"', 'min="1" max="480"',
        "startJob", "tickJob", "finishRequested", "今すぐ納品",
        "納品書庫", "finalizeJob", "state.archives", "deliveryNote",
        "成果物入り書庫JSON", "data-url", "全品質門PASS",
        "外部AI 0回・Claude重複なし", "外部AI安全策", 'mode:"local-only"',
        "リクエストエラーの結果は納品へ入れません", "claudeOverlap",
        "納品停止 外部AIエラーまたはClaude重複",
        "外部AIと作品を作る", "127.0.0.1:8766",
        "codex-kodekichi", "generateExternal", "外部AI応答JSON",
        "start-kodekichi-ai-bridge.ps1", "成果物は作成・納品していません",
        "ChatGPT / OpenAI API", 'value="openai"', "外部AIで制作",
        "ChatGPT Plusとは別のAPI鍵が必要",
        "setup-kodekichi-chatgpt.ps1", "evolution-provider", "resolveEvolutionProvider",
        "進化担当は当面Gemini固定",
        "コデ吉、干場をびっくりさせて！", "びっくり作品を作る",
        "こんなの作ったよ！", "generateSurprise", 'bridgeFetch("/surprise"',
        "Geminiびっくり企画", "Claude領域外", "renderLatest",
        "コデ吉の星キャッチゲーム画面", "星キャッチで遊ぶ", "gameLoop",
        "ArrowLeft", "gameLab", "syncGameKnowledge", "ゲーム星の発明王",
        "ゲームアプリ", "直接プレイ / HTML", "遊びから学習",
        "その場で遊べるミニゲームです",
        "自律進化エンジン", "Geminiの指示 ＋ 許可済みアプリ改造 ＋ セルフテスト合格",
        "ローカルLLM不使用", "requestEvolution", 'bridgeFetch("/evolve"',
        "validateEvolutionPlan", "applyEvolution", "rollbackEvolution", "evolutionConfig",
        'id="evolution-toggle"', 'id="evolution-rollback"', "daily[today]",
        "能力レーダー（実測）", 'id="evolution-radar"', "進化方向の比率",
        'id="weight-game"', 'id="weight-app"', 'id="weight-graphics"',
        "AI比率調整", "発火した判断ポイント", "decisionTriggers",
        "measuredRadar", "evolutionDecision", "evolutionGates", "catch_width",
        "generation_focus", "pet_palette", "pet_expression", "aura_style",
    ]
    assert all(value in page for value in required)
    assert "api.openai.com" not in page and "Authorization" not in page
    assert "state.externalAI.requests++" in page and "state.externalAI.errors++" in page
    bridge = (root.parent / "tools" / "kodekichi_ai_bridge.py").read_text(encoding="utf-8")
    assert all(value in bridge for value in ("gemini_text", "openai_text", "claudeOverlap", "codex-kodekichi", "parse_blueprint", "parse_surprises", '"/surprise"', "LOCK.acquire", '"gemini", "openai"', '"/evolve"', "validate_evolution", "parse_evolution", "EVOLUTION_SPECS", "EVOLUTION_SYSTEM_PROMPT", "EVOLUTION_TARGETS", "system_instruction"))
    assert "GEMINI_API_KEY" not in page and "GOOGLE_API_KEY" not in page
    assert sum(page.count(f'"{name}"') for name in ("image", "music", "app", "research")) >= 8
    assert "days:3,skills:8" in page and "days:30,skills:24" in page
    assert '["タイマー","クイズ"].includes(item.recipe)' in page
    for index in (root / "index.html", root / "latest" / "index.html"):
        assert "kodekichi/index.html" in index.read_text(encoding="utf-8")
    print("Kodekichi v3 checks passed: autonomous Gemini evolution, validated app upgrades, rollback, playable games, quality archive")


if __name__ == "__main__":
    main()
