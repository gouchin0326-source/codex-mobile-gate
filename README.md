# CODEX Mobile Gate

Static PWA site for GitHub Pages.

- Built: 2026-07-09 23:07:19
- Source gate: C:\Codex\mobile-gate
- Source latest: C:\Codex\public-mobile
- Policy: no local LLM, no GPU

After GitHub auth:

cd C:\Codex\pages-site
git init
git add .
git commit -m "publish codex mobile gate"
gh repo create codex-mobile-gate --public --source . --remote origin --push
gh api repos/:owner/codex-mobile-gate/pages -X POST -f source.branch=main -f source.path=/