# Orbit Catcher: Gate Run

CODEXGATE向けの単一HTMLゲームです。巨大マップを移動し、無尽蔵に出るゾンビを撃ちながらゲートへ到達します。ゲートを突破するたびに周回が進み、敵の数と強さが上がります。

## Controls

- PC: Move with arrow keys or WASD.
- Shooting is automatic. The player aims at the nearest enemy in range.
- Reloading is automatic when the magazine is empty and reserve ammo remains.
- PC: Hold Shift to boost, and Ctrl for precision movement.
- Touch/PC pointer: Use the stick, boost, and precision buttons below the game area.
- Touch/PC pointer: The two right-side buttons use toolbox items.
- Pause/resume: Use the side control button, or press P while playing.

## Gameplay

- Goal: Defeat the gate boss, then enter the green gate.
- Gate boss: Each gate starts locked by a boss-class enemy guarding the entrance. The gate opens only after the boss is defeated.
- Enemies: Walkers, runners, brutes, spitters, armored zombies, bloaters, summoners, and stalkers.
- Drops: Some enemies drop ammo, repair, or weapon pickups. Stronger or special enemies have better odds for useful drops.
- Allies: Weak survivors can appear randomly on the map. Touch them to recruit them. Rookies, medics, scouts, and guards fight beside you, but they have low durability and can be defeated quickly.
- Weapon: Starts as a single-shot gun that fires automatically.
- Powerups: Weapon pickups can temporarily switch to burst, spread, or pierce shots.
- Items: Ammo, repairs, and weapon pickups are used automatically.
- Toolbox: Medkits, bombs, and shields go into the two-slot toolbox and can be used by tapping/clicking their slot.
- Resources: Ammo pickups matter because enemies keep coming, and automatic reload cannot help once reserve ammo is empty.
- Support items: Repair pickups restore durability.
- Visuals: Characters and items use simple pixel-style sprites instead of plain circles.
- Audio: Browser-generated sound effects and a small looping music pattern can be toggled with the sound button.

## Missions

Each run has one daily-style mission, such as reaching the gate, defeating zombies, preserving ammo, or defeating brutes. Completed missions add a score reward at the end of the run.

## Export

- JSON: Saves the current state and latest finished result as `orbit-catcher-gate-run-result.json`.
- Markdown: Saves a readable result note as `orbit-catcher-gate-run-result.md`.
- AI prompt: Saves `orbit-catcher-gate-run-ai-prompt.txt`, a compact prompt for an external AI to suggest the next small improvements, asset directions, and balance ideas.

## Storage

Best score is saved in browser localStorage under `codex.orbit-catcher.best.v4`.
