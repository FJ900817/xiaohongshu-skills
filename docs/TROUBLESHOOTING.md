# TROUBLESHOOTING｜故障排查

> 本文件是**故障排查的唯一所有者（owner）**。契约细节见 [`CONTRACTS.md`](CONTRACTS.md)。

## 0｜快速定位

所有校验器在失败时都会打印 `FAIL <对象> | <字段> | <原因>` 并返回非零退出码；成功打印 `PASS <对象>`。先看字段路径（`$.xxx`）就知道问题在哪一层。

---

## 1｜环境与运行

### `python` 打不开 / 弹出应用商店 / “无法将 python 识别为 cmdlet”
说明只装了 Windows 的 Store 占位程序，没有真正的解释器。请安装 **Python 3.10+**（勾选 “Add to PATH”），然后确认：

```powershell
python --version   # 期望 Python 3.10 或更高
```

### `ModuleNotFoundError: No module named 'schema_validation'`
校验器与 `schema_validation.py` 在同一目录，依赖「脚本所在目录被加入 `sys.path`」这一标准 CPython 行为。如果你用的是**嵌入式/受限 Python**（例如 Windows embeddable zip 的隔离模式），脚本目录不会自动加入，就会出现此错。解决：使用常规 CPython 发行版；或从仓库根目录运行脚本。正常安装的 Python 不会出现该问题。

### 从哪个目录运行？
从**仓库根目录**运行 `scripts/*` 与 `validators/*`。脚本用 `Path(__file__).resolve().parents[1]` 推导仓库根，不依赖当前工作目录写死路径。

---

## 2｜初始化

### `FAIL: 目标已存在，为避免覆盖已停止：...`
`init_project.py` 不会覆盖已有目录。换一个新目标，或先手动备份/删除。

```powershell
python scripts/init_project.py --destination ./user-project-2
```

### `FAIL: 缺少 Starter Preset：...`
仓库不完整（`presets/starter/` 缺失）。重新获取完整仓库。

---

## 3｜校验器常见 FAIL

### Task Card
- `$.approval | Task Card must be human-approved before Keyword/Writing.`
  → 需要 `status=approved` 且 `approval.state=approved`。除测试外不要用 `--allow-unapproved`。

### Keyword Plan
- `$.keywords | exactly one main keyword is required` → 主词必须恰好 1 个。
- `$.approval | plan and all keyword choices must be human-approved and locked`
  → 计划 `approved`、`approval.state=approved`，且每个词 `status=locked`、`approval_state=approved`。
- `$.task_id | does not match Task Card.task_id` → `--task-card` 传错文件或 ID 不一致。

### Writing
- `$.status | new Writing Result must start as draft` → 新稿必须是 `draft`。
- `$.body | approved keyword ... missing; return a Keyword Revision Request ...`
  → 已锁定词必须原样出现在正文；**不要**删词，改为回到 Keyword 走修订。

### Finalization
- `$.body_sha256 | does not match body bytes; approval invalidated` → 正文被改，重新计算哈希并重新批准。
- `$.status | Visual requires human-approved status=approved` → 用 `--require-approved` 时必须是 `approved`。
- `$.approved_by | approved state requires approver and finalized_at` → `approved` 必填 `approved_by` 与 `finalized_at`。

### Visual Output
- `$.content_ref.status | Visual STOP: finalization must be human-approved` → 只接受 approved。
- `$.content_ref | writing_id/revision mismatch` / `...body_sha256 | finalized body hash mismatch` → 输入不是同一版终稿。
- `$.pages | public Visual V1 requires exactly eight pages` → V1 固定 8 页。
- `$.render_outputs[...].path | unsafe path` / `file missing` / `hash mismatch` → 用相对路径，且文件必须存在、哈希一致。
- `...dimensions | SVG dimensions do not match manifest` / `...text | SVG contains empty/missing text nodes` → 渲染产物与声明不符，重跑渲染。
- `$.qa_result.status | QA must pass` → QA 未通过即阻止导出（fail-closed）。

---

## 4｜Research 本地模式

- `unsupported local source format: .xxx` → 只支持 `.json/.csv/.md/.markdown/.txt`。
- `JSON source must be an array or contain a sources array` → 顶层需为数组或含 `sources`。
- `sources[i] needs source_id and title` → 每条来源必须有 `source_id` 与 `title`。
- 没有来源时结果是空来源 + 限制说明，这是**预期行为**，不是错误。**不得**在无外部数据时声称平台实时趋势。

---

## 5｜渲染与字体

- **中文显示为方块**：SVG 依赖你系统上的字体。安装含中文字形的字体（如 `Noto Sans CJK SC`）或在 `visual-config.yaml` 的 `font_family` 里换成你系统已有的中文字体。
- **不随包字体**：仓库不带字体/图标/图片，避免授权问题。
- `page N title exceeds safe line budget` / `body exceeds safe line budget` → 文案太长；精简该页文案后再渲染。

---

## 6｜编码

- 文件统一使用 UTF-8（部分 JSON 带 BOM）。脚本读取时用 `utf-8-sig`；若你自行读取，请同样使用。
- 生成产物（`ensure_ascii=False`）为 UTF-8。

---

## 7｜版本控制

- `user-project/`、`outputs/`、`.env` 等已在 `.gitignore` 中，**不会**进入版本控制。
- `examples/first-run/outputs/` 是**示例fixture**，通过 `.gitignore` 的否定规则保留在仓库内，勿误删。
- 若你要把自己的项目纳入版本控制，请自行调整忽略规则，并确保**不含**凭证与真实敏感资料。

---

## 8｜确定性演示

- `scripts/run_synthetic_demo.py` 是**回归/演示**执行器，不是 AI 生成服务；若输入未标 `synthetic` 会被拒绝（`E2E refuses non-synthetic fixture inputs`）。
- 演示中的批准是**明确命名的 synthetic mock**，禁止用于真实发布。

---

## 9｜仍然卡住？

1. 重新运行相关校验器，记录完整 `FAIL ...` 行与字段路径。
2. 确认输入对象的 `schema_version` 与契约一致。
3. 检查上游对象是否已 `approved` 且互相 ID/哈希对齐。
4. 若为环境问题（Python 版本、字体、编码），先按第 1、5、6 节处理。
