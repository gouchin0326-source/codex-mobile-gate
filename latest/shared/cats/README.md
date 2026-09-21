# Hoshi Cats

共通の軽量Canvas猫素材。描画原点は足元中央、方向は右から時計回りに0〜7。

```html
<script src="../shared/cats/cat-assets.js"></script>
<script src="../shared/cats/cat-core.js"></script>
```

```js
HoshiCats.draw(ctx,{x:100,y:100,catId:"moka",direction:0,walking:true,phase:4});
```

見た目だけを共有し、武器・能力・セーブは各ゲーム側で管理する。
