# Agent Native Protocol

1. 读取被调用 Skill 的 `SKILL.md` 与 `prompts/system.md`。
2. 解析 `input_refs`、配置引用及其内容；缺必填项时先询问，不得猜测私有事实。
3. 按 Skill 指令完成真实推理；确定性 demo 仅用于测试，不能冒充 AI 生产输出。
4. 输出 Skill 指定的结构化对象，验证其 Contract 与跨对象引用。
5. 人工 Gate 必须等待用户明确选择/批准；测试中的 mock approval 只能标记为测试模拟。
6. 在上下文允许时，将产物保存到用户项目的 `workspace/` 或 `outputs/`；不得写回 Skill 源码或共享规则。
7. 失败时返回字段级错误与下一步，不得通过放宽 Schema 绕过。

Provider、模型、Agent 工具均由宿主环境选择。Core Skill 不依赖某个 API、MCP 或远程服务。Research 无来源时只能输出基于用户提供资料/语义推理的结果，不得声称实时平台趋势。Learning 只生成 proposal。
