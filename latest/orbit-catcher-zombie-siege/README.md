# Orbit Catcher: Zombie Siege

`Gate Run` とは別方向のゾンビ制圧版です。ゴール到達よりも、大量のゾンビを銃・投擲武器・仲間でしのぎながら生き残るゲーム性に寄せています。

## Controls

- Move: WASD or arrow keys, or the on-screen stick.
- Sprint: Hold Shift on PC, or push the on-screen stick deeply. Sprinting consumes stamina.
- Shoot: Fully automatic while the round is running. Ammo and reload still matter.
- Aim mode: Press E or tap the aim button to switch auto aim/manual aim.
- Backpedal shooting: Hold S on PC, or hold the backpedal button on touch.
- Grenade: Press G or use the grenade tool.
- Molotov: Press F or use the molotov tool.
- Mine: Press M or use the mine tool.
- Weapon swap: Press Q, or tap a gun card.
- Pause: Press P or the pause button.

## Gameplay

- Buildings and obstacle walls are now placed across the large map. Buildings can be entered, but being inside increases pressure and makes retreat planning important.
- Zombies mostly walk in, with runners and heavy zombies mixed in from later waves.
- Zombies have walking motion, hit stagger, burn/slow status markers, shadows, and more detailed pixel bodies.
- The player shoots automatically, with muzzle flash, recoil, walking motion, shadow, stamina, and backpedal aiming.
- The mobile layout uses a compact HUD: the title header is hidden, the top menu is reduced to one thin status row plus weapon/tool cards, and most of the screen is reserved for the game canvas.
- The 2026-08-11 HUD adds tactical intel: danger level, current area pressure, nearest supply distance, a yellow supply guide arrow, and a mini-map supply route line.
- The high-spec visual pass adds procedural ground detail, muzzle light, shell casings, persistent blood marks, darker lens/vignette grading, and low-health screen damage.
- Zombies now attack harder: timed horde rushes, closer rage spawns, short lunges, swarm speed pressure, and grab damage when they stay on the player.
- On mobile, the main button row now includes a visible weapon cycle button, so weapons can be changed even when the weapon card row is hard to tap.
- The mobile control layer is now compact and transparent: the game canvas fills the screen, a large translucent controller sits at the lower center, and weapon/tool ring commands surround it in real time.
- The mobile canvas now syncs its drawing buffer to the real stage size, preventing vertical stretch and controller distortion after fullscreen layout changes.
- The mobile panel now exposes 操作/マップ/設定 tabs, and settings include camera zoom plus overall game speed so the player can switch between close and pulled-back views.
- The mobile controller is now centered around the MOVE pad: the old lower-right stick is hidden, ammo/HP/stamina are shown as compact circular controller gauges, and map/settings overlays open near the top so they do not cover movement.
- Allies are tougher and more useful, with stronger role weapons, higher durability, faster support fire, stronger traps, and improved melee cleanup.
- Weapons include pistol, shotgun, and machine gun. Each gun has its own ammo count and can be switched with one tap.
- Grenades explode, mines can be placed, and molotovs leave a burning area that damages and slows zombies over time.
- Allies can join randomly. They have visible type colors/icons: POWER, SPEED, GUARD, TRAP, SLOW, and BLADE.
- Ally roles include gunner, trap setter, slow-shot support, and melee cleanup. Allies have unlimited ammo but remain fragile.
- Ammo, throwables, healing, and weapon pickups can drop from zombies.

## Export

- JSON: `orbit-catcher-zombie-siege-result.json`
- Markdown: `orbit-catcher-zombie-siege-result.md`
- AI prompt: `orbit-catcher-zombie-siege-ai-prompt.txt`

Exports include tactical intel for danger and nearest supply routing.

Best score is stored in localStorage under `codex.orbit-catcher.zombie-siege.best.v1`.
