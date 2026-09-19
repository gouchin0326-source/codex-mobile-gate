import { writeFile } from "node:fs/promises";

const port = process.argv[2] || "9337";
const output = process.argv[3] || "C:/Codex/reports/gate-mobile-cdp.png";
const viewportHeight = Number(process.argv[4] || 844);
const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
const tab = tabs.find(item => item.url?.includes("orbit-catcher"));
if (!tab) throw new Error("Gate tab not found");
const socket = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(resolve => { socket.onopen = resolve; });
let id = 0;
const pending = new Map();
socket.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    pending.get(message.id)(message);
    pending.delete(message.id);
  }
};
const call = (method, params = {}) => new Promise(resolve => {
  const requestId = ++id;
  pending.set(requestId, resolve);
  socket.send(JSON.stringify({ id:requestId, method, params }));
});
await call("Page.enable");
await call("Runtime.enable");
await call("Emulation.setDeviceMetricsOverride", { width:390, height:viewportHeight, deviceScaleFactor:1, mobile:true });
await call("Page.reload", { ignoreCache:true });
await new Promise(resolve => setTimeout(resolve, 700));
const result = await call("Runtime.evaluate", { expression:`(() => {
  const rect = selector => { const r=document.querySelector(selector).getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,b:r.bottom,r:r.right}; };
  const visible = selector => getComputedStyle(document.querySelector(selector)).display !== "none";
  const c=document.querySelector('#game'); return {inner:[innerWidth,innerHeight],scroll:[document.documentElement.scrollWidth,document.documentElement.scrollHeight],stage:rect('.stage'),canvas:[c.width,c.height],controls:rect('.controls'),start:rect('#mobile-start'),settings:rect('#mobile-settings'),dash:rect('#dash'),items:[rect('#use-slot-0'),rect('#use-slot-1')],headerHidden:!visible('header'),settingsHidden:!visible('aside')};
})()`, returnByValue:true });
const value = result.result.result.value;
await call("Runtime.evaluate", { expression:"document.querySelector('#mobile-start').click()" });
await new Promise(resolve => setTimeout(resolve, 250));
const startedResult = await call("Runtime.evaluate", { expression:"({label:document.querySelector('#start').textContent,state:document.querySelector('#state').textContent})", returnByValue:true });
const started = startedResult.result.result.value;
const dashResult = await call("Runtime.evaluate", { expression:"document.querySelector('#dash').click();document.querySelector('#dash-state').textContent", returnByValue:true });
const dashState = dashResult.result.result.value;
const comboResult = await call("Runtime.evaluate", { expression:"handleEnemyDefeat({type:'walker',score:18,x:200,y:200});handleEnemyDefeat({type:'walker',score:18,x:220,y:200});({combo,score})", returnByValue:true });
const comboCheck = comboResult.result.result.value;
const mapResult = await call("Runtime.evaluate", { expression:"const a={stage:wave,seed:terrain.seed,theme:terrain.theme.name,obstacles:terrain.obstacles.length,hazards:terrain.hazards.length};clearGate();({a,b:{stage:wave,seed:terrain.seed,theme:terrain.theme.name,obstacles:terrain.obstacles.length,hazards:terrain.hazards.length}})", returnByValue:true });
const mapCheck = mapResult.result.result.value;
const growthResult = await call("Runtime.evaluate", { expression:"collectItem({type:'speedUp'});collectItem({type:'defenseUp'});collectItem({type:'attackUp'});weaponSlots=[{type:'single',level:1},{type:'homing',level:1},{type:'orbit',level:1}];collectItem({type:'weapon'});({upgrades:{...upgrades},slots:weaponSlots.length,types:weaponSlots.map(w=>w.type)})", returnByValue:true });
const growth = growthResult.result.result.value;
const motionResult = await call("Runtime.evaluate", { expression:"(() => {const dirs=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]],seen=[];dirs.forEach(([x,y])=>{stickState.x=x;stickState.y=y;movePlayer(.016);seen.push(player.facing)});stickState.x=0;stickState.y=0;movePlayer(.016);return {zoom:viewZoom(),directions:[...new Set(seen)].length,stopped:!player.walking,phase:player.walkPhase}})()", returnByValue:true });
const motion = motionResult.result.result.value;
const settingsResult = await call("Runtime.evaluate", { expression:"document.querySelector('#mobile-settings').click();const radar=document.querySelector('#ability-radar').getBoundingClientRect();({open:document.body.classList.contains('settings-open'),exportVisible:getComputedStyle(document.querySelector('#export-result')).display!=='none',radarVisible:radar.width>0&&radar.height>0,loadout:document.querySelectorAll('#weapon-loadout .equip').length})", returnByValue:true });
const settingsScreen = settingsResult.result.result.value;
await call("Runtime.evaluate", { expression:"document.querySelector('#settings-close').click()" });
const shot = await call("Page.captureScreenshot", { format:"png" });
await writeFile(output, Buffer.from(shot.result.data, "base64"));
socket.close();
const controlClearance=value.inner[1]-value.controls.b;
const fit = value.scroll[0] <= value.inner[0] && value.scroll[1] <= value.inner[1] && controlClearance >= 20 && value.items.every(item => item.r <= value.inner[0]);
const ratioMatch = Math.abs(value.canvas[0]/value.canvas[1]-value.stage.w/value.stage.h) < .01;
console.log(JSON.stringify({ fit, controlClearance, ratioMatch, ...value, started, dashState, comboCheck, mapCheck, growth, motion, settingsScreen, screenshot:output }));
if (!fit || !ratioMatch || dashState === "OK" || comboCheck.combo !== 2 || mapCheck.a.seed===mapCheck.b.seed || mapCheck.b.stage!==2 || mapCheck.a.obstacles<10 || mapCheck.b.hazards<3 || growth.upgrades.attack!==2 || growth.upgrades.speed!==2 || growth.upgrades.defense!==2 || growth.slots!==3 || motion.zoom>=.8 || motion.directions!==8 || !motion.stopped || motion.phase<=0 || !value.headerHidden || !value.settingsHidden || !settingsScreen.open || !settingsScreen.exportVisible || !settingsScreen.radarVisible || settingsScreen.loadout!==3 || started.label !== "やり直す") process.exitCode = 1;
