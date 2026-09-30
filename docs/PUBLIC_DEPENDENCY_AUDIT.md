# PUBLIC_DEPENDENCY_AUDIT｜依赖与许可处置（Release Candidate）

本文件是发布候选 `0.1.0-rc.1` 的依赖与许可处置记录。分类采用最终发布口径，**不含 `UNKNOWN`，也不含过渡性 `REPLACE_REQUIRED`**：任何曾经需要替换的旧资源，要么已重写为本仓库原创内容，要么未纳入发布。

分类含义：

- **SAFE_TO_DISTRIBUTE**：本仓库原创、可随 MIT 许可分发。
- **SAFE_AS_DEPENDENCY**：规范/标准引用，不捆绑第三方代码。
- **USER_PROVIDED**：用户运行时提供，本仓库不携带。
- **OPTIONAL_EXTERNAL**：可选外部服务/集成，默认不启用、不调用。
- **PRIVATE_ONLY**：永不进入本仓库或任何公开导出。

| 类别/候选 | 盘点事实 | 最终分类 | 处置 |
|---|---|---|---|
| Python 核心（scripts/validators/engine） | 本仓库原创，仅用 Python 标准库 | SAFE_TO_DISTRIBUTE | 随 MIT 许可发布 |
| 本地 Research Adapter | 原创、离线、仅标准库 | SAFE_TO_DISTRIBUTE | 随 MIT 许可发布 |
| JSON Schema 契约 | 原创 Schema，仅引用 JSON Schema 2020-12 规范 | SAFE_TO_DISTRIBUTE | 随 MIT 许可发布 |
| JSON Schema 规范引用 | `$schema` 为标准规范 URI，无代码捆绑 | SAFE_AS_DEPENDENCY | 仅作规范引用 |
| 字体 | 不捆绑任何字体二进制；使用系统字体栈 | USER_PROVIDED | 用户环境提供；缺失时回退 generic sans-serif |
| 图标 | 不捆绑图标库；符号为内联 SVG 几何 | SAFE_TO_DISTRIBUTE | 原创几何绘制 |
| 图片/照片 | 仓库内无任何第三方图片二进制 | SAFE_TO_DISTRIBUTE | 无外部图片，仅原创矢量 |
| 视觉模板/版式 | 自研渲染器，非外部模板拷贝 | SAFE_TO_DISTRIBUTE | 随 MIT 许可发布 |
| 第三方 Python 包 | 运行时零依赖，无 vendored 包 | SAFE_AS_DEPENDENCY | 无需声明 |
| npm / Node 包 | 无 `package.json`/lockfile，无 npm 依赖 | SAFE_AS_DEPENDENCY | 无需声明 |
| MCP / API 适配示例 | `integrations/*` 仅空占位目录，无实现与凭证 | OPTIONAL_EXTERNAL | 默认关闭；用户自行启用 |
| Feishu / Calendar 集成 | 未实现，无真实映射或凭证 | OPTIONAL_EXTERNAL | 用户显式启用时另附条款核验 |
| 外部文档链接 | README/CHANGELOG 指向规范站点，运行时从不抓取 | OPTIONAL_EXTERNAL | 仅文档引用 |
| 用户配置与词库 | 用户运行时创建，已被 `.gitignore` 排除 | USER_PROVIDED | 不入版本控制 |
| 用户 Research 来源资料 | 用户提供的 JSON/CSV/Markdown | USER_PROVIDED | 不入版本控制 |
| 原账号/经营数据、私有词库、真实任务卡 | 保留在独立私有源区，永不导出 | PRIVATE_ONLY | 永久排除 |

## 与早期审计的差异

早期 Phase 2D 审计对字体、图标、模板、第三方代码、npm 传递依赖、Python 包、MCP、Calendar 连接器、外部 API 与 README 外链使用过 `REPLACE_REQUIRED`。本轮 RC 已确认这些旧资源**均未进入本仓库**：可重写的已重写为原创，不能确认的未纳入。因此最终分类收敛为上述五类，不存在待替换项。
