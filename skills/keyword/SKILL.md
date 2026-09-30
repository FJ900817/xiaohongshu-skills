# Keyword Skill

## 1. 能力
为已批准任务匹配关键词意图、选择主次词、制定标题/正文/话题布局，并输出经人工批准的 Keyword Plan。

## 2. 什么时候调用
选题与任务卡已确认，用户需要知道用什么搜索词以及怎样自然布局时调用。

## 3. 输入
- 用户必须提供：Approved Task Card、可替换 Keyword Catalog。
- 自动继承：Task Card 的主题、受众、note_type、目标和关键词请求。
- 可选配置：Account Profile、语言/地区、Keyword Rules、用户候选词或授权来源证据。
- 上游输出：Topic Planning 的 Approved Task Card。

## 4. 输出
符合 `contracts/keyword-plan.schema.json` 的 Keyword Plan：候选/已选词、意图、主次角色、来源、证据、位置、出现规则、话题映射和 approval 状态。

## 5. 它会做什么
Lookup 用户目录；按任务意图筛选；提出一个主词和适量辅词；规划标题、正文和话题位置；检查词与主题一致性、重复与堆砌；生成 Validator 可读的报告。

## 6. 它不会做什么
不编造搜索量、排名、成交或热度；不把建议自动锁定；不写正文、不修改 Task Card；不更新用户词库；不让 Writing 偷换已批准词项。

## 7. 人工确认
用户须在候选阶段批准 Keyword Plan；只有 `approval.state=approved` 且词项 `status=locked`、`approval_state=approved` 才能交给 Writing。若需换词，返回 Keyword Revision Request，重新走确认。

## 8. 下一步
将 Approved Keyword Plan 与 Task Card、Account Profile 一并交给 Writing Skill。

## Prompt / Runtime
参见 `prompts/system.md`。演示词库为 `examples/synthetic/keyword_catalog.json`；运行时检查器：`validators/keyword_plan_validator.py`。
