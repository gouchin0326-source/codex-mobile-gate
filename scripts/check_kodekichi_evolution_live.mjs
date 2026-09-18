const port = process.argv[2] || "9333";
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
let actual;
for (let attempt = 0; attempt < 100; attempt++) {
  const result = await call("Runtime.evaluate", {
    expression: `(() => {
      const saved = JSON.parse(localStorage.getItem("cg-kodekichi-v2-1") || "{}");
      return {
        version: saved.evolution?.version || 1,
        applied: saved.evolution?.applied || [],
        failures: saved.evolution?.failures || [],
        weights: saved.evolution?.strategy?.weights || {},
        radarInk: [...document.querySelector("#evolution-radar").getContext("2d").getImageData(0, 0, 320, 270).data].some((v, i) => i % 4 === 3 && v > 0),
        aura: document.querySelector("#game-arena").dataset.aura,
        petClass: document.querySelector("#game-pet").className,
        gates: document.querySelectorAll("#evolution-gates .gate").length
      };
    })()`,
    returnByValue: true
  });
  actual = result.result.result.value;
  if (actual.version > 1 || actual.failures.length) break;
  await new Promise(resolve => setTimeout(resolve, 250));
}
socket.close();
if (actual.version <= 1 || !actual.applied.length || !actual.radarInk || actual.gates !== 6) {
  throw new Error(`Autonomous evolution failed: ${JSON.stringify(actual)}`);
}
const weightTotal = Object.values(actual.weights).reduce((sum, value) => sum + Number(value), 0);
if (Math.abs(weightTotal - 100) > 0.1) throw new Error(`Weight total is ${weightTotal}`);
console.log(`Kodekichi autonomous evolution PASS: ${JSON.stringify(actual)}`);
