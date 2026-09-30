# USER_GUIDE｜使用指南

> 本文件是**使用流程的唯一所有者（owner）**。首次运行请先看 [`QUICKSTART.md`](QUICKSTART.md)。

## 0｜总览

```text
Research（可选） → Topic Planning → Keyword → Writing → Visual
Learning（旁路，不阻塞）
```

每个 Skill 都有：明确输入、稳定输出、可运行校验器、**人工确认门**。用自然语言调用即可，例如
`使用 Keyword Skill，为已批准任务生成关键词计划`。

---

## 1｜Research（可选）

- **何时用**：不确定方向是否有人需要、想先收集证据和候选角度。
- **输入**：研究主题/问题；可选受众、内容领域、研究目标、种子词、你提供的本地资料（JSON/CSV/Markdown）。
- **做什么**：归纳用户问题、需求信号、表达方式、候选主题与候选词；每条附来源与置信限制。
- **不做什么**：不定正式题、不写任务卡、不改词库、不联网抓取、不伪造搜索量。
- **人工门**：Research Result 永远是 `proposed`；是否采用由你在 Topic Planning 决定。
- **下一步**：把结果交给 Topic Planning，或直接跳过。

运行（本地模式）：

```powershell
python scripts/run_research.py --request <request.json> --sources <sources.json> --output <result.json>
```

## 2｜Topic Planning

- **何时用**：决定下一篇写什么。
- **输入**：你的 Account Profile + 本轮目标；可选产品/服务、Research Result、避重复清单。
- **做什么**：生成**至少 3 个**实质不同的候选，给出理由、内容类型、证据限制与风险。
- **不做什么**：候选不会自动入库；未批准前不会编译正式任务卡。
- **人工门**：你回复「批准第 N 个」后才编译任务卡；`Reject` 停止，`Request Revision` 只改候选。
- **下一步**：把 `status=approved` 的任务卡交给 Keyword。

## 3｜Keyword

- **何时用**：题目已定，需要确定覆盖哪些搜索词、怎么自然布局。
- **输入**：已批准任务卡；可选你自己的词库、账号画像、语言/地区。
- **做什么**：匹配搜索意图，给出主词（恰 1 个）与辅词、标题/正文/话题位置建议、话题映射。
- **不做什么**：不保证排名/流量，不编造搜索量，不静默改任务卡或正文；模型推断词必须标「未验证」。
- **人工门**：逐词确认后，计划与所有词才转 `approved/locked`。
- **下一步**：把已批准关键词计划交给 Writing；若 Writing 发现词与内容冲突，应返回 Keyword Revision Request。

## 4｜Writing

- **何时用**：题目和关键词都已确认，要出完整笔记草稿。
- **输入**：已批准任务卡 + 已批准关键词计划 + 你的 Account Profile；可选已核实的产品资料。
- **做什么**：按内容类型组织结构，自然使用**锁定词**，产出标题、正文、话题、关键词使用报告与 warnings。
- **不做什么**：不虚构经历/案例/产品功能/数量承诺；不自行发布；草稿**绝不**自动变成 final。
- **人工门**：你审事实、产品声明、语气与平台要求并确认终稿。
- **下一步**：确认后生成 Finalization（`approved` + body SHA-256），再交给 Visual。

## 5｜Finalization（终稿门）

- 状态机与字段见 [`CONTRACTS.md`](CONTRACTS.md#6finalization-状态机)。
- 你明确确认后：`status=approved`，填写 `approved_by` 与 `finalized_at`，并记录正文哈希。
- **任何正文改动都会使批准失效**（回到 `revision_required`），必须重新审阅并重跑视觉/QA。

## 6｜Visual

- **何时用**：正文已终稿批准，要出图文页面。
- **输入**：已批准 Writing Result + 匹配的 Finalization；可选视觉配置与自有授权素材。
- **做什么**：校验批准状态与哈希 → 规划 8 页 → 本地渲染 SVG → 路径/尺寸/哈希/引用校验 → QA + Manifest。
- **不做什么**：不吃 draft/review；不改正文；不用未授权素材；不调用外部图片服务；不发布。
- **人工门**：逐页人工视觉验收；发现溢出/错字/事实改写/授权问题即阻止 Export。
- **下一步**：检查 `outputs/` 下的 P1–P8 与 Manifest。

运行（本地渲染）：

```powershell
python scripts/render_visual.py --writing <writing-result.json> --finalization <finalization.json> --config <visual-config.yaml> --output <outputs-dir>
```

## 7｜Learning（旁路）

- **何时用**：你想从「草稿→终稿」的改动里沉淀可复用经验。
- **输入**：原 Writing Result + 对应 approved Finalization；可选修订历史/反馈/视觉 QA。
- **做什么**：输出可观察差异、重复模式、证据，并提出 Core/Adapter/One-off 三类建议。
- **不做什么**：不自动写回 Profile、Skill、Contract、Rules；不把相关性说成因果。
- **人工门**：提案须你显式 Accept/Reject；Accept 只**记录**决议（`applied=false`）。

```powershell
python scripts/run_learning_review.py --original <writing-result.json> --final <finalization.json> --feedback <feedback.json> --output <review.json>
python scripts/record_learning_decision.py --review <review.json> --decision accept --output <decision.json> --reviewer "<你>"
```

---

## 8｜产物与位置

| 阶段 | 典型产出 |
|---|---|
| Topic Planning | 候选清单、Task Card |
| Keyword | Keyword Plan |
| Writing | Writing Result（draft） |
| Finalization | Finalization（approved） |
| Visual | P1–P8 页面、QA、Production Manifest、Visual Output |
| Learning | Learning Review、Decision |

产物写入你项目的 `workspace/`、`outputs/`、`learning/`；用户数据默认被 `.gitignore` 排除。

## 9｜失败时的行为

- 任何校验失败都会打印 `FAIL <对象> | <字段> | <原因>` 并**非零退出**，不静默覆盖。
- 缺图/缺许可/正文哈希不符时 Visual **fail-closed**，不会生成误导性的最终包。
- 排错见 [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)。
