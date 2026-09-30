# CONTRACTS｜数据契约与状态机

> 本文件是**契约的唯一所有者（owner）**。

## 1｜总则

- 全部 Schema 采用 **JSON Schema Draft 2020-12**，自包含，**不引用**任何私有路径。
- 面向人的展示名与机器枚举并存；未知字段默认拒绝（`additionalProperties: false`）。
- 每个字段只有**一个规范真源**；其他模块引用版本化 Schema，不复制字段定义。
- 变更契约须提升 `schema_version`，并同步更新 fixtures 与 tests。
- 校验器只报告错误/警告/证据，**不擅自改写**任何值。

## 2｜Schema 清单

| 文件 | 标题 | 职责 | 主要消费者 |
|---|---|---|---|
| `task-card.schema.json` | Task Card V1 | 承载经人工批准的任务与阶段状态 | Topic Planning、Keyword、Writing、Visual |
| `note-type.schema.json` | Note Type V1 | 三类内容枚举及策略接口 | Topic Planning、Writing、Visual |
| `keyword-plan.schema.json` | Keyword Plan V1 | 候选/选定关键词、意图、证据、布局、批准状态 | Keyword、Writing、Validator |
| `finalization.schema.json` | Finalization V1 | 稿件生命周期与批准审计字段 | Writing、Visual、Workflow Gate |
| `visual-output.schema.json` | Visual Output V1 | 页面计划→渲染→QA→Manifest 的交付对象 | Visual、QA、Export |
| `production-manifest.schema.json` | Production Manifest V1 | 本次导出的唯一交付清单 | Visual、Export |
| `account-profile.schema.json` | Account Profile V1 | 用户账号画像（定位/受众/方向/语气） | Topic Planning、Keyword、Writing |
| `topic-planning-result.schema.json` | Topic Planning Result V1 | 单个候选编译后的选题结果 | Topic Planning、Task Card |
| `writing-result.schema.json` | Writing Result V1 | 结构化草稿与关键词使用报告 | Writing、Finalization、Visual |
| `research-request.schema.json` | Research Request V1 | 研究请求 | Research |
| `research-result.schema.json` | Research Result V1 | 证据化研究结果（固定 `proposed`） | Research、Topic Planning |
| `learning-feedback.schema.json` | Learning Feedback V1 | 复盘反馈/修订历史输入 | Learning |
| `learning-review.schema.json` | Learning Review V1 | 改进提案（固定 `proposed`） | Learning |

## 3｜Task Card

**顶层最小必填 17 项**：`schema_version`, `task_id`, `status`, `profile_ref`, `content_goal`,
`audience`, `topic`, `note_type`, `core_problem`, `core_answer`, `title_requirement`,
`keyword_request`, `writing_constraints`, `topics`, `risk`, `evidence`, `approval`。

- `task_id` 是用户工作区内唯一标识，**不内嵌**账号编号/日期路径/旧系统 ID。
- `profile_ref` 指向用户自己的 Profile；不要求任何原项目人物或既有账号。
- `status` 只表达任务卡阶段；正文生命周期由 Finalization 表达。
- `keyword_request` 是请求；`keyword_result` 由 Keyword 生成（可选），不重复维护。
- `offer_ref`/`cta` 可选，可为空；为空时**不得**生成虚构产品声明。
- 只有 `status=approved` 且 `approval.state=approved` 的任务卡才能进入 Keyword/Writing。

## 4｜Note Type（仅三枚举）

| 机器枚举 | 展示名 | 适用场景 | 默认正文字数（中文字符，建议） |
|---|---|---|---|
| `search` | 搜索解答型 | 用户主动搜索明确问题/教程 | 500–1000 |
| `recommendation` | 经验推荐型 | 选择、推荐、避坑、方案比较 | 500–1000 |
| `editorial_trend` | 趋势观点型 | 热点/现象/观察与观点 | 400–900 |

字数是默认建议，非硬限制；用户可按平台/内容覆盖，但校验应提示偏离。枚举不可直接扩展，新增类型需提案、示例与版本更新。

## 5｜Keyword Plan

- 每个词含 phrase、intent、priority/level、source、evidence、status、role（main/secondary）、placement（title/body/topic/tag）、occurrence_rule、approval_state。
- **主词恰为 1 个**；确认后 Writer 只消费，不重选/替换/提升词项。
- 无经确认的词时，Writer 须明确询问或按用户允许的「无关键词模式」继续。
- 来源仅来自模型语义推理时必须标 `source.kind=model_suggestion` 并注明**未验证**；**禁止捏造搜索量/热度/成交数据**。
- 进入 Writing 前须 `status=approved`、`approval.state=approved`，且所有词 `status=locked`、`approval_state=approved`。`plan_id` 与 `task_id` 须分别与 Keyword Plan、Task Card 对齐。

## 6｜Finalization 状态机

```text
draft → review → approved
  ↘ rejected → revision_required → review → approved
approved → revision_required （正文改动使批准失效）
```

- `approved` 即 final；不另设易混淆的 `final` 状态。
- Writing 新稿输出 `draft`；仅人工可转 `approved`/`rejected`，且 `approved` 必填 `approved_by` 与 `finalized_at`。
- 批准记录含 **body SHA-256**；正文任何改动都使批准失效，必须重新审阅并重跑视觉/QA。
- 自动化**不能**代替人工批准。

## 7｜Visual Output 与 Manifest

- 顶层：`visual_plan`, `pages`, `image_tasks`, `assets`, `render_outputs`, `qa_result`, `production_manifest`。
- **硬门控**：只接受 `status=approved` 且 `writing_id`/`revision`/`body_sha256` 与 Finalization 一致的正文；`draft`/`review` 或哈希不符即 STOP。
- V1 固定 **8 页**；页面 ID 唯一；`render_outputs` 路径必须为安全相对路径且 SHA-256 与文件一致。
- `qa_result.status` 与 `production_manifest.qa_status` 必须为 `pass`；Manifest 的 `page_outputs` 必须与 `render_outputs` 完全一致。
- 内嵌 Manifest 与顶层契约版本一致；**不含**本机绝对路径或凭证。

## 8｜Research 与 Learning

- **Research**：输出 `status` 固定 `proposed`；每条 evidence 的 `source_id` 必须存在于 `sources`；`signals/user_problems/candidate_topics/candidate_keywords` 的 `evidence_refs` 必须指向已包含的 evidence。无来源时输出空来源 + 明确限制。
- **Learning**：`status` 固定 `proposed`，`approval_required=true`；`suggested_rules[].scope` 必须与 `category` 一致（core_rule_candidate↔core，account_adapter_candidate↔adapter，one_off_preference↔one_off）；`suggested_adapter_changes` 必须只镜像 adapter 提案。Accept/Reject 仅**记录决议**（`applied=false`，`modified_paths=[]`），不写入规则。

## 9｜校验入口

| 校验器 | 用途 |
|---|---|
| `validators/schema_validation.py` | 依赖无关的 Draft 2020-12 子集校验函数 |
| `validators/task_card_validator.py` | 任务卡结构与批准状态 |
| `validators/keyword_plan_validator.py` | 关键词计划、唯一主词、锁定与批准 |
| `validators/writing_validator.py` | 草稿结构、锁定词使用、上游批准对齐 |
| `validators/finalization_validator.py` | 生命周期与 body 哈希（`--require-approved`） |
| `validators/visual_output_validator.py` | 8 页、路径、哈希、SVG 尺寸、QA/Manifest |
| `validators/research_result_validator.py` | 来源/证据引用与 `proposed` |
| `validators/learning_review_validator.py` | 提案状态、scope/category 一致、记录性决议 |

互操作字段：`topic.topic_id`、Keyword Plan `plan_id`、Writing Result `writing_id`/`revision`/`keyword_plan_ref`、Finalization 与 Visual 的 `writing_id`+`revision`+`body_sha256`、以及 Manifest 与 `render_outputs` 的对应关系。这些链接字段嵌于各自对象内，不增加 Task Card 顶层必填数量。
