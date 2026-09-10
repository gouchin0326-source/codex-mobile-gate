const port = process.argv[2] || "9335";
const output = process.argv[3] || "C:/Codex/reports/kodekichi-mobile-0910-final.png";
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

await call("Page.enable");
await call("Runtime.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 390,
  height: 844,
  deviceScaleFactor: 1,
  mobile: true
});
await call("Page.reload", { ignoreCache: true });
await new Promise(resolve => setTimeout(resolve, 900));
const result = await call("Runtime.evaluate", {
  expression: `(() => {
    const pet = document.querySelector("#game-pet").getBoundingClientRect();
    const nav = document.querySelector(".mobile-dock").getBoundingClientRect();
    document.querySelector('[data-mobile-view="settings"]').click();
    const settingsVisible = getComputedStyle(document.querySelector('.evolution-panel')).display !== "none";
    document.querySelector('[data-mobile-view="results"]').click();
    const resultsVisible = getComputedStyle(document.querySelector('#gallery')).display !== "none";
    document.querySelector('[data-mobile-view="home"]').click();
    const homeVisible = getComputedStyle(document.querySelector('.hero')).display !== "none";
    document.querySelectorAll('.garden-site')[1].click();
    const gardenState = JSON.parse(localStorage.getItem('cg-kodekichi-v2-1')).garden;
    const discoveryPlanned = gardenState.discovered.includes('flower-maze') && gardenState.plans.some(plan => plan.siteId === 'flower-maze' && plan.stage === 0);
    document.querySelectorAll('.garden-site')[0].click();
    document.querySelector('#game-start').click();
    const switchedToGame = document.querySelector('#game-arena').dataset.mode === 'minigame' && document.querySelector('#game-star').classList.contains('on');
    return {
      innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      navItems: document.querySelectorAll(".mobile-dock button").length,
      navVisible: getComputedStyle(document.querySelector(".mobile-dock")).display !== "none",
      petWidth: pet.width,
      navRight: nav.right,
      hasTouchDrag: document.documentElement.innerHTML.includes("pointermove"),
      settingsVisible,
      resultsVisible,
      homeVisible,
      discoveryPlanned,
      switchedToGame,
      schedule: gardenState.schedule.start + '-' + gardenState.schedule.end
    };
  })()`,
  returnByValue: true
});
await call("Page.reload", { ignoreCache: true });
await new Promise(resolve => setTimeout(resolve, 500));
const screenshot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
await import("node:fs").then(fs => fs.writeFileSync(output, Buffer.from(screenshot.result.data, "base64")));
socket.close();
const actual = result.result.result.value;
if (actual.innerWidth !== 390 || actual.scrollWidth > 390 || actual.navItems !== 3 || !actual.navVisible || actual.petWidth >= 100 || Math.round(actual.navRight) !== 390 || !actual.hasTouchDrag || !actual.settingsVisible || !actual.resultsVisible || !actual.homeVisible || !actual.discoveryPlanned || !actual.switchedToGame || actual.schedule !== "08:00-22:00") {
  throw new Error(`Mobile UI check failed: ${JSON.stringify(actual)}`);
}
console.log(`Kodekichi mobile UI PASS: ${JSON.stringify(actual)}`);
