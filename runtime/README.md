# Agent Native Runtime

公共 Skills 的推荐生产模式是 Agent Native：支持 Skills 的 Agent 读取本仓库 Skill 指令、用户配置和结构化输入，在当前会话中执行推理并产出合同规定的对象。此目录不绑定模型厂商，也不发起模型 API 请求。

`scripts/run_synthetic_demo.py` 是确定性测试执行器，不是生产生成器。

每次运行可使用 `execution_context.schema.json` 描述上下文。Agent 必须遵守 Skill 的人工门控和验证步骤；模型或工具不得自行批准选题、关键词、终稿或学习规则。
