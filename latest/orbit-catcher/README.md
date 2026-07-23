# Orbit Catcher

Codex mini game prototype. It runs in the browser as a single HTML file and uses canvas plus localStorage.

## Controls

- PC: Move with arrow keys or WASD. Hold Shift to boost.
- Touch/PC pointer: Use the stick below the game area to move, and the boost button to accelerate.
- Pause/resume: Use the side control button, or press Space while playing.

## Goal

Collect green sparks, avoid red hazards, and grab gold bonuses for shield and extra time. Combos raise the score and can add time. Score also advances named stages, gradually changing spawn timing and hazard speed.

## Export

- JSON: Saves the current state, latest finished result, current stage data, and full stage table as `orbit-catcher-result.json`.
- Markdown: Saves a readable result note and stage table as `orbit-catcher-result.md`.

## Storage

Best score is saved in browser localStorage under `codex.orbit-catcher.best.v2`.
