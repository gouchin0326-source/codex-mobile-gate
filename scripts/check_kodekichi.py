from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    page = (root / "latest" / "kodekichi" / "index.html").read_text(encoding="utf-8")
    required = [
        "コデ吉", "第1形態 めばえ", "自律開発の計画を見る", "成果の棚",
        "星空", "庭園", "都市", "ポスター", "モザイク", "ピクセル",
        "冒険", "子守歌", "祭り", "宇宙", "雨音", "不思議",
        "習慣", "カウンター", "タイマー", "メモ", "カンバン", "クイズ",
        "toBlob", "audio/wav", "text/html", "text/markdown", "localStorage",
        "holidays.json", "free-info.json", "today.json", "weather-info.json",
        "cg-kodekichi-v2-1", 'localStorage.removeItem(OLD)', 'localStorage.removeItem("cg-kodekichi-v2")', "learningDays",
        "aria-live", "min-height:44px", "prefers-reduced-motion", "推測では補いません",
        "CODEKICHI /", "品質門", "advanceGardenPlan()",
        "開発時間を指示する", 'id="job-minutes"', 'min="1" max="480"',
        "startJob", "tickJob", "finishRequested", "今すぐ納品",
        "納品書庫", "finalizeJob", "state.archives", "deliveryNote",
        "成果物入り書庫JSON", "data-url", "全品質門PASS",
        "外部AI 0回・Claude重複なし", "外部AI安全策", 'mode:"shared-governed-lane"',
        "リクエストエラーの結果は納品へ入れません", "claudeOverlap",
        "納品停止 外部AIエラーまたはClaude重複",
        "外部AIと作品を作る", "127.0.0.1:8766",
        "codex-kodekichi", "generateExternal", "外部AI応答JSON",
        "start-kodekichi-ai-bridge.ps1", "成果物は作成・納品していません",
        "Codex Plus（追加課金なし）", 'value="codex"', 'value="both"', "外部AIで制作",
        "OpenAI APIは追加課金防止のため無効", "evolution-provider", "resolveEvolutionProvider",
        "共通の日次上限・送信間隔・処理中ロック",
        "コデ吉、干場をびっくりさせて！", "びっくり作品を作る",
        "こんなの作ったよ！", "generateSurprise", 'bridgeFetch("/surprise"',
        "Geminiびっくり企画", "Claude領域外", "renderLatest",
        "コデ吉の庭。指で上下左右へ動かせます", 'special:"star"', "gameLoop",
        "ArrowLeft", "gameLab", "syncGameKnowledge", "ゲーム星の発明王",
        "ゲームアプリ", "直接プレイ / HTML", "遊びから学習",
        "その場で遊べるミニゲームです",
        "自律進化エンジン", "外部AIの指示 ＋ 許可済みアプリ改造 ＋ セルフテスト合格",
        "ローカルLLM不使用", "requestEvolution", 'bridgeFetch("/evolve"',
        "validateEvolutionPlan", "applyEvolution", "rollbackEvolution", "evolutionConfig",
        'id="evolution-toggle"', 'id="evolution-rollback"', "daily[today]",
        "能力レーダー（実測）", 'id="evolution-radar"', "進化方向の比率",
        'id="weight-game"', 'id="weight-app"', 'id="weight-graphics"',
        "AI比率調整", "発火した判断ポイント", "decisionTriggers",
        "measuredRadar", "evolutionDecision", "evolutionGates", "catch_width",
        "generation_focus", "pet_palette", "pet_expression", "aura_style",
        "mobile-dock", 'data-mobile-view="settings"', 'data-mobile-view="results"',
        "gameObjectsTouch", 'addEventListener("pointermove"',
        "庭アプリ開発計画", 'value="08:00"', 'value="22:00"',
        "計画書 → 試作 → テスト → 庭へ配置", "gardenPlanMarkdown",
        "GARDEN_APPS", "moveGardenTo", "activateGardenSite", "gardenCore",
        "完成数上限: なし（ただし1時間に1工程）", "外部API必須",
        'id="plan-auto"', "ensureAutonomousPlan", "コデ吉の自律工程",
        'bridgeFetch("/generate"', "外部API設計なし", 'lane:"codex-kodekichi-garden"',
        "コデ吉・コデ美・コデ郎 v9.20260919", 'id="app-version"', 'id="app-updated"',
        'datetime="2026-09-19T00:00:00+09:00"', "三部屋自律版",
        'id="experience-dialog"', 'id="experience-stage"', "openExperience", "closeExperience",
        "🔎 大きく見る", "▶ 聴く", "🎮 遊ぶ", "📖 読む", 'audio.controls=true',
        'frame.sandbox="allow-scripts"', "experienceObjectUrl", "URL.revokeObjectURL",
        'id="character-switch"', "🎵 コデ美へ", "🎮 コデ吉へ",
        'data-mode="room"', "ROOM_STATIONS", "renderRoom", "switchCharacter",
        "createLocalMusicWav", 'type:"audio/wav"', "歌声付き楽曲を作る", "room-audio",
        'data-mode="library"', "LIBRARY_SHELVES", "renderLibrary", "createKodesamaKnowledge",
        "KODESAMA_FEEDS", "../data/social-trends.json", "../data/ai-info.json", "公開RSS/APIを読めます",
        "無料情報を読む", "外部AIへ送信しません", 'collection:"public-rss-api"', "aiUsed:false",
        "renderKodesamaSources", 'target="_blank"', "コデ郎の図書館", "AI 0回",
        "createKodesamaKnowledge(true)", "自動更新中", "Date.parse(state.kodesama.feedUpdatedAt)>600000", "kodesamaBusy",
        "budget:plan?used<=8:used<8", "本日の自動進化は8回まで",
        "コデ美の歌声つき楽曲スタジオ", 'id="song-create"', 'id="song-test"',
        'bridgeFetch("/kodemi/song"', "pollKodemiSong", "explicitUserAction:true",
        "ACEローカル（GPU・外部送信0回）", "Gemini Lyria 3（無料画面・安全枠）",
        "この確認は生成回数に含みません", "約3分", "saveCodemiAudio",
        "世良祈の制作パターン", "sera-moon-strings", "sera-frost-pop", "sera-indoor-waltz",
        "sera-night-electronica", "sera-meteor-future", "sera-dawn-strings", "sera-memory-piano",
        'id="lyrics-provider"', 'id="lyrics-variation"', 'id="lyrics-variant"',
        "AIで異なる歌詞を3案", 'bridgeFetch("/kodemi/lyrics"', "applyLyricVariant",
        "楽曲生成はまだ0回", "SERA_PATTERN_CONFIG",
        "三人の予定と実績", 'id="agent-board"', 'id="dispatch-summary"',
        "コデ朗の節約確認", "kodekichi-dispatch.json", "dispatchMarkdown",
        "個別送信を避けた回数", "10分ごとに空きを確認",
        "干場の方向指示", 'id="direction-task"', 'id="direction-acceptance"',
        'id="direction-budget"', "saveDirection", 'bridgeFetch("/dispatch/direction"',
        "明日の配車案", 'id="tomorrow-approve"', 'id="tomorrow-hold"',
        "tomorrowPlanMarkdown", "renderTomorrowPlan", 'bridgeFetch("/dispatch/tomorrow-plan"',
        "三人の成果価値", 'id="value-board"', "renderValueMetrics", "rework_events",
        'id="ha-lane-state"', "renderHaLane", "Claude側スナップショット待ち",
    ]
    assert all(value in page for value in required)
    assert "api.openai.com" not in page and "Authorization" not in page
    assert "state.externalAI.requests++" in page and "state.externalAI.errors++" in page
    assert "dailyCompletions" not in page
    assert 'q("#mission").onclick=()=>runMission()' not in page
    assert 'q("#custom").onclick=()=>runMission' not in page
    assert 'q("#job-start").onclick=startJob' in page
    assert 'q("#job-finish").onclick=requestFinish' in page
    assert 'q("#job-start").onclick=()=>{}' not in page
    assert 'q("#job-finish").onclick=()=>{}' not in page
    assert "next.activeJob=null" not in page
    assert "next.activeJob=next.activeJob&&next.activeJob.id?next.activeJob:null" in page
    assert 'setInterval(()=>{tickJob();advanceGardenPlan();maybeAutoEvolve()}' in page
    bridge = (root.parent / "tools" / "kodekichi_ai_bridge.py").read_text(encoding="utf-8")
    lane = (root.parent / "tools" / "external_ai_lane.py").read_text(encoding="utf-8")
    assert all(value in bridge for value in ("gemini_text", "codex_text", "request_session", "claudeOverlap", "codex-kodekichi", "codex-kodemi", "codex-kodesama", "parse_blueprint", "parse_surprises", '"/surprise"', '"/music"', '"/research"', "gemini_grounded_text", "lyria_music", "lyria-3-clip-preview", "ALLOW_PAID_LYRIA", "paidLyriaEnabled", "LOCK.acquire", '"gemini", "codex", "both", "openai"', '"/evolve"', "validate_evolution", "parse_evolution", "EVOLUTION_SPECS", "EVOLUTION_SYSTEM_PROMPT", "EVOLUTION_TARGETS", "system_instruction", '"/kodemi/song"', '"/kodemi/lyrics"', "SONG_WORKER", "SERA_PATTERNS", "parse_lyric_variants", "testMode", '"counted": False', "songEngines", '"musicGenerated": False', "DIRECTION_PATH", "validate_direction", '"/dispatch/direction"', "read_tomorrow_plan", "save_tomorrow_approval", '"/dispatch/tomorrow-plan"', "REGISTER_AUTONOMY"))
    autonomy = (root.parent / "tools" / "kodekichi_autonomous_day.py").read_text(encoding="utf-8")
    assert all(value in autonomy for value in ("approved_directions", "direction_caps", "干場の承認済み指示", '"directions": approved_directions()', "ensure_tomorrow_plan_draft", '"tomorrow_plan": tomorrow_plan', "build_value_metrics", '"value_metrics": value_metrics', "read_ha_lane_snapshot", '"ha_lane_snapshot": ha_lane_snapshot'))
    worker = (root.parent / "tools" / "kodemi_song_worker.py").read_text(encoding="utf-8")
    assert all(value in worker for value in ("music_lane.py", "generate-lyria-via-cdp.py", "song_ace.mp3", "song_lyria3", "explicitUserAction", "additionalCostJpy", "status.json"))
    assert "GEMINI_API_KEY" not in page and "GOOGLE_API_KEY" not in page
    assert 'encoding="utf-8", errors="replace"' in lane
    policy = (root.parent / "data" / "external_ai_policy.json").read_text(encoding="utf-8")
    assert all(value in policy for value in ('"dailyTotal": 6', '"dailyLimit": 4', '"dailyLimit": 2', '"globalMinIntervalSeconds": 120', '"model": "gpt-5.6-luna"', '"kodemi"'))
    assert 'message[-217:]' in bridge
    kodesama_function = page.split("async function createKodesamaKnowledge", 1)[1].split("activateGardenSite=function", 1)[0]
    assert 'bridgeFetch("/research"' not in kodesama_function
    assert "state.externalAI.requests++" not in kodesama_function
    assert sum(page.count(f'"{name}"') for name in ("image", "music", "app", "research")) >= 8
    assert "days:3,skills:8" in page and "days:30,skills:24" in page
    assert '["タイマー","クイズ"].includes(item.recipe)' in page
    for index in (root / "index.html", root / "latest" / "index.html"):
        assert "kodekichi/index.html" in index.read_text(encoding="utf-8")
    print("Kodekichi v9 checks passed: three autonomous rooms, Sera patterns, shared lanes")


if __name__ == "__main__":
    main()
