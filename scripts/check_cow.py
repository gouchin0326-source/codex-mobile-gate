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
        ["node", "-e", "new (require('vm').Script)(process.argv[1])", script],
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, f"JavaScript syntax error in {path}: {result.stderr}")
    return text


def run():
    cow = check_script(ROOT / "latest" / "codex-world" / "index.html")
    gate = check_script(ROOT / "latest" / "index.html")
    check_script(ROOT / "latest" / "app-launcher.html")

    require("CODEXWorld <small>— COW</small>" in cow, "COW name missing")
    require(not re.search(r"\bCW\b", cow), "old CW abbreviation remains")
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
    print("COW checks passed: naming, JavaScript, CG listing, genres, ZIP, offline cache, registry")


if __name__ == "__main__":
    run()
