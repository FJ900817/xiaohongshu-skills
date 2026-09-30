# ARCHITECTURE｜架构与边界

> 本文件是**架构的唯一所有者（owner）**。其他文档若涉及架构，只链接本文件，不重复描述。

## 1｜设计目标

提供一套**与模型/供应商无关、可离线运行**的小红书图文工作台：由宿主 AI Agent 执行推理，本仓库提供上下文、指令、数据契约、校验器与人工确认门。核心主张：

- **Agent Native**：模型不在本仓库内，也不强制任何 API。
- **证据先行**：事实性输出必须有来源或明确的「未验证」标记。
- **人工在环**：选题、关键词、终稿、视觉验收都必须由人确认。
- **默认离线**：不联网、不抓取、不同步、不发布。
- **可移植**：全部路径由工作区/配置推导，跨 Windows/macOS。

## 2｜六层结构与职责

```text
              ┌────────────────────────── 用户可见层（6 Skills） ──────────────────────────┐
              │  Research（可选） → Topic Planning → Keyword → Writing → Visual               │
              │                                   Learning（旁路，独立）                     │
              └──────────────────────────────────────────────────────────────────────────────┘
                          │调用
              ┌───────────┴──────────── 支撑层（非用户第一层概念） ───────────┐
              │ Contracts：字段唯一真源   Validators：只报告不修改             │
              │ Workflows：阶段/输入输出/人工门   Rules：跨 Skill 共享约束      │
              │ Adapters/Presets：账号与视觉配置   Integrations：可选外部适配   │
              └──────────────────────────────────────────────────────────────┘
```

- **Contracts** 是字段真源，任何 Skill 都引用它，不各自维护副本 → 见 [`CONTRACTS.md`](CONTRACTS.md)。
- **Validators** 对有效/无效输入都给出可解释结果，**绝不**自动改写用户数据。
- **Workflows** 只描述阶段与门控，不复刻能力规则。
- **Adapters/Presets** 承载账号/平台差异；真实值留在本地。
- **Integrations** 为可选外部适配，默认关闭，不进入本地主流程。

## 3｜仓库目录

```text
xiaohongshu-skills/
├── README.md                     # 用户首页
├── LICENSE / NOTICE.md           # 许可与第三方记录
├── VERSION / CHANGELOG.md        # 版本
├── skills/                       # 六个用户可见入口（含 prompts/system.md）
│   ├── research/  topic-planning/  keyword/  writing/  visual/  learning/
├── contracts/                    # 版本化 JSON Schema（字段真源）
├── validators/                   # 可运行校验器（stdlib）
├── rules/                        # 跨 Skill 共享规则（占位）
├── workflows/                    # 流程描述（占位）
├── adapters/research/            # 本地来源适配器
├── presets/starter/              # 可复制配置模板
├── examples/                     # synthetic 与 first-run 合成样例
├── tests/                        # 回归测试与质量用例
├── integrations/                 # 可选外部适配（feishu/calendar/platform，占位）
├── scripts/                      # 可移植 CLI 与本地运行辅助
├── runtime/                      # Agent 运行协议与执行上下文 Schema
└── docs/                         # 本文档集（QUICKSTART/USER_GUIDE/CONTRACTS/...）
```

## 4｜端到端数据流与人工门

```text
Account Profile + 目标
        │
 Research（可选，只产证据）
        ▼
 Topic Planning ──[人工选题门]──▶ Task Card（status=approved）
        ▼
 Keyword ──[人工关键词门]──▶ Keyword Plan（approved + locked）
        ▼
 Writing ──▶ Writing Result（status=draft）
        ▼
 Finalization ──[人工终稿门]──▶ status=approved（含 body SHA-256）
        ▼
 Visual ──▶ 8 页 SVG + QA + Production Manifest
        ▼
 Export（本地交付；不发布）

Learning（旁路）：draft vs approved final → proposal → [人工采纳]
```

关键门控：**Visual 硬性只接受 `approved` 且哈希一致的正文**；正文任何改动都会使批准与下游 QA 失效。

## 5｜Public / Private 边界

| 级别 | 内容 |
|---|---|
| PUBLIC_CORE | 通用接口、无凭证逻辑、通用流程、测试、合成样例 |
| PUBLIC_AFTER_SANITIZE | 需先抽象路径/账号/平台映射、删商业细节、核许可后才能导出 |
| PRIVATE_ONLY | 原 staging、真实账号与经营数据、真实任务卡/正文、产品真值、外部空间/表 ID、凭证、运行产物、未授权素材 |

- 私有源区、原始 Vault 与迁移记录物理地**位于本仓库之外**，不是运行依赖。
- `00_staging/` 若出现即视为 PRIVATE / DO NOT PUBLISH。
- 仓库内所有「合成」样例在文件名与元数据均标注 `synthetic`。

## 6｜可扩展点

- 新增内容类型：`contracts/note-type.schema.json` 需要版本评审（当前三枚举）。
- 新增数据源：实现 `adapters/` 下的适配器，不改 Core Skill。
- 新增外部集成：在 `integrations/` 下实现，用户显式启用、最小权限、dry-run + 确认。
- 任何契约变更：提升 `schema_version` 并更新 fixtures/tests。

## 7｜历史与变更

Phase 2D/2E 的实现报告、依赖审计草案与设计候选稿属于**内部资料**，不随本公开仓库发布，仅作历史证据，**不作为当前规则**。当前规则的唯一所有者是本文件及 [`CONTRACTS.md`](CONTRACTS.md)、[`USER_GUIDE.md`](USER_GUIDE.md)、[`CUSTOMIZATION.md`](CUSTOMIZATION.md)。
