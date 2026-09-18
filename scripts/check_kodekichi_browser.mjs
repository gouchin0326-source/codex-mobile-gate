const port = process.argv[2] || "9331";
const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
const tab = tabs.find(item => item.url?.includes("kodekichi/index.html"));
if (!tab) throw new Error("Kodekichi browser tab not found");

const socket = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(resolve => { socket.onopen = resolve; });
let nextId = 0;
const pending = new Map();
socket.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    pending.get(message.id)(message);
    pending.delete(message.id);
  }
};
const call = (method, params = {}) => new Promise(resolve => {
  const id = ++nextId;
  pending.set(id, resolve);
  socket.send(JSON.stringify({ id, method, params }));
});

await call("Runtime.enable");
await call("Runtime.evaluate", { expression: "localStorage.clear(); location.reload()" });
await new Promise(resolve => setTimeout(resolve, 800));
const result = await call("Runtime.evaluate", {
  expression: `(() => {
    document.querySelectorAll("#garden-sites .garden-site")[0].click();
    document.querySelector("#game-start").click();
    document.querySelector("#game-left").click();
    return {
      label: document.querySelector("#game-start").textContent,
      star: document.querySelector("#game-star").classList.contains("on"),
      petLeft: document.querySelector("#game-pet").style.left,
      time: document.querySelector("#game-time").textContent,
      evolution: document.querySelector("#evolution-version").textContent,
      autoEvolution: document.querySelector("#evolution-toggle").textContent,
      localLlmFree: document.querySelector(".garden-note").textContent.includes("ローカルLLM"),
      radarInk: [...document.querySelector("#evolution-radar").getContext("2d").getImageData(0, 0, 320, 270).data].some((v, i) => i % 4 === 3 && v > 0),
      weightTotal: ["game", "app", "graphics"].reduce((n, key) => n + Number(document.querySelector("#weight-" + key).value), 0),
      gates: document.querySelectorAll("#evolution-gates .gate").length,
      petEvolvedClass: document.querySelector("#game-pet").className.includes("game-palette-")
    };
  })()`,
  returnByValue: true
});
const actual = result.result.result.value;
if (actual.label !== "プレイ中！" || !actual.star || parseFloat(actual.petLeft) > 40 || parseFloat(actual.petLeft) < 12 || actual.evolution !== "EVOLUTION 1" || actual.autoEvolution !== "自動進化 ON" || !actual.localLlmFree || !actual.radarInk || actual.weightTotal !== 100 || actual.gates !== 6 || !actual.petEvolvedClass) {
  throw new Error(`Game smoke test failed: ${JSON.stringify(actual)}`);
}
console.log(`Kodekichi browser game PASS: ${JSON.stringify(actual)}`);

const libraryResult = await call("Runtime.evaluate", {
  expression: `(async () => {
    document.querySelector("#character-switch").click();
    document.querySelector("#character-switch").click();
    document.querySelectorAll("#garden-sites .garden-site")[0].click();
    const before = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1")).externalAI.requests;
    document.querySelector("#game-start").click();
    await new Promise(resolve => setTimeout(resolve, 1200));
    const state = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1"));
    const aiFeed = await fetch("../data/ai-info.json", {cache: "no-store"}).then(response => response.json());
    return {
      character: document.body.dataset.character,
      action: document.querySelector("#game-start").textContent,
      knowledge: state.kodesama.knowledge.length,
      aiRequestsBefore: before,
      aiRequestsAfter: state.externalAI.requests,
      sourceLinks: document.querySelectorAll("#game-knowledge a[href]").length,
      sources: state.kodesama.knowledge.map(item => item.source),
      displayName: document.querySelector("#app-title").textContent,
      aiFeedOfficial: aiFeed.items.filter(item => item.provider || item.genre === "AI").length,
      speech: document.querySelector("#speech").textContent
    };
  })()`,
  awaitPromise: true,
  returnByValue: true
});
const library = libraryResult.result.result.value;
if (library.character !== "kodesama" || library.knowledge < 1 || library.aiRequestsAfter !== library.aiRequestsBefore || library.sourceLinks < 1 || !library.action.includes("無料情報") || !library.speech.includes("読み") || !library.displayName.includes("コデ郎") || !library.sources.some(source => /Gemini|ChatGPT|OpenAI/.test(source))) {
  throw new Error(`Kodesama free-feed smoke test failed: ${JSON.stringify(library)}`);
}
console.log(`Kodesama free-feed PASS: ${JSON.stringify(library)}`);

const musicResult = await call("Runtime.evaluate", {
  expression: `(() => {
    document.querySelector("#character-switch").click();
    document.querySelector("#character-switch").click();
    document.querySelectorAll("#garden-sites .garden-site")[0].click();
    const before = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1")).externalAI.requests;
    document.querySelector("#game-start").click();
    const state = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1"));
    return {
      character: document.body.dataset.character,
      aiRequestsBefore: before,
      aiRequestsAfter: state.externalAI.requests,
      studioVisible: getComputedStyle(document.querySelector("#kodemi-studio")).display !== "none",
      duration: document.querySelector("#song-seconds").value,
      engines: [...document.querySelector("#song-engine").options].map(x => x.value),
      patterns: [...document.querySelector("#song-pattern").options].map(x => x.value),
      lyricProviders: [...document.querySelector("#lyrics-provider").options].map(x => x.value),
      lyricVariantDisabled: document.querySelector("#lyrics-variant").disabled,
      lyricsLength: document.querySelector("#song-lyrics").value.length,
      stateText: document.querySelector("#song-state").textContent,
      action: document.querySelector("#game-start").textContent,
      activeSongJob: state.codemi.activeSongJob
    };
  })()`,
  returnByValue: true
});
const music = musicResult.result.result.value;
if (music.character !== "kodemi" || !music.studioVisible || music.duration !== "180" || !music.engines.includes("ace") || !music.engines.includes("lyria3") || music.patterns.length !== 7 || !music.patterns.includes("sera-memory-piano") || !music.lyricProviders.includes("gemini") || !music.lyricProviders.includes("codex") || !music.lyricVariantDisabled || music.lyricsLength < 40 || music.aiRequestsAfter !== music.aiRequestsBefore || music.activeSongJob !== null || !music.action.includes("歌声付き")) {
  throw new Error(`Kodemi vocal studio smoke test failed: ${JSON.stringify(music)}`);
}
console.log(`Kodemi vocal studio PASS (generation not invoked): ${JSON.stringify(music)}`);

const jobResult = await call("Runtime.evaluate", {
  expression: `(async () => {
    document.querySelector("#character-switch").click();
    document.querySelector("#character-switch").click();
    document.querySelector("#job-minutes").value = "1";
    document.querySelector("#job-theme").value = "停止復旧テスト";
    document.querySelector("#job-start").click();
    await new Promise(resolve => setTimeout(resolve, 800));
    const started = Boolean(JSON.parse(localStorage.getItem("cg-kodekichi-v2-1")).activeJob);
    document.querySelector("#job-finish").click();
    await new Promise(resolve => setTimeout(resolve, 2500));
    const state = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1"));
    return {started, activeJob: state.activeJob, archives: state.archives.length, stateText: document.querySelector("#job-state").textContent};
  })()`,
  awaitPromise: true,
  returnByValue: true
});
socket.close();
const job = jobResult.result.result.value;
if (!job.started || job.activeJob !== null || job.archives < 1 || !job.stateText.includes("待機中")) {
  throw new Error(`Timed game development smoke test failed: ${JSON.stringify(job)}`);
}
console.log(`Timed game development PASS: ${JSON.stringify(job)}`);
