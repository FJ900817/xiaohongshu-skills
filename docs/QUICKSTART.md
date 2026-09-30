# 快速开始（约 10–15 分钟）

## 先决条件

需要一个支持读取本地 Skill 指令与文件的 AI Agent 环境。推荐 Agent Native 模式；本仓库不要求 API Key。Python 3.10+ 仅用于项目初始化、校验和本地 SVG 渲染。`run_synthetic_demo.py` 是测试，不是生产内容生成器。

## 1｜初始化

在仓库目录执行：

```powershell
python scripts/init_project.py --destination ./user-project
```

如目标目录已存在，初始化会停止而不会覆盖。默认建议目录 `user-project/` 已加入 `.gitignore`；若自定义目标，请自行确保用户运行数据不会进入版本控制。

## 2｜填写账号配置

编辑 `user-project/config/account-profile.yaml`：身份/定位、目标人群、内容方向、语气和避免事项。不要填写登录凭证、真实 UID 或敏感个人资料。

## 3｜填写项目配置

编辑 `user-project/config/project-config.yaml`，设定当前目标；没有产品或服务就保持空列表。Research 默认关闭。

## 4｜规划选题

向 Agent 说：“请读取我的账号配置，并使用 Topic Planning Skill，根据本轮目标生成至少 3 个不同候选。”检查候选的问题、答案、证据限制和风险。选择一个并明确批准；未批准前不要编译正式任务卡。

## 5｜选择一个 Topic

明确回复要批准的候选编号，或要求修改。只有明确批准后才能生成 Task Card。

## 6｜规划关键词

向 Agent 说：“使用 Keyword Skill，为已批准任务生成关键词计划。”可以把自有资料填入 `keyword-catalog.yaml`。空词库时允许语义候选，但它们必须标记为未验证；不得出现虚构搜索量、热度或成交数据。逐词确认后再批准计划。

## 7｜生成正文

向 Agent 说：“使用 Writing Skill，按账号配置和 note_type 写一版草稿。”检查正文事实、类型结构、关键词使用、话题和风险。Writing 只能输出 draft。

## 8｜确认正文

人工修改并明确确认终稿。正文有任何变化，都必须生成新的修订并重新确认；不得沿用旧正文的批准状态。

## 9｜生成视觉页

将已批准终稿与对应 Finalization 交给 Visual Skill。Skill 会检查批准状态和正文哈希；缺图时使用内置几何矢量占位，不需要图片 API。

## 10｜查看输出

本地 SVG 与 Manifest 应写入用户项目 `outputs/`。逐页检查 P1–P8；需要时再用 Learning Skill 比较原稿与人工终稿，学习建议仍需人工审核。

## 可选：Research / Learning

Research 可跳过；也可提供本地 CSV、JSON 或 Markdown 资料，只能把用户资料当成证据。没有外部数据时不可声称平台实时趋势。Learning 是旁路，不阻塞生产，也不会自动写规则。

### 统一调用说法

`使用 Research Skill…`、`使用 Topic Planning Skill…`、`使用 Keyword Skill…`、`使用 Writing Skill…`、`使用 Visual Skill…`、`使用 Learning Skill…`。具体 slash command 是否可用取决于宿主 Agent；自然语言调用始终可用。
