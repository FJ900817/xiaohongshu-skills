---
name: xiaohongshu-skills
description: >
  Xiaohongshu image-text production suite — control entry / router. Routes a user request to one of
  six Skills: Research, Topic Planning, Keyword, Writing, Visual, Learning. Defines the default
  production flow and the human approval gates. Use this file first, then load the target Skill.
---

# 小红书 Skills · 总控入口（Router）

> 本文件是整套系统的**唯一总控入口**。它本身不生产内容，只负责：
> 1. 判断用户当前处在哪个阶段；
> 2. 把任务**路由**到对应的 `skills/<skill-name>/SKILL.md`；
> 3. 提醒每一步的**人工确认门（Human Gate）**与下一步。

本套件为 **Agent Native**：由你正在使用的 AI Agent 完成推理，本目录只提供指令、上下文、数据契约、校验器与人工门。默认离线，不需要任何 API Key。

---

## 1｜本套件包含的六个 Skill

| Skill | 入口文件 | 一句话职责 | 何时调用 |
|---|---|---|---|
| **Research** | `skills/research/SKILL.md` | 搜集并归纳受众需求与证据，产出候选角度 | 用户不确定方向是否有需求 / 想先看证据时（**可选**） |
| **Topic Planning** | `skills/topic-planning/SKILL.md` | 依据账号画像与目标生成候选选题，批准后编译任务卡 | 用户问「下一篇写什么」时 |
| **Keyword** | `skills/keyword/SKILL.md` | 匹配搜索意图，给出主/次关键词与布局 | 题目已定，需要确定覆盖哪些搜索词时 |
| **Writing** | `skills/writing/SKILL.md` | 产出结构化笔记草稿（始终为 `draft`） | 题目与关键词都已确认，要出正文时 |
| **Visual** | `skills/visual/SKILL.md` | 把**已人工确认**的正文渲染成 8 页图文 + QA + Manifest | 正文终稿批准后，要出页面时 |
| **Learning** | `skills/learning/SKILL.md` | 对比草稿与终稿，提出可验证的改进建议 | 用户想从改动中沉淀经验时（**旁路，可选**） |

---

## 2｜默认完整流程

```text
Research（可选）
   → Topic Planning
   → Keyword
   → Writing
   → Visual
   → Learning（可选）
```

每个阶段之间都有**人工确认门**；未通过确认，不得进入下一阶段：

```text
Topic Planning ──[人工选题确认]──▶ Keyword
Keyword        ──[人工关键词确认]──▶ Writing
Writing        ──[人工终稿确认]──▶ Visual   （Visual 硬性只接受 approved + 哈希一致）
Visual         ──[人工视觉验收]──▶ 交付
Learning       ──[人工采纳]──────▶ 仅记录决议，不自动改规则
```

---

## 3｜路由规则（如何选择 Skill）

按用户意图选择目标 Skill，并**只**加载该 `SKILL.md`：

| 用户意图 | 路由到 |
|---|---|
| 「这个方向有没有需求 / 帮我看看证据 / 调研一下」 | `skills/research/SKILL.md` |
| 「下一篇写什么 / 帮我规划选题 / 出几个候选」 | `skills/topic-planning/SKILL.md` |
| 「用什么关键词 / 标题正文怎么布局 / 埋词」 | `skills/keyword/SKILL.md` |
| 「写正文 / 出一版草稿 / 继续写这篇」 | `skills/writing/SKILL.md` |
| 「出图 / 生成页面 / 做图文 / 封面内页」 | `skills/visual/SKILL.md` |
| 「复盘 / 提炼规律 / 学习我的修改」 | `skills/learning/SKILL.md` |

**路由判定顺序**：

1. 若用户给了明确的单阶段指令（如「出关键词」），直接路由到该 Skill。
2. 若用户给了完整目标（如「做一篇关于 X 的图文」），按第 2 节默认流程从 Topic Planning 开始（Research 可选）。
3. 如果缺少关键输入（账号配置、已批准任务卡、已确认终稿），先向用户索取，**不要臆造**。
4. 不跨阶段越权：例如未获得人工批准的正文，不得送入 Visual。

---

## 4｜人工确认门（不可绕过）

- **选题门**：候选未获用户明确批准，不得编译正式任务卡。
- **关键词门**：计划与词项未 `approved` 且 `locked`，不得进入 Writing。
- **终稿门**：正文必须由人确认并记录 `body_sha256`；正文任何改动都会使批准失效。
- **视觉门**：Visual 只接受 `approved` 且哈希一致的正文；QA 未通过即阻止导出。
- **学习门**：Learning 只提出提案，Accept 仅**记录**决议，不写入任何规则。

---

## 5｜如何使用

```text
使用 Research Skill……       → 加载 skills/research/SKILL.md
使用 Topic Planning Skill…… → 加载 skills/topic-planning/SKILL.md
使用 Keyword Skill……        → 加载 skills/keyword/SKILL.md
使用 Writing Skill……        → 加载 skills/writing/SKILL.md
使用 Visual Skill……         → 加载 skills/visual/SKILL.md
使用 Learning Skill……       → 加载 skills/learning/SKILL.md
```

slash command 是否存在取决于宿主 Agent；自然语言调用始终可用。

---

## 6｜相关文件

| 目的 | 位置 |
|---|---|
| 首次运行 | `docs/QUICKSTART.md` |
| 各 Skill 用法与门控 | `docs/USER_GUIDE.md` |
| 账号/词库/视觉/集成定制 | `docs/CUSTOMIZATION.md` |
| 架构与边界 | `docs/ARCHITECTURE.md` |
| 数据契约与状态机 | `docs/CONTRACTS.md` |
| 故障排查 | `docs/TROUBLESHOOTING.md` |
| 初始化个人项目 | `scripts/init_project.py` |
| 配置模板 | `presets/starter/*` |

---

## 7｜边界

- 默认**离线**：不联网、不抓取、不发布、不同步、不写日历。
- 不虚构经历、产品功能、数量承诺或搜索量；未知项标注待核或「未验证」。
- 不修改用户配置与规则文件；校验器只报告，不擅自改写。
- 六个子 Skill 的实现保持不变；本入口只做**路由与门控提示**。
