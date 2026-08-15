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
- Fixed the mobile MOVE pad hit target by preventing the transparent ring base from intercepting canvas touches.
- The balance now starts with pistol only; weapon pickups unlock the next weapon before later pickups upgrade weapons. Early waves spawn fewer zombies and scale up more gradually.
- Actor rendering now uses pseudo-3D bodies for the player, allies, zombies, bosses, and pickups: shaded ellipsoids/capsules, stronger foot shadows, walking bob, limb swing, damage marks, and Y-sorted depth overlap.
- Actor rendering was optimized to remove per-character gradient creation, reducing movement stutter. Bodies now use lighter 3D forms with elongated torsos, facing changes, limb swing, and less spherical silhouettes.
- Mobile MOVE input now behaves like the earlier tilt stick again: touch position is read relative to the fixed center pad, and held touches keep movement active. Player animation now uses movement direction while moving and aim direction only while idle.
- Mobile MOVE input now preserves the full analog vector: diagonal movement is continuous, light tilt walks, deep tilt runs, and the transparent ring base no longer steals the movement drag area.
- The player silhouette now has a clearer tactical upper body, helmet/visor, arms, and longer rifle shape so it reads less like a round body and more like an armed survivor.
- The mobile ring/controller layout is lifted away from the screen edge, while start/pause are parked on the lower-left side so they do not cover the MOVE pad.
- Zombies now show a short close-range attack state with forward-reaching arms, a wider mouth, claw streaks, and a small pounce burst instead of only speeding up.
- The player model has broader shoulders, a darker tactical vest, visor highlight, and clearer rifle line to move away from a stick-figure read.
- The 10-feature gameplay pass adds wave objectives, hunt/survive/scavenge/rescue missions, building cache pickups, rescue survivors, ally proximity support, crawler zombies, boss slam/summon attacks, weapon-level performance mods, weapon-specific player silhouettes, hit stop, screen shake, stronger muzzle feedback, and a night-visibility light cone.
- The mob realism pass adds lightweight LOD rendering: off-screen actors are culled, distant mobs use simpler bodies, and close mobs gain torn clothing, shirt color variation, exposed ribs, jaw damage, packs, crawler posture, and stronger survivor/zombie silhouette differences without adding bitmap asset overhead.
- The animation pass adds player sprint lean, reload pose, dodge tilt, recoil lean, and enemy hit-stagger, lunge, spit, crawler, and boss attack poses through the existing lightweight LOD renderer.
- The actor graphics pass improves readability beyond stick-figure silhouettes: the player now has broader tactical shoulders, segmented armor, helmet/visor, pouches, hands, and clearer weapon hold, while zombies gain hunched posture, asymmetric shoulders, ragged clothing, damaged hands, and closer face/body decay details.
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
