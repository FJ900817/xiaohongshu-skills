# Topic Planning Skill

## 1. 能力
依据用户的账号画像、内容目标和可用证据，提出可比较的选题候选；仅在用户批准后编译任务卡。

## 2. 什么时候调用
用户不知道下一篇写什么、要按目标规划选题，或要把已研究方向整理成候选时调用。

## 3. 输入
- 用户必须提供：Account Profile 引用/内容、当前内容目标、目标用户、内容方向。
- 自动继承：用户显式提供的 Profile、项目配置、共享 Note Type/Task Card Contract。
- 可选配置：产品/服务及经确认的事实、Research Result、近期选题去重列表、风险边界。
- 上游输出：Research Result 可选；无 Research 时只用用户输入，不臆造调研证据。

## 4. 输出
Stage A `topic-candidates.json`（topic_id、标题方向、受众、问题/答案、note_type、content_goal、理由、证据、风险）。用户确认后，Stage B 输出符合 `contracts/task-card.schema.json` 的 Task Card。候选不是正式任务卡。

## 5. 它会做什么
理解账号定位与目标；提出有差异的候选；明确内容类型、问题、答案、证据限制和风险；处理 Approve / Reject / Request Revision；Approve 后编译并运行 Task Card Validator。

## 6. 它不会做什么
不会硬编码账号、人设、旧路径、真实选题库；不会自动批准、入库或排产；不会编造研究、产品事实或经营数据；不写正文、不做关键词策略、不设计图片。

## 7. 人工确认
Stage A 必须由用户选择并明确批准一个候选；Reject 不进入 Stage B；Revision 必须重出候选。只有批准后才生成 `status=approved` 且 `approval.state=approved` 的任务卡。

## 8. 下一步
把已批准 Task Card 交给 Keyword Skill。若校验失败，停止并说明字段错误，不得继续。

## Prompt / Runtime
参见 `prompts/system.md`。确定性演示执行器为 `scripts/run_synthetic_demo.py`；运行时 Task Card 检查器为 `validators/task_card_validator.py`。
