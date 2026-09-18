const port = process.argv[2] || "9332";
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
  socket.send(JSON.stringify({id, method, params}));
});
await call("Runtime.enable");
await call("Runtime.evaluate", {expression: "localStorage.clear(); location.reload()"});
await new Promise(resolve => setTimeout(resolve, 800));
const result = await call("Runtime.evaluate", {
  expression: `(() => {
    document.querySelector("#character-switch").click();
    const before = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1")).externalAI.requests;
    document.querySelector("#song-pattern").value = "sera-memory-piano";
    document.querySelector("#song-pattern").dispatchEvent(new Event("change"));
    const state = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1"));
    return {
      title: document.title,
      character: document.body.dataset.character,
      patterns: [...document.querySelector("#song-pattern").options].map(x => x.value),
      bpm: document.querySelector("#song-bpm").value,
      seconds: document.querySelector("#song-seconds").value,
      providers: [...document.querySelector("#lyrics-provider").options].map(x => x.value),
      variantsDisabled: document.querySelector("#lyrics-variant").disabled,
      aiBefore: before,
      aiAfter: state.externalAI.requests,
      activeSongJob: state.codemi.activeSongJob
    };
  })()`,
  returnByValue: true
});
socket.close();
const actual = result.result.result.value;
if (!actual.title.includes("v8") || actual.character !== "kodemi" || actual.patterns.length !== 7 || actual.bpm !== "68" || actual.seconds !== "180" || !actual.providers.includes("gemini") || !actual.providers.includes("codex") || !actual.variantsDisabled || actual.aiAfter !== actual.aiBefore || actual.activeSongJob !== null) {
  throw new Error(`Kodemi studio smoke failed: ${JSON.stringify(actual)}`);
}
console.log(`Kodemi studio v8 PASS (AI requests 0, music jobs 0): ${JSON.stringify(actual)}`);
