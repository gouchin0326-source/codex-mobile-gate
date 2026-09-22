# Hoshi Cats

共通の軽量Canvas猫素材。描画原点は足元中央、方向は右から時計回りに0〜7。上下左右に加え、右下・左下は斜め前、右上・左上は斜め後ろの専用姿勢を使う。

```html
<script src="../shared/cats/cat-assets.js"></script>
<script src="../shared/cats/cat-core.js"></script>
```

```js
HoshiCats.draw(ctx,{x:100,y:100,catId:"moka",direction:1,action:"pounce",phase:4,motion:true,detail:false});
```

`motion:false` で微動を停止。`detail:true` で最大8矩形の高精細表示、未指定時はscale 1.35以上だけ自動有効。通常ゲームは低負荷のまま。見た目だけを共有し、武器・能力・セーブは各ゲーム側で管理する。

`HoshiCats.actions`: idle / walk / sit / sleep / groom / pounce / attack / claw / spin / charge / hurt / happy。猫パンチ・連続爪・回転攻撃・突進を共通利用できる。
