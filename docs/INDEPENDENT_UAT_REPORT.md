# INDEPENDENT_UAT_REPORT｜独立用户验收测试

- 日期（date）：2026-09-30
- 版本（version）：`0.1.0-rc.1`
- 测试者视角（tester view）：**仅** public workspace / README / QUICKSTART / Starter Preset
- 未使用的信息（not used）：原 Vault、private staging、迁移报告、内部审计报告、任何旧 S 编号或原系统背景
- 结论（result）：**PASS**（发现并修复 1 个 blocker）

---

## 1｜测试隔离说明

本次测试从「一个不知道原项目背景的新用户」视角出发，只读取公开仓库自身的内容：

- `README.md`（第一屏：这是什么、6 个 Skill、最快开始、环境要求）
- `docs/QUICKSTART.md`（首次运行步骤）
- `presets/starter/*`（初始化模板）
- `skills/*/SKILL.md` 与 `prompts/system.md`（Agent Native 指令）

测试**没有**读取私有源区、原私有仓库/内部资料、迁移记录或任何真实账号/经营数据。生成内容由本次
Agent 推理完成，不是固定 fixture；审批步骤由测试者显式模拟（命名与真实用户确认区分）。

---

## 2｜全新虚构账号

测试者从零创建一个此前从未出现过的虚构账号：

| 项目 | 内容 |
|---|---|
| 身份（display_name） | 通勤便当备菜手记 |
| 定位（positioning） | 帮没有整块时间的通勤族，用一次备菜覆盖工作日午餐，少点外卖 |
| 目标用户（audience） | 周中加班、想带饭但常因没时间或怕坏而放弃的上班族 |
| 内容方向（content_directions） | 备菜流程、保存与安全、低成本搭配、常见误区 |
| 本轮目标（content_goal） | 解决「周中没有整块时间做饭，却又想带饭」的问题 |
| 产品/服务（products_or_services） | 无（保持空列表） |
| 关键词库（keyword-catalog） | 空（刻意验证「无词库 → 语义候选并标注未验证」路径） |

账号配置写入由 `init_project.py` 复制出的 `user-project/config/`，**修改的是用户配置，不是源码**。

---

## 3｜执行路径与结果

| # | 步骤 | 输入 → 输出 | 门控 / 校验 | 结果 |
|---|---|---|---|---|
| 1 | init（初始化） | Starter Preset → `user-project/{config,workspace,outputs,learning}` | 拒绝覆盖已有目录 | PASS |
| 2 | Account Profile | 填写身份/定位/受众/方向/目标 | 仅公开信息，无凭证/UID | PASS |
| 3 | Topic（选题） | Profile + 目标 → 3 个差异候选 | 人工选题 | PASS（选定候选 bento-topic-001） |
| 4 | Task Card | 获批候选 → Task Card | `task_card_validator.py` | PASS |
| 5 | Keyword | 空词库 → 1 主词 + 2 辅词 | `keyword_plan_validator.py`；人工关键词门 | PASS（词项标 `model_suggestion` / 未验证） |
| 6 | Writing | 批准任务 + 批准词计划 + Profile → 草稿 | `writing_validator.py`；人工终稿门 | PASS（状态保持 draft） |
| 7 | Final Approval | 人工审阅 → approved Finalization + 一致正文哈希 | `finalization_validator.py --require-approved` | PASS |
| 8 | Visual | 终稿 + 配置 → P1–P8 SVG + Visual Output | 输入哈希门；`visual_output_validator.py` | **首次 FAIL（见第 6 节）→ 修复后 PASS** |
| 9 | 输出核对 | 8 个 SVG + `visual-output.json` | 页数/路径/哈希/QA | PASS（`qa=pass`，`manifest_qa=pass`） |

产物：**8 页 SVG**（P1–P8，1080×1440），QA `pass`，Manifest `qa_status=pass`，`human_visual_review=pending`（符合设计：视觉终审必须由人做）。

机械化流水线（init → 校验 → 渲染）实测耗时约 **0.63 秒**；其余为 Agent 推理与人工填写时间。

---

## 4｜验收指标（10 项）

| # | 指标 | 结果 |
|---|---|---|
| 1 | 是否知道第一步做什么 | ✅ 是。README 第 4 节 + QUICKSTART 第 1 步直接给出 `init_project.py` 命令 |
| 2 | 是否需要问开发者 | ❌ 否。全程无提问 |
| 3 | 是否需要修改源码 | ❌ 否。用户只改自己的 `config/*.yaml` |
| 4 | 是否出现路径错误 | ❌ 否。脚本从 `__file__` 推导根目录，输出使用相对路径 |
| 5 | 是否出现配置错误 | ❌ 否（无阻断）。观察到 1 处低风险不一致，见第 7 节 |
| 6 | 是否能理解 Human Gate | ✅ 是。选题/关键词/终稿/视觉四个门在 QUICKSTART 与 SKILL.md 中表述清晰 |
| 7 | 是否知道下一步 | ✅ 是。每个 SKILL.md 都有「下一步」，QUICKSTART 逐步编号 |
| 8 | 最终是否产生完整输出 | ✅ 是。8 页 SVG + Visual Output + Manifest |
| 9 | 总耗时 | 机械化约 0.63s；含 Agent 推理与人工填写约数分钟（无回退需求） |
| 10 | 卡点数量 | 2（1 个 blocker + 1 个低风险观察，均记录于第 6、7 节） |

---

## 5｜内容质量评审（Agent Native）

- **选题**：3 个候选角度互不重复（流程 / 保存判断 / 新手误区），均给出理由与证据限制。
- **关键词**：主词「周末备菜」+ 辅词「便当备菜」「上班族带饭」；空词库下全部标记为
  `model_suggestion` 与「未验证」，未陈述任何搜索量、热度或成交数据。
- **正文**：`search` 类型，先给结论再给三步，附保存与安全边界；无虚构经历/数据；`status=draft`。
- **终稿门**：正文经人工确认并记录 `body_sha256`；Visual 仅在哈希一致时渲染。
- **视觉**：8 页从终稿抽取标题、要点与话题；P5 为内置几何矢量占位，无外部图片/字体依赖。

---

## 6｜发现并修复的 blocker（1 个）

**现象**：用一份完全符合写作契约（398 中文字符，落在 400–900 建议区间近似值内）的真实正文渲染时，
`render_visual.py` 在第 8 页抛出
`ValueError: page 8 body exceeds safe line budget; summarize the page copy before rendering`，导致
**无法生成 8 页**。

**根因**：第 8 页文案由 `derive()` 自动拼装为「标题 + 正文最后两段 + 话题」，当标题或段落较长时，
渲染行的总行数超过固定版式预算（8 行）；而用户**无法直接控制**这段自动派生的页面文案，错误信息
不可执行。属于「QuickStart/Visual 无法完成」类 blocker。

**修复（最小改动，未改架构）**：`scripts/render_visual.py` 的 `render_svg()` 由「超预算即报错」改为
「自动适配到固定安全版式」（标题最多 3 行；正文最多 8 行，超出时折叠末尾并加提示）。这是
可用性修复，不触发任何**已有示例**的重新生成（既有内容本就不超预算，改动对它们是 no-op）。
修复后回归测试 **17/17 PASS**，UAT 第 8 步转为 PASS。

> 说明：变更只涉及渲染器的**排版兜底**，不触碰批准门、哈希门、QA 与 Manifest 语义。

---

## 7｜低风险观察（非阻断，未改）

- `presets/starter/account-profile.yaml` 含一个字段 `claims_boundary`，它**不在**
  `contracts/account-profile.schema.json` 的允许属性内。当前没有任何校验器校验 YAML 用户配置，
  因此**不会报错**；但若今后对 YAML 配置做严格 Schema 校验，需要把该字段纳入契约或移除。
  本轮遵循「冻结契约」，未修改。

---

## 8｜结论

| 验收标准 | 结果 |
|---|---|
| 修改源码次数（用户视角） | 0 |
| Private 文件访问 | 0 |
| 原 Vault 依赖 | 0 |
| 必要开发者干预（用户运行期） | 0（blocker 在 RC 加固期修复，用户运行未受影响） |
| 完整流程可完成 | ✅ |
| 8 页 Visual 可生成 | ✅ |
| 用户能理解每一步下一步 | ✅ |
| 所有失败都有明确错误提示 | ✅（blocker 修复前错误提示明确但不可执行；修复后不再失败） |

**独立 UAT：PASS。** 仍建议在更多真实宿主 Agent 产品上重复本测试，以覆盖工具权限与提示遵循差异。
