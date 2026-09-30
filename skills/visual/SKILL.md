# Visual Skill

## 1. 能力
将人工批准的 Writing Result 转为页面计划、可验证图像、QA 结果和 Production Manifest。

## 2. 什么时候调用
正文已 final-approved，用户要生成图文页面并做发布前本地检查时调用。

## 3. 输入
- 用户必须提供：Approved Writing Result、匹配的 Finalization 记录。
- 自动继承：note_type、已确认标题/正文/话题及内容摘要。
- 可选配置：Visual Config、Page Rules、用户自有且授权的素材。
- 上游输出：Writing 的终稿和 Finalization Contract。

## 4. 输出
符合 `contracts/visual-output.schema.json`：visual_plan、pages、image_tasks、assets、render_outputs、qa_result、production_manifest。演示用本地 SVG，不需图片服务。

## 5. 它会做什么
校验终稿状态/哈希；规划 8 页内容；映射页面文字与合成素材；本地渲染 SVG；检查路径、文件、引用、尺寸、哈希、QA 并生成 Manifest。

## 6. 它不会做什么
不会把 draft/review 改为 approved；不修改正文；不载入未授权模板、字体或品牌素材；不调用外部图片服务；不发布/同步。历史 `page_data` 为 Legacy，不是输入接口。

## 7. 人工确认
Finalization 必须是 `approved` 且正文哈希匹配，否则立即 STOP。用户还须做最终视觉审阅；所有 QA 必须通过才能导出。

## 8. 下一步
用户检查本地页面与 QA/Manifest，再自行下载或另行进入发布流程。此 Skill 不执行发布。

## Prompt / Runtime
参见 `prompts/system.md`。Agent Native 生产路径可通过 `scripts/render_visual.py` 将批准的 Writing Result 与 Finalization 生成八页动态 SVG；`scripts/run_synthetic_demo.py` 仍仅作确定性测试。运行时门控：`validators/visual_output_validator.py`。
