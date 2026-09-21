# にゃんパニ！

CODEXGATE向けの単一HTML猫アクションです。自宅から縄張りマップへ出て、危険度・報酬付き事件を選ぶと既存の軽快なシューティング戦闘が始まります。

舞台は猫が暮らす空き地・路地・河川敷・公園です。土管、木箱、柵、タイヤ、ゴミ箱が進路を変える障害物になります。

## Controls

- PC: Move with arrow keys or WASD.
- Shooting is automatic. The player aims at the nearest enemy in range.
- Reloading is automatic when the magazine is empty and reserve ammo remains.
- PC: Hold Shift to boost, and Ctrl for precision movement.
- Touch/PC pointer: Use the stick, boost, and precision buttons below the game area.
- Touch/PC pointer: The two right-side buttons use toolbox items.
- Touch/PC pointer: The pink button activates the ultimate when its gauge reaches 100%.
- Touch: Quickly flick the movement stick for a short speed burst. This does not grant invulnerability.
- Pause/resume: Use the side control button, or press P while playing.

## Gameplay

- Campaign: 猫を操作して`自宅の玄関 → 縄張りマップ → 事件アイコン → 戦闘 → 自宅帰還`を固定1画面で進行します。
- Events: 空き地・路地裏・河川敷の事件は危険度と猫小判報酬が異なります。
- World movement: 自宅と縄張りは戦闘と同じ8方向スティックで歩き、事件はアイコンへの接触だけで開始します。
- Home cat hub: 猫部屋では4匹が軽量な自律行動を行い、猫を直接タップすると操作を交代します。戦闘同行猫は操作猫に応じて自動編成されます。
- Radial difficulty: 自宅から離れた事件ほど危険度・報酬・戦闘マップ規模が上がります。
- Map scale: 危険度1〜5に応じて戦闘マップが段階的に広がります。
- Boss hunt: 規定数の雑魚を倒すと大ボスが出現し、画面外では方向矢印が案内します。
- Armory: 戦闘小判と成功報酬で武器を解放・強化し、合計重量10以内で複数武器を同時装備できます。
- Armory display: 8武器を専用ピクセル絵、効果、Lv、重量、装備中表示、価格付きの2列カードで比較できます。
- Performance: 1回の自動射撃を最大18発に制限し、多武器同時発射時も既存の総弾数上限を守ります。
- Run growth: 戦闘内の攻撃・速度・防御・一時武器LvはRUN限定です。帰宅・敗北時に解除され、MAX取得時は戦闘小判と回復へ変換されます。
- Goal: Defeat the gate boss, then enter the green gate.
- Gate boss: Each gate starts locked by a boss-class enemy guarding the entrance. The gate opens only after the boss is defeated.
- Enemies: Walkers, runners, brutes, spitters, armored zombies, bloaters, summoners, and stalkers.
- Drops: Some enemies drop ammo, repair, or weapon pickups. Stronger or special enemies have better odds for useful drops.
- Rescue: Tough elite guards surround captive cats and use telegraphed charges. Defeat every guard, then touch the cat to recruit it.
- Allies: Rookies use twin shots, medics heal, scouts fire homing shots, and guards use heavy piercing shots.
- Difficulty: Stage 1 teaches the basics; proximity acceleration begins later, and telegraphed enemy charges expand from stage 3 onward.
- Ultimate: Kills slowly charge the gauge. At 100%, `肉球乱舞・猫嵐` clears hostile shots and damages all enemies with a lightweight paw storm.
- Performance limits: 6 allies, 48 ally shots, 120 enemies, 340 total shots, and 160 particles.
- Weapon: Starts as a single-shot gun that fires automatically.
- Powerups: Weapon pickups can temporarily switch to burst, spread, or pierce shots.
- Items: Ammo, repairs, and weapon pickups are used automatically.
- Toolbox: Medkits, bombs, and shields go into the two-slot toolbox and can be used by tapping/clicking their slot.
- Resources: Ammo pickups matter because enemies keep coming, and automatic reload cannot help once reserve ammo is empty.
- Support items: Repair pickups restore durability.
- Visuals: Characters and items use simple pixel-style sprites instead of plain circles.
- Nonstop effects: Capped impact sparks, short camera micro-shake, and ultimate/boss flashes add punch without pausing combat.
- Panic action: Nearby enemies trigger a pulsing danger frame, speed lines, warning callout, sweat, and startled cat face without stopping play.
- Ultimate cut-in: `肉球乱舞・猫嵐` uses a cat portrait, 12 concentration lines, gold trim, paw marks, and full-screen paw storm.
- Cat pixels: The hero now has triangular ears, inner-ear color, large expressive eyes, muzzle, cheeks, whiskers, collar bell, curved tail, short paws, paw pads, blinking, and happy/panic/hurt faces.
- Tabby gestures: One lightweight state-driven gesture is shown at a time—ear twitch, tail sway/run bob, grooming, alert crouch, hit fur-ruffle, ultimate pounce, or homecoming victory jump.
- Tabby reactions: A fixed-priority controller shows only one of hit crying, critical trembling, healing lick, pickup surprise, dodge crouch, combo swagger, reload fatigue, or rescue sparkle at once.
- Cat selection: Tap Moka, Mike, Kuro, or Shiro directly in the cat room to choose the playable cat; each keeps its own role and weapon affinity.
- Cat cast base: The four coats are now stable named characters—モカ、ミケ、クロ、シロ—with a personality and lightweight signature accessory reusable across future cat apps.
- Comic gait: The reusable cat sprite now shows away-facing head markings, toward-facing expressions, alternating paws, body bob/sway, and a two-beat tail response across all eight movement directions.
- Cat room: Home is now a warm indoor room with a window, cat tower, bed, scratching post, bowl, yarn toy, and the mission door; the large hero also uses lightweight away-facing and alternating-paw motion.
- Cat roles and control effects: モカ is balanced, ミケ is agile, クロ is power-focused, and シロ specializes in control/defense. Preferred weapons gain 15% damage; pierce/hairball knock enemies back, homing slows, and laser weakens attacks with capped boss resistance.
- Audio: Browser-generated sound effects and a small looping music pattern can be toggled with the sound button.

## Missions

Each run has one daily-style mission, such as reaching the gate, defeating zombies, preserving ammo, or defeating brutes. Completed missions add a score reward at the end of the run.

## Export

- JSON: Saves the current state and latest finished result as `orbit-catcher-gate-run-result.json`.
- Markdown: Saves a readable result note as `orbit-catcher-gate-run-result.md`.
- AI prompt: Saves `orbit-catcher-gate-run-ai-prompt.txt`, a compact prompt for an external AI to suggest the next small improvements, asset directions, and balance ideas.

## Storage

Best score is saved in browser localStorage under `codex.orbit-catcher.best.v4`.
