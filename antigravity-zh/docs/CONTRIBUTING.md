# 贡献指南

感谢你对 Antigravity 2.0 汉化项目的关注！

## 如何贡献翻译

### 1. Fork 本仓库

### 2. 修改翻译文件

翻译文件位于 `translations/nls.messages.zh-CN.json`，格式为 JSON 数组：

```json
[
  "翻译后的文本1",
  "翻译后的文本2",
  ...
]
```

每个条目对应 `source/nls.keys.original.json` 中的键名。

### 3. 翻译规范

- **占位符保留**: `{0}`, `{1}` 等占位符必须保留且位置合理
- **快捷键保留**: `&&` 前缀的热键字符保留（如 `&&File` → `文件(&&F)`）
- **术语一致性**: 参考下方术语表
- **简洁优先**: 中文翻译应比英文更简洁
- **语境理解**: 参考 `source/nls.keys.original.json` 理解上下文

### 4. 术语表

| 英文 | 中文 | 备注 |
|------|------|------|
| Terminal | 终端 | |
| Debug | 调试 | |
| Breakpoint | 断点 | |
| Extension | 扩展 | |
| Command Palette | 命令面板 | |
| Settings | 设置 | |
| Workspace | 工作区 | |
| Explorer | 资源管理器 | |
| Source Control | 源代码管理 | |
| Output | 输出 | |
| Problems | 问题 | |
| Search | 搜索 | |
| Editor | 编辑器 | |
| Sidebar | 侧边栏 | |
| Status Bar | 状态栏 | |
| Activity Bar | 活动栏 | |
| Panel | 面板 | |
| Tab | 选项卡 | |
| Snippet | 代码片段 | |
| Refactor | 重构 | |
| Lint | 代码检查 | |
| Hover | 悬停 | |
| Peek | 速览 | |
| Fold | 折叠 | |
| Agent | 智能体 | Antigravity 特有 |
| Chat | 对话 | AI 相关 |
| Prompt | 提示词 | AI 相关 |
| Model | 模型 | AI 相关 |
| Tool | 工具 | Agent 工具调用 |
| Artifact | 产物 | Agent 产物 |

### 5. 提交 PR

- PR 标题格式: `[翻译] 模块名: 简要描述`
- 说明翻译了哪些内容和条目数量

## 报告问题

- 翻译错误: 使用 Issue 模板"翻译修正"
- 版本更新: 使用 Issue 模板"版本更新"
