# FRESH_CLONE_TEST｜全新环境复现测试

- 日期（date）：2026-09-30
- 版本（version）：`0.1.0-rc.1`
- 目标：模拟「GitHub 用户下载仓库后在干净环境首次运行」的状态，验证不依赖任何已有运行产物。

---

## 1｜方法

1. 把公开仓库整体复制到一个**全新的隔离目录**，模拟下载后的状态。
2. 删除复制体中的 `__pycache__/` 与 `*.pyc`，确保**不复用任何缓存/运行产物**。
3. 复制体文件数：**156**；不含任何缓存文件。
4. 全部命令都在复制体目录内、用干净的解释器执行，**不引用**原工作目录或任何运行输出。

> 说明：本环境无 `git` 可执行文件，无法执行 `git clone`；因此以「整目录复制 + 清除缓存」等价模拟，
> 并单独核对 `.gitignore` 规则（见第 4 节）。

---

## 2｜执行步骤与结果

| # | 步骤 | 命令 | 结果 |
|---|---|---|---|
| 1 | 阅读入口 | README / QUICKSTART（人工） | 可独立理解，无需作者解释 |
| 2 | QuickStart 自检 | `python -m unittest discover -s tests -p "test_*.py"` | **17/17 PASS** |
| 3 | 就绪检查 | `python scripts/check_phase_2d_ready.py` | **PHASE 2D READY = YES** |
| 4 | 合成首次运行 | `python scripts/run_synthetic_demo.py` | **END_TO_END=PASS; pages=8** |
| 5 | 初始化新项目 | `python scripts/init_project.py --destination ./fresh-user-project` | **PROJECT INITIALIZED** |
| 6 | 本地渲染（first-run 输入） | `python scripts/render_visual.py --writing examples/first-run/writing-result.json --finalization examples/first-run/finalization.json --config examples/first-run/user-project/config/visual-config.yaml --output ./fresh-render` | **PASS Visual Output**；生成 8 个 SVG |
| 7 | 视觉校验 | `python validators/visual_output_validator.py ./fresh-render/visual-output.json --finalization examples/first-run/finalization.json` | **PASS Visual Output** |

覆盖的链路：init → Account Profile → Topic → Keyword → Writing → Final Approval → Visual（8 页）。
第 4 步覆盖六个 Skill 的完整闭环（含 Research 与 Learning 旁路）。

---

## 3｜可复现性核对

把克隆体中重新渲染的 8 页 SVG 与仓库内已提交的 8 页逐一比对 SHA-256：

```text
P1: MATCH  P2: MATCH  P3: MATCH  P4: MATCH
P5: MATCH  P6: MATCH  P7: MATCH  P8: MATCH
```

- 8/8 字节级一致 → 渲染是**确定性**的，且新环境与提交产物一致。
- 这也证明 Independent UAT 中针对渲染器的 blocker 修复对既有示例是 **no-op**（既有示例未超版式预算）。

---

## 4｜干净环境与版本控制核对

- **不依赖既有运行产物**：缓存已清除，`fresh-user-project/` 与 `./fresh-render/` 均为本次新生成。
- **`.gitignore` 与 fixture 保留规则**（无法运行 git，按规则逐一核对）：
  - 用户/运行数据被忽略：`.user-data/`、`user-data/`、`user-project/`、`outputs/`、`.env*`。
  - 示例 fixture 被**显式否定保留**：`!examples/first-run/outputs/`、`!examples/first-run/outputs/**`、
    `!examples/first-run/user-project/`、`!examples/first-run/user-project/**`。
  - `runtime/` 未被忽略（公开运行协议需要入库）。
  - 说明：在真实 `git init` 后应执行 `git status --ignored` 复核；本环境无 git，故以规则推理 + 就绪脚本为准。
- **无私有内容**：复制体不含 `00_staging/`、真实账号资料、凭证或绝对用户路径。

---

## 5｜结论

| 检查 | 结果 |
|---|---|
| 干净环境下 6 Skill 回归 | **PASS**（17/17 单测；合成 E2E PASS） |
| 干净环境下 init_project | **PASS** |
| 干净环境下 Visual 8 页 | **PASS**（且与提交产物 8/8 一致） |
| 复用已有运行产物 | **否** |
| 原 Vault / 私有源依赖 | **0** |

**Fresh Clone Test：PASS。**
