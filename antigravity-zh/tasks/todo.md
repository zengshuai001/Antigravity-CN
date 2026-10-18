# 卡死问题排查计划

- [x] 确认脚本入口和预期启动流程 -> 验证: 找到用户实际运行的脚本和它修改/启动 Antigravity 的路径
- [x] 复现或收集卡死证据 -> 验证: 获取脚本输出、后台安装日志、Antigravity 进程状态和应用日志
- [x] 定位最小根因 -> 验证: 将卡死归因到脚本等待、补丁内容、语言包 JSON、或 Antigravity 自身日志中的具体错误
- [x] 提出并确认修复方案 -> 验证: 修复前说明影响范围，得到确认后再改代码
- [x] 修复后验证 -> 验证: 运行相关脚本/校验命令，并记录结果

## Review

已确认:
- `scripts/apply.ps1` 会生成 `zh_cn_ui_main.js` 并将 `resources\extracted_asar` 重新打包为 `app.asar`。
- `bg_install.log` 卡在等待 PID 退出，说明后台安装路径可能会一直等待未退出的 Antigravity 进程。
- `translations\nls.messages.zh-CN.json` 通过数量与占位符校验，`zh_cn_ui_main.js` 也通过 `node --check` 语法校验。
- 原始 `app.asar.bak` 的 `dist\customScheme.js` 只注册 `plugin` 协议；当前 `extracted_asar\dist\customScheme.js` 额外注册了全局 `https` 协议处理器，用来替换 `/main.js`。这会影响主窗口加载 `https://127.0.0.1:<port>/`，是进入界面卡死的最小可疑根因。

建议修复:
- 先移除 `customScheme.js` 中全局 `https` 拦截，保留原版 `plugin` 协议处理。
- 重新打包 `app.asar` 后启动 Antigravity 验证是否能进入界面。
- 如果需要继续汉化 AI 面板，再另做更安全的注入方案，避免劫持整个 `https` 协议。

版本更新策略:
- 安装前读取 Antigravity 当前版本、`app.asar` hash、前端 bundle hash，并写入本项目的兼容性记录。
- 核心 NLS/product/extension 翻译走宽松校验: 结构和占位符通过即可应用。
- AI 面板补丁走严格校验: 只有 bundle hash 或已知特征匹配时才启用；不匹配时自动跳过，不影响启动。
- 提供 `Update`/`Extract` 流程: 新版本出现后先提取原文和前端 bundle，生成差异和待翻译清单，而不是直接套旧补丁。
- 安装结果要记录为 `stable-core`、`ai-ui-enabled` 或 `ai-ui-skipped-version-mismatch`，方便用户知道当前启用了哪些层。

最终结果:
- `scripts/apply.ps1` 默认改为 `stable-core` 模式，清理残留 AI UI bundle，并将 `customScheme.js` 恢复为不拦截 `https` 的核心模板。
- 新增 `-EnableAiUi` 可选模式，仅当 Antigravity 版本和 UI bundle hash 命中 `patches/ai-ui-compat.json` 时启用 AI 面板汉化。
- `scripts/bg_install.py` 改为调用 `apply.ps1`，避免后台安装器重复执行旧的高风险打包逻辑。
- `scripts/extract.ps1 -Update` 会生成版本更新报告，供新版本适配时确认 hash 和文本变化。
- 已在本机运行默认安装，安装状态为 `stable-core`。验证 `app.asar` 中不再包含 `protocol.handle('https')` / `zh_cn_ui_main` 拦截，`https://127.0.0.1:14360/` 和 `/main.js` 均返回 200，语言服务日志显示初始化成功。

AI UI 复查:
- [x] 验证结果: zh_cn_ui_main.js 已生成，但用户看到主界面仍未汉化。
- [x] 查明 Electron 窗口是否实际加载翻译后的 /main.js，而不是语言服务器内嵌原始 bundle。
- [x] 若是缓存问题，清理缓存并验证；若是拦截问题，改为可实际生效的资源替换方案。

AI UI 复查结果:
- 原 `protocol.handle('https')` 路线没有可靠命中主窗口的 `/main.js` 请求。
- 已改为注册 `agy-ui://` 自定义协议，并通过 `webRequest.onBeforeRequest` 只将 `https://127.0.0.1:*/main.js` 重定向到本地翻译 bundle。
- 已重新安装 `-EnableAiUi` 并启动 Antigravity。主进程日志出现 `Serving translated AI UI bundle`，Electron 页面文本包含“文件 / 视图 / 新建对话 / 历史对话 / 计划任务 / 项目 / 设置 / 问任何问题”等中文。

设置页补翻:
- 已补充 AI UI 设置页文案: `外观 / 聊天设置 / 详细智能体对话 / 显示并保留中间思考步骤 / 浅色主题 / 深色主题 / 预设 / 默认浅色 / 默认深色 / 背景 / 前景 / 强调色`。
- 已补充设置导航分类: `模型 / 自定义 / 浏览器 / 应用`。
- 已重新运行 `scripts/apply.ps1 -EnableAiUi`，生成结果为 `66/81` 条命中替换。

设置中心全量补扫:
- 已将 `scripts/translate_ui.py` 扩展到 181 条词条，并重新生成 `zh_cn_ui_main.js`，本次命中 162 条。
- 新增覆盖范围包括 `Permissions / Browser / Customizations / App / Account / Editor / Tab / Best of N` 对应的大部分标题、标签、描述和常见下拉项。
- 本机在 2026-05-20 自动升级到 `2.0.1` 后，旧的 `apply.ps1` 安装判断失效；已确认原因是 `resources/app/out/nls.messages.json` 路径在 `2.0.1` 中已不存在。
- 已手动将 `patches/customScheme.ai-ui.js` 重新打入 `2.0.1` 当前 `app.asar`，主日志再次出现 `Serving translated AI UI bundle`。

运行态补翻继续:
- 为避免再次写坏 bundle，`scripts/translate_ui.py` 已改为优先按字符串字面量安全替换，再辅以少量片段替换。
- 最新一轮已扩展到 219 条词条，重生成命中 192 条，并通过 `node --check`。
- 运行中的项目设置页已验证变成中文：
  `管理项目文件夹、智能体设置和权限 / 文件夹 / 添加文件夹 / 智能体设置 / 安全预设 / 产物评审策略 / 本地权限 / 文件访问规则 / 网络访问规则 / 终端命令 / 沙箱外命令 / MCP 工具 / 危险区域 / 删除项目`
- 当前残留主要是运行态拼接文本，例如：
  `Learn more about 无限制`
  `Inherits from global settings. Local permissions have higher priority. 了解更多.`
  `Rules`
  `Show 1 breakdown`

收尾补充:
- 已继续补齐账号页、应用页、通知页、快捷键页的主要固定说明。
- 最新一轮 `scripts/translate_ui.py` 已扩展到 289 条词条，重生成命中 251 条，并继续通过 `node --check`。
- 用户确认当前完成度足够，剩余少量动态/拼接残留不再继续处理。
