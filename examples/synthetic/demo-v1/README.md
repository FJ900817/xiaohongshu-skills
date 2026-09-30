# 合成演示｜demo-v1

此目录中的账号画像、选题、关键词、正文、确认状态和 SVG 页面资产均为虚构合成数据，不反映任何真实账号、产品或经营结果。

顺序：`account-profile.json` → `task-card.json` → `keyword-plan.json` → `writing-draft.md` → `finalization-approved.json`（人工确认 mock）→ `visual-output.json` / `visual-asset.svg`。

这些是静态 end-to-end fixtures，可用于结构/状态/哈希/Manifest 校验；不是已实现的六个可执行 Skills 或真实图像 Renderer。Research 与 Integrations 未启用。无任何真实凭证或外部服务依赖。
> **Synthetic asset licensing note:** `visual-asset.svg` is original simple geometric/text artwork authored as a synthetic fixture. No external fonts, images, icons, or remote assets are bundled. Check the repository-level license before redistributing.

Offline smoke check (Python 3 standard library only):

```powershell
python scripts/validate_synthetic_demo.py
```

This checks fixture structure, approval/hash gating, synthetic asset declarations, relative output paths, asset hash, and manifest consistency. It does not execute Skill logic or render new images.

合成关键词目录：synthetic-keyword-catalog.json。
