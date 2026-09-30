# CUSTOMIZATION｜定制你自己的账号与项目

> 本文件是**定制配置的唯一所有者（owner）**。字段级数据契约见 [`CONTRACTS.md`](CONTRACTS.md)。

## 1｜生成你的项目

```powershell
python scripts/init_project.py --destination ./user-project
```

生成的目录：

```text
user-project/
├── config/
│   ├── account-profile.yaml
│   ├── project-config.yaml
│   ├── keyword-catalog.yaml
│   └── visual-config.yaml
├── workspace/
├── outputs/
└── learning/
```

`user-project/` 已在 `.gitignore` 中；这是**你的本地数据**，不会进入版本控制。初始化器拒绝覆盖已存在的目录。

## 2｜账号画像 `account-profile.yaml`

| 字段 | 含义 | 提示 |
|---|---|---|
| `profile_id` | 你的账号标识 | 自定义，不要求任何外部 ID |
| `display_name` | 展示名 | 任意 |
| `positioning` | 你是谁、帮谁解决什么 | 必填，直接影响选题 |
| `audience.description` | 目标人群 | 越具体越好 |
| `audience.needs` | 人群需求 | 列表，可空 |
| `content_directions` | 内容方向 | 列表 |
| `voice.traits` | 语气特征 | 例：真诚、具体 |
| `voice.avoid` | 避免的表达 | 例：夸大、说教 |
| `synthetic` | 是否合成示例 | 真实用户填 `false` |
| `claims_boundary` | 声明边界 | 只写你确认过的事实 |

> 只填公开信息，**不要**填登录凭证、真实 UID 或敏感个人资料。

## 3｜项目配置 `project-config.yaml`

| 字段 | 含义 |
|---|---|
| `project_id` | 项目标识 |
| `language` | 语言（默认 `zh-CN`） |
| `content_goal` | 本轮目标 |
| `products_or_services` | 产品/服务；**没有就保持空列表** |
| `research.enabled` | 是否启用 Research（默认 `false`） |
| `research.sources` | 本地资料路径；不联网 |
| `paths.*` | workspace/outputs/learning 相对路径 |

## 4｜关键词库 `keyword-catalog.yaml`

```yaml
catalog_id: my-keywords
keywords: []
# 可选示例（仅结构示意，不代表真实数据）：
# - phrase: 你的关键词
#   intent: 用户意图描述
#   source: user_provided
#   evidence: 你的资料来源
#   metrics: null
```

- 未知字段保持空白；**禁止**把猜测写成真实搜索量或成交数据。
- 空词库允许，此时语义候选会被标记为 `model_suggestion / unverified`。

## 5｜视觉配置 `visual-config.yaml`

| 字段 | 含义 |
|---|---|
| `canvas.width/height` | 画布尺寸（默认 1080×1440） |
| `page_count` | 页数（V1 固定 8） |
| `format` | 输出格式（svg） |
| `font_family` | 字体栈（默认系统字体，无需随包字体） |
| `palette.background/ink/accent/muted` | 调色板 |
| `assets` | 可选自有素材（须确认你拥有使用权） |

- 不随包字体、图标、图片；渲染使用你系统上的字体。
- P5 使用内置几何矢量占位，避免未授权图片。

## 6｜Starter Preset 与示例

- 模板：`presets/starter/*`（`init_project.py` 复制的就是它）。
- 合成示例：
  - `examples/first-run/`——首次运行示例（窗台香草主题，合成）。
  - `examples/synthetic/demo-v1/`、`examples/synthetic/demo-project/`——契约与端到端样例（合成）。

若要替换视觉基线，可复制 `visual-config.yaml` 并改调色板/画布；改 `font_family` 时请确认字体在你的系统存在。

## 7｜自定义来源（Research）

`adapters/research/local_json_source.py` 支持：

- `.json`——数组，或含 `sources` 数组的对象；
- `.csv`——表头含 `source_id,title,summary,...`；多值字段用 `|` 分隔，词-意图对用 `phrase::intent`；
- `.md` / `.txt`——作为 `user_upload` 文本来源。

所有来源只当作**用户提供证据**；没有外部数据时不得声称平台实时趋势。

## 8｜可选集成（默认关闭）

`integrations/feishu`、`integrations/calendar`、`integrations/platform` 目前是**空占位**，未实现、无凭证、默认不调用。启用任何集成须：

1. 明确开启，最小权限；
2. 凭证只放本地环境变量/系统凭证库，**不落仓库、不落日志**；
3. 先 dry-run/预览，再人工确认；
4. 不阻塞本地 Markdown/图片导出。

## 9｜自定义内容类型的边界

当前仅 `search` / `recommendation` / `editorial_trend` 三类。新增类型需：提案 → 示例 → Writing/Visual 策略 → 契约版本更新。**不要在用户配置里自造枚举**，否则校验会失败。

## 10｜运行你自己的校验

```powershell
python validators/task_card_validator.py <task-card.json>
python validators/keyword_plan_validator.py <keyword-plan.json> --task-card <task-card.json>
python validators/writing_validator.py <writing-result.json> --task-card <task-card.json> --keyword-plan <keyword-plan.json>
python validators/finalization_validator.py <finalization.json> --require-approved
python validators/visual_output_validator.py <visual-output.json> --finalization <finalization.json>
```
