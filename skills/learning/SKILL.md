# Learning Skill

## 1. 能力
比较原稿与批准终稿、修订记录和反馈，形成有证据、分范围的规则建议，不自动改写任何规则资产。

## 2. 什么时候调用
用户希望复盘内容修改、反馈或 QA 问题，判断哪些改进可以复用时调用。它不是经营数据分析。

## 3. 输入
- 必填：original Writing Result、匹配的 approved Finalization/终稿。
- 可选：revision history、用户修改理由/反馈、visual QA feedback、Account Profile 引用。
- 示例使用的反馈为 synthetic；真实输入由用户主动提供。

## 4. 输出
符合 `contracts/learning-review.schema.json` 的 Learning Review Result，含 observed_changes、repeated_patterns、evidence、suggested_rules、suggested_adapter_changes、confidence、scope，且 `status=proposed`、`approval_required=true`。

## 5. 它会做什么
比较原稿和终稿的可观察差异；仅将有证据支持的规律列为建议；区分 Core Rule Candidate、Account Adapter Candidate、One-off Preference。

## 6. 它不会做什么
不做经营数据归因；不把一次修改误称为反复规律；不写入 Skill、Contract、Rules、Preset 或 Account Adapter；不因 Accept 自动应用建议。

## 7. 人工确认
Review 先作为 proposal。用户需逐项 Accept/Reject；Accept 只记录 `approved_proposal` 决议，`applied=false`，正式规则仍不变。

## 8. 下一步
将 Review 与证据交给人工评审；后续如需应用，必须另行设计显式 Rule Update Workflow。

## Prompt / Runtime
参见 `prompts/system.md`。执行器：`scripts/run_learning_review.py`；决议记录器：`scripts/record_learning_decision.py`；校验器：`validators/learning_review_validator.py`。
