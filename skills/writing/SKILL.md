# Writing Skill

## 1. 能力
把已批准任务、关键词计划和用户自己的账号配置，转换为结构化、可审核的笔记草稿。

## 2. 什么时候调用
选题和关键词已确认，用户现在需要完整小红书正文、标题及配套话题时调用。

## 3. 输入
- 用户必须提供：Approved Task Card、Approved Keyword Plan、Account Profile、note_type。
- 自动继承：账号语气/边界、Task Card 约束、已批准关键词及位置意图。
- 可选配置：合成或授权的 Style Reference/Example、Offer 真值及证据、CTA 配置。
- 上游输出：Topic Planning 与 Keyword 的已批准产物。

## 4. 输出
符合 `contracts/writing-result.schema.json` 的 Writing Result：writing_id/draft_id/revision/task_id、标题、正文、话题、关键词使用报告、warnings、`status=draft`。不输出自动 final。

## 5. 它会做什么
按 search / recommendation / editorial_trend 策略组织信息；结合 Account Adapter 语气；自然实现锁定关键词；标示事实和产品声明；输出评论区建议（启用时）。

## 6. 它不会做什么
不重选或改写主次关键词、role、placement intent；不编造经历/数据/产品事实；不把草稿设成 approved；不发布、不生成视觉页面。

## 7. 人工确认
用户审核标题、正文、事实/产品声明及风险。Writing 默认只产出 draft；Finalization Validator 对人工批准、正文哈希、审批人和时间进行验证。任何正文修改都需重新审核。

## 8. 下一步
将 draft 送人工审阅；用户批准后生成 Finalization `approved` 记录，再交 Visual Skill。关键词冲突必须返回 Keyword Revision Request。

## Prompt / Runtime
参见 `prompts/system.md`。运行时检查器：`validators/writing_validator.py`，终稿状态检查器：`validators/finalization_validator.py`。
