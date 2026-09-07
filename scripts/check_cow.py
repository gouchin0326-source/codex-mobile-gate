import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def check_script(path):
    text = path.read_text(encoding="utf-8")
    start = text.find("<script>")
    end = text.rfind("</script>")
    require(start >= 0 and end > start, f"script missing: {path}")
    script = text[start + len("<script>") : end]
    result = subprocess.run(
        ["node", "--check", "-"],
        input=script.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    require(result.returncode == 0, f"JavaScript syntax error in {path}: {result.stderr.decode('utf-8', errors='replace')}")
    return text


def run():
    cow = check_script(ROOT / "latest" / "codex-world" / "index.html")
    gate = check_script(ROOT / "latest" / "index.html")
    check_script(ROOT / "latest" / "app-launcher.html")

    require("CODEXWorld <small>— COW</small>" in cow, "COW name missing")
    require(not re.search(r"\bCW\b", cow), "old CW abbreviation remains")
    require('id="instruction"' in cow and 'id="app-name"' not in cow, "one-instruction easy mode missing")
    require("function inferGenre" in cow and "function inferName" in cow, "autonomous decisions missing")
    require("function completeBuild" in cow and "function improve" in cow, "automatic build/review loop missing")
    require("社長指示の流れ" in cow and "function renderCommandChain" in cow, "command chain visualization missing")
    for command_step in ["1 社長", "2 COW受付", "3 担当セル", "4 制作・検品", "5 社長確認"]:
        require(command_step in cow, f"command step missing: {command_step}")
    require("COMPACT_ORDER" in cow and "compact-order-example" in cow, "compact screen instruction example missing")
    require("2Dフロア × カンバン" in cow and "function renderFloorKanban" in cow, "floor and kanban visualization missing")
    for room in ["president", "reception", "ren", "mio", "sora", "akari", "qa", "delivery"]:
        require(f'id:\"{room}\"' in cow, f"floor room missing: {room}")
    for column in ["受領", "設計", "制作", "検品", "社長確認"]:
        require(f'title:\"{column}\"' in cow, f"kanban column missing: {column}")
    require("openJob(job)" in cow and "card.onclick=()=>openJob(job)" in cow, "job card navigation missing")
    require("COWに完成まで任せる" in cow and "このままCGへ掲載" in cow, "easy action labels missing")
    for term in ["cow-state-v1", "cg-cow-artifacts-v1", "cow-library/v1", "cow-artifact/v1"]:
        require(term in cow, f"missing COW identifier: {term}")
    for signature in ["0x04034b50", "0x02014b50", "0x06054b50"]:
        require(signature in cow, f"ZIP signature missing: {signature}")
    for genre in ["productivity", "game", "learning", "data", "creative", "wellness", "other"]:
        require(genre in cow, f"genre missing: {genre}")
    require("./codex-world/index.html" in gate, "COW free-operation link missing")
    require("COW成果物" in gate and "cg-cow-artifacts-v1" in gate, "CG artifact listing missing")

    for service_worker in [ROOT / "sw.js", ROOT / "latest" / "sw.js"]:
        require("codex-world/index.html" in service_worker.read_text(encoding="utf-8"), f"offline cache missing: {service_worker}")

    capabilities = json.loads((ROOT / "latest" / "data" / "artifact-capabilities.json").read_text(encoding="utf-8"))
    require(any(row.get("id") == "codex-world" for row in capabilities["artifacts"]), "artifact registry missing COW")
    print("COW checks passed: command floor, kanban, easy mode, autonomous flow, review loop, CG listing, ZIP, offline cache")


if __name__ == "__main__":
    run()
