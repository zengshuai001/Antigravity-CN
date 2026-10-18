# Google Antigravity 中文本地化项目 (通用开源版)

<p align="center">
  <img src="https://img.shields.io/badge/Antigravity-1.x%20%7C%202.0%2B-blue.svg?style=flat-square" alt="Antigravity Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue.svg?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/badge/Dependencies-Zero-orange.svg?style=flat-square" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
</p>

本项目为 Google 强大的 AI 编程工具 **[Google Antigravity](https://antigravity.google/)** 提供全架构、跨平台、深度且安全的界面中文本地化（汉化）方案。

无论你是刚接触 Antigravity 的新手用户，还是资深开发者，都可以通过本项目提供的**一键脚本**，秒级完成全套界面的中文汉化，并可随时**一键无损还原**为官方原版英文状态！

---

## 🌟 核心特性

- 🚀 **小白友好，一键操作**：Windows 用户双击 `.bat`，macOS 用户双击 `.command` / 运行 `.sh`，全程无需配置复杂环境。
- 📦 **零外部依赖**：基于原生 Python 3 标准库打造，无需安装 Node.js、npm、asar 工具包或任何第三方 Python 库（纯净轻量）。
- 🛡️ **安全自动备份**：首次注入汉化前自动备份原始纯净文件（`.bak`），杜绝重复覆盖，保证随时可完美回滚。
- 🔄 **一键还原英文**：提供独立的一键还原脚本，随时随地秒级切回官方原版英文。
- 🎯 **全版本架构自适应**：
  - **Antigravity 2.0+**（含 2.0.x ~ 2.24.x+ 最新版）：纯 Python 解析 Electron `app.asar`，双上下文注入 DOM 动态翻译引擎并重打包，自动修正 SHA256 完整性哈希。
  - **Antigravity 1.x**：自动注入 `workbench.html` 并同步更新 `product.json` 校验和，消除“安装受损”弹窗警告。
- 🔍 **路径完全动态化**：自动通过系统环境变量（`%LOCALAPPDATA%`、`%ProgramFiles%`、`$HOME` 等）与运行中进程智能定位安装目录，支持任意盘符与自定义安装路径。
- ⚠️ **版本比对与防白屏守护**：内置版本智能校验机制，如果检测到用户的 Antigravity 版本高于汉化包已适配版本，会自动弹出系统级警告提示，防止小白因官方架构大更新导致白屏。
- 🛡️ **代码与终端防污染保护**：严格锁定代码编辑器、终端、提示建议框、SVG 图标等代码区域不予翻译，只翻译界面按钮、菜单、设置项和操作提示。
- 🏷️ **标准社区标签检索**：原生支持 `antigravity`, `antigravity-ide`, `antigravity-tools`, `antigravity-chinese`, `antigravity-zh` 社区统一检索规范。

---

## 📋 运行前准备

本项目仅需要系统安装有 **Python 3**（Python 3.6 或更高版本）：

1. 打开 [Python 官方下载页面](https://www.python.org/downloads/) 下载并安装。
2. ⚠️ **特别注意（Windows 用户）**：安装时在第一屏**务必勾选** `Add python.exe to PATH`（将 Python 添加到环境变量）！

---

## 🚀 小白快速上手指南

### 🖥️ Windows 用户

#### 1. 一键汉化
1. 彻底退出正在运行的 Antigravity（如未完全退出，脚本也会贴心地帮您自动安全关闭）。
2. **双击运行根目录的 `一键汉化.bat`**。
3. 脚本会自动检测安装目录并完成备份与汉化注入。
4. 看到 `[SUCCESS] 恭喜！Antigravity 界面中文本地化注入成功！` 后，按提示重新启动 Antigravity 即可看到熟悉的中文界面！

#### 2. 一键还原英文
- 想要切回官方原版英文时，**直接双击运行根目录的 `一键还原英文.bat`** 即可瞬间回滚！

---

### 🍎 macOS 用户

#### 1. 一键汉化
1. 退出正在运行的 Antigravity。
2. **双击运行 `run_hanhua.command`**（或在终端打开本目录执行 `./run_hanhua.sh`）。
3. 按照屏幕提示输入选项（默认按回车即开始汉化并自动备份）。
4. 汉化完成后重新启动 Antigravity。

#### 2. 一键还原英文
- **双击运行 `restore_english.command`**（或终端运行 `./restore_english.sh`）即可瞬间还原为官方原版英文。

> 💡 **macOS 权限提示**：
> 如果系统提示没有执行权限或被安全策略拦截，请打开终端执行以下命令赋予权限：
> ```bash
> cd <本文件夹路径>
> chmod +x *.sh *.command
> ```

---

## 🛠️ 高级命令行用法 (开发者进阶)

除了双击脚本交互菜单，你也可以直接在终端中使用命令行参数：

```bash
# 查看当前系统环境、Antigravity 安装路径与汉化状态
python auto_localize.py --status

# 仅执行原版文件安全备份（不进行汉化注入）
python auto_localize.py --backup

# 非交互模式直接执行汉化注入（适合静默脚本调用）
python auto_localize.py --apply

# 一键还原回滚至官方原版英文状态
python auto_localize.py --restore

# 手动指定 Antigravity 的安装目录（适合特殊自定义目录）
python auto_localize.py --install-dir "D:\CustomPath\Antigravity"
```

---

## 📂 项目结构说明

```text
├── auto_localize.py          # 核心驱动引擎：跨平台/自适应架构/安全备份与注入/还原
├── ag_zh_inject.js           # 前端 DOM 高性能监听与翻译引擎（防代码污染、防死循环）
├── zh_cn_dict.json           # 深度优化的中文映射词库（涵盖设置、菜单、快捷键等）
│
├── 一键汉化.bat              # [Windows] 小白双击汉化入口
├── 一键还原英文.bat          # [Windows] 小白双击还原英文入口
├── run_hanhua.bat            # [Windows] 通用汉化启动脚本
│
├── run_hanhua.sh             # [macOS/Linux] 终端通用汉化脚本
├── restore_english.sh        # [macOS/Linux] 终端一键还原脚本
├── run_hanhua.command        # [macOS] 双击直达汉化启动项
├── restore_english.command   # [macOS] 双击直达还原启动项
│
├── 一键创建并发布到GitHub.bat # 一键在 GitHub 创建仓库并自动绑定社区 Topics
├── publish_github.py         # 仓库发布与社区标签配置辅助引擎
│
├── .gitignore                # Git 忽略配置（防止隐私数据、运行缓存外泄）
└── README.md                 # 傻瓜式中文使用说明文档
```

---

## ❓ 常见问题 FAQ

#### Q1: 双击 `.bat` 提示“未在系统 PATH 中找到 Python 3”怎么办？
- 可能是安装 Python 时没有勾选添加到环境变量。请重新运行 Python 安装包，选择 `Modify`，并在列表中勾选 `Add Python to environment variables`。

#### Q2: 官方发布了 Antigravity 新版本更新，更新后界面又变成英文了怎么办？
- Antigravity 官方自动更新会拉取官方原版 `app.asar` 覆盖。更新完成后，只需**重新双击运行一次 `一键汉化.bat`** 即可恢复中文！

#### Q3: 为什么代码、终端命令和会话标题没有被翻译？
- 这是出于代码安全性的刻意设计！为了防止汉化破坏您正在编写的代码、脚本变量名、CLI 终端命令输出，系统对编辑器、终端、代码块做了严格隔离保护。

#### Q4: 杀毒软件提示“修改文件”或拦截怎么办？
- 本项目代码完全开源透明，核心原理是修改本地安装目录下的前端语言资源。部分安全防护软件会对进程退出和文件替换较敏感，点击“允许”或“信任”即可。

---

## 📄 开源许可与声明

- 本项目遵循 [MIT 许可证](LICENSE) 开源。
- 本项目仅供学习交流与个人研究使用，Antigravity 商标及相关产品权利均归 Google 及其关联公司所有。
