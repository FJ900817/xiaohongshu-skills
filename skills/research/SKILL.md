# Research Skill

## 1. 能力
基于可追溯资料收集需求信号、用户问题、表达和候选方向，并输出 `status=proposed` 的 Research Result。

## 2. 什么时候调用
用户不知道市场近期在关注什么，希望先收集证据和候选方向时调用。Research 是可选步骤；没有 Research Result 时，Topic Planning 仍可基于用户 Brief 工作。

## 3. 输入
- 必填：research_request、audience/target user、content domain、research goal。
- 可选：seed keywords、Account Profile、数据源选择、用户上传的文本/CSV/JSON。
- 当前可执行来源：用户明确提供的本地 JSON、CSV、Markdown/TXT 文件；Web、平台/MCP 仅作为可替换 Adapter 接口，不会在无授权时连接。

## 4. 输出
符合 `contracts/research-result.schema.json` 的 Research Result：sources、signals、user_problems、candidate_topics、candidate_keywords、evidence、confidence、limitations，状态固定为 `proposed`。

## 5. 它会做什么
汇集所提供的来源；提取问题、需求信号、常用表达；归并重复项；形成带证据引用、置信度与限制说明的候选方向。

## 6. 它不会做什么
不自动批准选题、不创建 Task Card、不修改 Keyword Catalog/Skill/Contract/Rule、不调用 Writing；不把 synthetic fixture 冒充真实市场数据。

## 7. 人工确认
Research Result 可直接存在，但只作为 Topic Planning 的可选证据输入。Topic Planning 的选题批准仍由用户完成。

## 8. 下一步
将 Research Result（如有）与 Account Profile、内容目标交给 Topic Planning；用户也可跳过 Research。

## Prompt / Runtime
参见 `prompts/system.md`。本地来源 Adapter：`adapters/research/local_json_source.py`；执行器：`scripts/run_research.py`；校验器：`validators/research_result_validator.py`。无来源时应明确标注“仅基于用户提供资料/当前输入”，不得声称平台实时趋势。
