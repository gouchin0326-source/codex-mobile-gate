# CG開発状況 2026-08-01

CGは2026-08-01版に更新済みです。

- 公開CG: https://gouchin0326-source.github.io/codex-mobile-gate/
- Google Drive版: `G:\マイドライブ\CODEX\latest\index.html`
- 最新成果物: 外部AIブリーフ圧縮器
- メインレーン: CODEX -> 外部AI / Web
- 重いGPU/CPU/NPU処理: HOSHI権限のためCODEXでは使わない

## 外部AIブリーフ圧縮器

スマホから成果物の詳細をセットし、CODEXが実行できる形へ圧縮する管制盤です。

- ジャンルレーン選択
- 詳細情報セット
- 曖昧さスコア
- 超概算トークン量
- GO判定
- セット完了 / GOサイン
- JSON / Markdown / タスクJSON出力

開く場所:

`latest\external-ai-brief-compressor\index.html`

## 次の使い方

圧縮器でタスクを作成し、チャット欄へ貼ってから次のように指示します。

```text
このセット済みタスクをGOで実行して
```
