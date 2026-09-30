# 小红书图文 Skills · Xiaohongshu Skills

> 版本 `0.1.0-rc.1`（Release Candidate）· 面向普通创作者的可下载工作台

一套**与模型/供应商无关**的小红书图文生产 Skill 集合。你不需要 API Key，也不需要任何云端服务：由你正在使用的 AI Agent 负责推理，本仓库负责提供上下文、指令、数据契约、校验器和人工确认门（Human Gate）。

> This repo is Agent-Native and provider-agnostic: your Agent performs inference; this repo supplies instructions, contracts, validators and human gates. No bundled model API.

---

## 1｜这是什么

把「做一篇小红书图文」拆成 6 个可独立使用、也可串联成流水线的 Skill。每个 Skill 有明确的输入、输出、人工确认点和可运行的校验器。它解决的问题是：**选题没依据、关键词乱堆、正文像广告、封面靠手搓、做完不复盘**。

---

## 2｜它能解决什么

| 你现在的痛点 | 这套 Skills 的做法 |
|---|---|
| 不知道下一篇写什么 | Topic Planning 基于你的账号定位和目标产出可比较的候选，由你来选 |
| 关键词凭感觉，堆砌严重 | Keyword 匹配搜索意图、给出主/次词和自然布局建议，并明确标注「未验证」 |
| 正文容易夸大数据、编造经历 | Writing 对未证实的事实/产品声明打标待核，草稿绝不自动变成终稿 |
| 封面/内页要手动做 | Visual 用内置几何矢量离线渲染 8 页 SVG，不依赖图片 API |
| 做完没有沉淀 | Learning 对比草稿与终稿，提出可验证的改进建议（仅提案，人工采纳） |

---

## 3｜六个 Skill

| Skill | 一句话职责 | 是否必需 |
|---|---|---|
| **Research** | 搜集并归纳受众需求与证据，产出候选角度（只提案，不定题） | 可选 |
| **Topic Planning** | 依据账号画像与目标生成候选选题，经你批准后编译成任务卡 | 必需 |
| **Keyword** | 匹配搜索意图，给出主/次关键词与标题/正文/话题布局 | 必需 |
| **Writing** | 产出结构化笔记草稿，标注待核实声明，输出始终为 draft | 必需 |
| **Visual** | 把**已人工确认**的正文渲染成 8 页图文页面 + QA + Manifest | 必需 |
| **Learning** | 对比草稿与终稿，提出可追踪的改进建议（旁路，不阻塞生产） | 可选 |

主流程：

```text
Research（可选）
   → Topic Planning → [人工选题确认]
   → Keyword → [人工关键词确认]
   → Writing → [人工终稿确认]
   → Visual → 8 页输出 + QA + Manifest

Learning（旁路）：草稿 / 终稿差异 → 改进提案 → [人工采纳]
```

技能调用用自然语言即可，例如“使用 Topic Planning Skill，根据我的账号配置生成本轮候选”。slash command 是否存在取决于你的宿主 Agent。

---

## 4｜最快怎么开始（约 10–15 分钟）

```powershell
# 1) 初始化你自己的项目（不会覆盖已有目录）
python scripts/init_project.py --destination ./user-project

# 2) 填写你自己的账号配置
#    user-project/config/account-profile.yaml   （你是谁、写给谁、避免什么）
#    user-project/config/project-config.yaml    （本轮目标；无产品就留空）

# 3) 交给你的 Agent：
#    使用 Topic Planning Skill，根据我的账号配置生成本轮选题候选
```

完整步骤见 [`docs/QUICKSTART.md`](docs/QUICKSTART.md)。

---

## 5｜需要什么环境

- 一个能读取本地文件与 Skill 指令的 AI Agent 环境（推荐 Agent Native 模式）。
- **Python 3.10+**：仅用于项目初始化、校验和本地 SVG 渲染。
- 无需联网、无需 API Key、无需登录小红书账号。

自检（可选）：

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## 6｜哪些东西不是必需的

- ❌ 不需要 API Key、不需要任何模型账号
- ❌ 不需要联网、不需要抓取小红书
- ❌ 不需要图片生成服务（Visual 默认离线矢量渲染）
- ❌ 不需要飞书 / 日历 / 任何 MCP（这些是**可选**集成，默认关闭）
- ❌ 不需要你了解任何旧系统编号或历史项目背景

---

## 7｜如何创建你自己的项目

1. 运行第 4 节的第一步完成初始化，得到：

   ```text
   user-project/
   ├── config/      account-profile.yaml / project-config.yaml
   │                keyword-catalog.yaml / visual-config.yaml
   ├── workspace/   过程产物
   ├── outputs/     最终交付（8 页 SVG + Manifest）
   └── learning/    复盘记录
   ```

2. 按 [`docs/CUSTOMIZATION.md`](docs/CUSTOMIZATION.md) 填写配置、词库、视觉与可选集成。
3. `user-project/` 已在 `.gitignore` 中，属于你的本地数据，不会进入版本控制。

---

## 8｜文档索引

| 文档 | 内容（所有者） |
|---|---|
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | 首次运行步骤（QuickStart 唯一所有者） |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | 每个 Skill 的用法、人工门与下一步（使用流程唯一所有者） |
| [`docs/CUSTOMIZATION.md`](docs/CUSTOMIZATION.md) | 账号配置、词库、视觉、可选集成（定制唯一所有者） |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 架构、边界、目录结构（架构唯一所有者） |
| [`docs/CONTRACTS.md`](docs/CONTRACTS.md) | 数据契约与状态机（契约唯一所有者） |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | 常见报错与排查（故障排查唯一所有者） |
| [`docs/PUBLIC_DEPENDENCY_AUDIT.md`](docs/PUBLIC_DEPENDENCY_AUDIT.md) | 依赖与许可处置 |
| [`docs/INDEPENDENT_UAT_REPORT.md`](docs/INDEPENDENT_UAT_REPORT.md) | 独立用户验收报告 |
| [`docs/FRESH_CLONE_TEST.md`](docs/FRESH_CLONE_TEST.md) | 全新环境复现测试 |
| [`docs/RELEASE_READINESS_REPORT.md`](docs/RELEASE_READINESS_REPORT.md) | 发布就绪清单 |

---

## 9｜边界与安全

- 本仓库**不包含**任何真实账号资料、真实经营数据、私有词库、凭证或原项目内部内容。
- 合成样例在文件名与元数据中均标注 `synthetic`，不复制真实业务语料。
- 校验器只报告问题，**不会**擅自改写你的配置或正文。
- Visual 只接受**已人工确认且哈希一致**的正文；任何正文改动都会让旧批准失效。
- Learning 的结论永远只是提案，不会自动写入任何规则文件。

## 10｜许可

MIT，见 [`LICENSE`](LICENSE)；第三方与依赖记录见 [`NOTICE.md`](NOTICE.md)。
