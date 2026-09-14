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
await call("Runtime.evaluate", {expression: `(() => {
  const key="cg-kodekichi-v2-1",state=JSON.parse(localStorage.getItem(key));
  const tests=[{name:"体験検査",pass:true}],now=new Date().toISOString();
  state.artifacts=[
    {id:"experience-image",kind:"image",recipe:"星空",seed:101,title:"体験画像",createdAt:now,status:"passed",tests},
    {id:"experience-music",kind:"music",recipe:"冒険",seed:102,title:"体験音楽",createdAt:now,status:"passed",tests},
    {id:"experience-app",kind:"app",recipe:"クイズ",seed:103,title:"体験ゲーム",createdAt:now,status:"passed",tests},
    {id:"experience-research",kind:"research",recipe:"朝の要点",seed:104,title:"体験調査",text:"# 体験調査\\n\\n情報源: 検査用公開データ\\n全文を画面内で読めます。",createdAt:now,status:"passed",tests}
  ];
  localStorage.setItem(key,JSON.stringify(state));location.reload();
})()`});
await new Promise(resolve => setTimeout(resolve, 900));
const result = await call("Runtime.evaluate", {expression: `(() => {
  const find=label=>[...document.querySelectorAll("#gallery button")].find(button=>button.textContent.includes(label));
  const close=()=>document.querySelector("#experience-close").click(),results={};
  find("大きく見る").click();results.image=document.querySelector("#experience-dialog").open&&document.querySelector("#experience-stage canvas")?.width===900;close();
  find("聴く").click();results.music=document.querySelector("#experience-dialog").open&&document.querySelector("#experience-stage audio[controls]")?.src.startsWith("blob:");close();
  find("遊ぶ").click();results.app=document.querySelector("#experience-dialog").open&&document.querySelector("#experience-stage iframe")?.srcdoc.includes("<button");close();
  find("読む").click();results.research=document.querySelector("#experience-dialog").open&&document.querySelector("#experience-stage .experience-text")?.textContent.includes("全文を画面内で読めます");close();
  results.closed=!document.querySelector("#experience-dialog").open&&!document.querySelector("#experience-stage").children.length;
  results.labels=[...document.querySelectorAll("#gallery .artifact-actions button:first-child")].map(button=>button.textContent);
  return results;
})()`, returnByValue: true});
socket.close();
const actual = result.result.result.value;
if (!actual.image || !actual.music || !actual.app || !actual.research || !actual.closed || actual.labels.length !== 4) {
  throw new Error(`In-app experience failed: ${JSON.stringify(actual)}`);
}
console.log(`Kodekichi in-app experience PASS: ${JSON.stringify(actual)}`);
