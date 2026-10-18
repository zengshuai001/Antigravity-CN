import os
import sys
import re
import argparse
def to_single_quoted(value):
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def apply_safe_literal_replacement(content, original_literal, translated_literal):
    source_value = original_literal[1:-1]
    target_value = translated_literal[1:-1]

    before = content
    content = content.replace(repr(source_value).replace('"', "'"), to_single_quoted(target_value))
    content = content.replace(f'"{source_value}"', f'"{target_value}"')
    content = content.replace(to_single_quoted(source_value), to_single_quoted(target_value))
    content = content.replace('"' + source_value.replace("\\", "\\\\").replace('"', '\\"') + '"',
                              '"' + target_value.replace("\\", "\\\\").replace('"', '\\"') + '"')
    return content, content != before

def main():
    print("=== Antigravity 2.0 UI Translator ===")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=os.environ.get("AGY_UI_MAIN_SOURCE", ""),
        help="Path to the extracted Antigravity UI main bundle.",
    )
    args = parser.parse_args()
    
    # Paths
    input_file = args.input
    
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("Error: APPDATA environment variable not found.")
        sys.exit(1)
        
    output_dir = os.path.join(appdata, "Antigravity")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "zh_cn_ui_main.js")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        sys.exit(1)
        
    print(f"Reading from: {input_file}")
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Define string translation mapping
    # Note: We must be very precise to match JSON property keys, arrays, or JSX definitions
    translations = {
        # Navigation / Sidebars
        'label:"New Conversation"': 'label:"新建对话"',
        'label:"Create Project"': 'label:"创建项目"',
        'label:"Command Palette"': 'label:"命令面板"',
        'label:"Toggle Fullscreen"': 'label:"切换全屏"',
        'label:"Zoom In"': 'label:"放大"',
        'label:"Zoom Out"': 'label:"缩小"',
        'label:"Reset Zoom"': 'label:"重置缩放"',
        'label:"Toggle Developer Tools"': 'label:"开发者工具"',
        'label:"Minimize"': 'label:"最小化"',
        'label:"Maximize"': 'label:"最大化"',
        'label:"Close"': 'label:"关闭"',
        'label:"About"': 'label:"关于"',
        'label:"Check for Updates"': 'label:"检查更新"',
        
        'title:"File"': 'title:"文件"',
        'title:"View"': 'title:"视图"',
        'title:"Window"': 'title:"窗口"',
        
        # Sidebar section labels
        '"New Conversation"': '"新建对话"',
        '"Scheduled Tasks"': '"计划任务"',
        '"Conversation History"': '"历史对话"',
        '"Projects"': '"项目"',
        '"No conversations yet"': '"暂无历史对话"',
        '"Settings"': '"设置"',
        
        # Chat input placeholder
        '"Ask anything, @ to mention"': '"问任何问题，输入 @ 提及"',
        '", / for actions"': '"，输入 / 执行操作"',
        'aria-label:"Message input"': 'aria-label:"消息输入框"',
        
        # Settings Screens
        '"Project General"': '"项目常规"',
        '"Project Folders"': '"项目文件夹"',
        '"Project Agent"': '"项目智能体"',
        '"Account"': '"账户"',
        '"Google Drive"': '"谷歌云端硬盘"',
        '"General"': '"通用"',
        '"Appearance"': '"外观"',
        '"Chat Settings"': '"聊天设置"',
        '"Verbose agent chat"': '"详细智能体对话"',
        '"Display and preserve intermediate thinking steps"': '"显示并保留中间思考步骤"',
        '"Configure the agent\'s visual theme and display preferences."': '"配置智能体的视觉主题和显示偏好。"',
        '"Select light, dark, or inherit system settings."': '"选择浅色、深色或跟随系统设置。"',
        '"Light Theme"': '"浅色主题"',
        '"Dark Theme"': '"深色主题"',
        '"Preset"': '"预设"',
        '"Default Light"': '"默认浅色"',
        '"Default Dark"': '"默认深色"',
        '"Background"': '"背景"',
        '"Foreground"': '"前景"',
        '"Accent"': '"强调色"',
        '"Models"': '"模型"',
        '"Customizations"': '"自定义"',
        '"Browser"': '"浏览器"',
        '"App"': '"应用"',
        '"Account"': '"账户"',
        '"Permissions"': '"权限"',
        '"Notifications"': '"通知"',
        '"Editor"': '"编辑器"',
        '"Tab"': '"Tab"',
        '"Best of N"': '"Best of N"',
        '"Browser Settings"': '"浏览器设置"',
        '"App Settings"': '"应用设置"',
        '"Manage application settings."': '"管理应用设置。"',
        '"Configure settings for Best of N mode."': '"配置 Best of N 模式的相关设置。"',
        '"Best of N Settings"': '"Best of N 设置"',
        '"Shortcuts"': '"快捷键"',
        '"Provide Feedback"': '"提供反馈"',
        '"Notification Settings"': '"通知设置"',
        '"Open System Preferences"': '"打开系统设置"',
        '"Keyboard shortcuts for quick navigation and control."': '"用于快速导航和控制的键盘快捷键。"',
        '"RECOMMENDED"': '"推荐"',
        '"Open Conversation Picker"': '"打开对话选择器"',
        '"Open File Search"': '"打开文件搜索"',
        '"Focus Input"': '"聚焦输入框"',
        '"Go Back"': '"返回"',
        '"Go Forward"': '"前进"',
        '"File Picker"': '"文件选择器"',
        '"Select Previous Conversation"': '"选择上一个对话"',
        '"Select Next Conversation"': '"选择下一个对话"',
        '"CONVERSATION"': '"对话"',
        '"LAYOUT CONTROLS"': '"布局控制"',
        '"Toggle Model Selector"': '"切换模型选择器"',
        '"Toggle Voice Recording"': '"切换语音录制"',
        '"Find in Pane"': '"在面板中查找"',
        '"Toggle Sidebar"': '"切换侧边栏"',
        '"Toggle Auxiliary Pane"': '"切换辅助面板"',
        '"Enable Telemetry"': '"启用遥测"',
        '"Marketing Emails"': '"营销邮件"',
        '"Your Plan:"': '"当前套餐："',
        '"Upgrade"': '"升级"',
        '"Sign Out"': '"退出登录"',
        '"Email"': '"邮箱"',
        '"Terms of Service"': '"服务条款"',
        '"Projects"': '"项目"',
        '"Conversations"': '"对话"',
        '"Not in Project"': '"未归属项目"',
        '"Workspaces"': '"工作区"',
        '"Show all"': '"显示全部"',
        '"Theme"': '"主题"',
        '"Keyboard Shortcuts"': '"快捷键"',
        '"Permissions"': '"权限"',
        '"No project selected or project management not available."': '"未选择项目，或项目管理不可用。"',
        '"Open Settings"': '"打开设置"',
        '"Open Keyboard Shortcuts"': '"打开快捷键列表"',
        '"No agents running"': '"当前没有运行中的智能体"',
        '"Folders"': '"文件夹"',
        '"Add Folder"': '"添加文件夹"',
        '"Agent Settings"': '"智能体设置"',
        '"Security Preset"': '"安全预设"',
        '"Unrestricted"': '"无限制"',
        '"Agent Behavior"': '"智能体行为"',
        '"Artifact Review Policy"': '"产物评审策略"',
        '"Local Permissions"': '"本地权限"',
        '"File Access Rules"': '"文件访问规则"',
        '"Network Access Rules"': '"网络访问规则"',
        '"MCP Tools"': '"MCP 工具"',
        '"Danger Zone"': '"危险区域"',
        '"Delete Project"': '"删除项目"',
        '"Open"': '"打开"',
        '"Learn more about Unrestricted"': '"了解更多关于“无限制”"',
        '"Learn more about "': '"了解更多关于 "',
        '"Rules"': '"规则"',
        '"Show 1 breakdown"': '"显示 1 项明细"',
        '"Terminal Commands"': '"终端命令"',
        '"Commands Outside Sandbox"': '"沙箱外命令"',
        '"Global"': '"全局"',
        '"File Reads"': '"文件读取"',
        '"File Writes"': '"文件写入"',
        '"Read URLs"': '"读取 URL"',
        '"Skills"': '"技能"',
        '"Custom"': '"自定义"',
        '"Hide breakdown"': '"隐藏明细"',
        '"No customizations found for this workspace."': '"当前工作区未找到任何自定义内容。"',
        '"Learn more about Unrestricted"': '"了解更多关于无限制"',
        '"user_global"': '"用户全局"',
        '"Suggestions"': '"建议"',
        '"Navigation"': '"导航"',
        '"Context"': '"上下文"',
        '"Advanced"': '"高级"',
        '"Quota"': '"配额"',
        '"Default Customizations"': '"默认自定义"',
        '"Customize Global Skills"': '"自定义全局技能"',
        '"Custom Agents"': '"自定义智能体"',
        '"MCP Servers"': '"MCP 服务器"',
        '"Actuation Permissions"': '"执行权限"',
        '"Browser Actuation Rules"': '"浏览器执行规则"',
        '"Configure allowed and denied URLs for browser actuation."': '"配置浏览器执行时允许和拒绝的 URL。"',
        '"Edit"': '"编辑"',
        '"Add"': '"添加"',
        '"Delete command"': '"删除命令"',
        '"Remove"': '"移除"',
        '"Cancel"': '"取消"',

        # Settings labels / descriptions
        '"Allow List Terminal Commands"': '"允许列表终端命令"',
        '"Deny List Terminal Commands"': '"拒绝列表终端命令"',
        '"Agent Auto-Fix Lints"': '"智能体自动修复 Lint"',
        '"Enable Workspace API"': '"启用 Workspace API"',
        '"Confirm Window Reload"': '"确认窗口重载"',
        '"Enable Demo Mode (Beta)"': '"启用演示模式（Beta）"',
        '"Explain and Fix in Current Conversation"': '"在当前对话中解释并修复"',
        '"Strict Mode"': '"严格模式"',
        '"Agent Non-Workspace File Access"': '"智能体访问工作区外文件"',
        '"Enable Terminal Sandbox"': '"启用终端沙箱"',
        '"Sandbox Allow Network"': '"沙箱允许网络"',
        '"Enable Shell Integration"': '"启用 Shell 集成"',
        '"Terminal Command Auto Execution"': '"终端命令自动执行"',
        '"Agent Host Address"': '"智能体主机地址"',
        '"Review Policy"': '"评审策略"',
        '"Enable Sounds for Agent"': '"为智能体启用提示音"',
        '"Auto-Expand Changes Overview"': '"自动展开变更概览"',
        '"Conversation History"': '"历史对话"',
        '"Knowledge"': '"知识库"',
        '"Auto-Open Edited Files"': '"自动打开已编辑文件"',
        '"Open Agent on Reload"': '"重载时打开智能体"',
        '"Suggestions in Editor"': '"编辑器内建议"',
        '"Tab to Jump"': '"Tab 跳转"',
        '"Tab to Import"': '"Tab 导入"',
        '"Tab Speed"': '"Tab 速度"',
        '"Highlight After Accept"': '"接受后高亮"',
        '"Tab Gitignore Access"': '"Tab 访问 .gitignore"',
        '"Browser Javascript Execution Policy"': '"浏览器 JavaScript 执行策略"',
        '"Chrome Binary Path"': '"Chrome 可执行文件路径"',
        '"Browser User Profile Path"': '"浏览器用户配置路径"',
        '"Browser CDP Port"': '"浏览器 CDP 端口"',
        '"Show Selection Actions"': '"显示选区操作"',
        '"Include Jetski Default Customizations"': '"包含 Jetski 默认自定义"',
        '"Prevent Sleep"': '"防止休眠"',
        '"Keep In Menu Bar"': '"保持在菜单栏中"',
        '"Enable Remote Control"': '"启用远程控制"',
        '"Disabled"': '"禁用"',
        '"Request Review"': '"请求评审"',
        '"Always Proceed"': '"始终继续"',
        '"Proceed in Sandbox"': '"在沙箱中继续"',
        '"Fast"': '"快速"',
        '"Slow"': '"慢速"',
        '"Terminal"': '"终端"',
        '"File Access"': '"文件访问"',
        '"Automation"': '"自动化"',
        '"History"': '"历史"',
        '"Sandboxed"': '"沙箱模式"',
        '"Strict"': '"严格模式"',
        '"Enabled"': '"已启用"',
        '"Value:"': '"值："',

        # Settings descriptions
        '"When enabled, Agent can interact with Google Workspace through the API to search and read documents."': '"启用后，智能体可以通过 API 与 Google Workspace 交互，搜索并读取文档。"',
        '"Toggle if a confirmation is shown when using the "Reload Window" button."': '"控制使用“重载窗口”按钮时是否显示确认提示。"',
        '"When enabled, "Explain and Fix" actions will continue in the current conversation instead of starting a new one."': '"启用后，“解释并修复”操作会在当前对话中继续，而不是新建对话。"',
        '"When enabled, terminal commands run with sandbox restrictions."': '"启用后，终端命令将在沙箱限制下运行。"',
        '"When enabled, sandboxed commands are allowed to make network requests."': '"启用后，沙箱中的命令可以发起网络请求。"',
        '"When enabled, Agent will use IDE\'s shell integration to detect and report terminal command execution. When disabled, the agent will use its own shell. Restart the application for this to take effect."': '"启用后，智能体会使用 IDE 的 Shell 集成来检测并报告终端命令执行情况。禁用后，智能体将使用自己的 Shell。重新启动应用后生效。"',
        '"When enabled, Agent will use IDE\'s shell integration to detect and report terminal command execution."': '"启用后，智能体会使用 IDE 的 Shell 集成来检测并报告终端命令执行情况。"',
        '"When enabled, Agent is given awareness of lint errors created by its edits and may fix them without explicit user prompting."': '"启用后，智能体会感知自身编辑产生的 Lint 错误，并可在无需明确提示的情况下修复。"',
        '"When enabled, the agent will be able to access past conversations to inform its responses."': '"启用后，智能体可以访问历史对话来辅助生成回复。"',
        '"Open files in the background if Agent creates or edits them"': '"当智能体创建或编辑文件时，在后台自动打开这些文件。"',
        '"To modify notification settings, open your operating system\'s system preferences."': '"若要修改通知设置，请打开操作系统的系统设置。"',
        '"Manage your plan, credentials, and general preferences."': '"管理你的套餐、凭据和通用偏好设置。"',
        '"When toggled on, Antigravity collects usage data to help Google enhance performance and features."': '"开启后，Antigravity 会收集使用数据，以帮助 Google 改进性能和功能。"',
        '"Receive product updates, tips, and promotions from Google Antigravity via email."': '"通过电子邮件接收来自 Google Antigravity 的产品更新、技巧和推广信息。"',
        '"You can upgrade to a Google AI Ultra plan to receive the highest rate limits."': '"你可以升级到 Google AI Ultra 套餐，以获得最高的速率限制。"',
        '"By using this app, you agree to its"': '"使用此应用即表示你同意其"',
        '"Open Agent panel on window reload"': '"窗口重载时打开智能体面板。"',
        '"Allows the agent to access files outside of your current workspace."': '"允许智能体访问当前工作区之外的文件。"',
        '"Agent cannot modify files outside of the workspace in strict mode."': '"在严格模式下，智能体无法修改工作区之外的文件。"',
        '"Agent will always ask to review in strict mode."': '"在严格模式下，智能体始终会请求评审。"',
        '"Show suggestions when typing in the editor."': '"在编辑器输入时显示建议。"',
        '"Quickly add and update imports with a tab keypress."': '"通过按下 Tab 键快速添加和更新导入。"',
        '"Set the speed of tab suggestions"': '"设置 Tab 建议的显示速度。"',
        '"Highlight newly inserted text after accepting a Tab completion."': '"接受 Tab 补全后高亮新插入的文本。"',
        '"Controls whether the agent can run custom JavaScript to automate complex browser actions."': '"控制智能体是否可以运行自定义 JavaScript 来自动化复杂的浏览器操作。"',
        '"Path to the Chrome/Chromium executable. Leave empty for auto-detection."': '"Chrome/Chromium 可执行文件路径。留空则自动检测。"',
        '"Custom path for the browser user profile directory. Leave empty for default (~/.gemini/antigravity-browser-profile)."': '"浏览器用户配置目录的自定义路径。留空则使用默认值（~/.gemini/antigravity-browser-profile）。"',
        '"Port number for Chrome DevTools Protocol remote debugging. Leave empty for default (9222)."': '"Chrome DevTools Protocol 远程调试端口。留空则使用默认值（9222）。"',
        '"Show "Edit" and "Chat" buttons when selecting text in the editor."': '"在编辑器中选中文本时显示“编辑”和“聊天”按钮。"',
        '"When enabled, the agent will include default customizations, including default skills."': '"启用后，智能体会包含默认自定义内容，包括默认技能。"',
        '"Prevent the computer from sleeping while the app is running."': '"在应用运行期间阻止计算机进入睡眠。"',
        '"The app will be accessible from the menu bar and will keep running in the background when all windows are closed."': '"应用可从菜单栏访问，并会在所有窗口关闭后继续在后台运行。"',
        '"If enabled, you can manage your conversations from the Antigravity website. Please reload the application to apply this setting."': '"启用后，你可以在 Antigravity 网站上管理对话。请重新加载应用以使设置生效。"',
        '"Configure the browser subagent. It requires"': '"配置浏览器子智能体。它需要"',
        '"to be installed. The browser subagent can be invoked by typing /browser in the conversation input box."': '"已安装。可在对话输入框中输入 /browser 来调用浏览器子智能体。"',
        '"No permissions configured."': '"尚未配置任何权限。"',
        '"Controls whether terminal commands require your approval before running."': '"控制终端命令在执行前是否需要你的批准。"',
        '"Restricts agent tools to a secure, isolated local sandbox."': '"将智能体工具限制在安全、隔离的本地沙箱中。"',
        '"Agents run in a secure sandbox that restricts access to external resources outside of your trusted folders."': '"智能体会在安全沙箱中运行，限制其访问受信任文件夹之外的外部资源。"',
        '"Terminal commands always require review and the agent cannot access files outside of its given workspaces."': '"终端命令始终需要评审，且智能体无法访问其指定工作区之外的文件。"',
        '"Execute URLs"': '"执行 URL"',
        '"Allow/deny agent browser actuation access to specific URLs."': '"允许或拒绝智能体对特定 URL 执行浏览器操作。"',
        '"Allow/deny agent read access to specific files or directories."': '"允许或拒绝智能体读取特定文件或目录。"',
        '"Allow/deny agent write access to specific files or directories."': '"允许或拒绝智能体写入特定文件或目录。"',
        '"Allow/deny agent read access to specific URLs or domains."': '"允许或拒绝智能体读取特定 URL 或域名。"',
        '"Allow/deny specific terminal commands."': '"允许或拒绝特定终端命令。"',
        '"Allow/deny agent command execution outside the sandbox."': '"允许或拒绝智能体在沙箱外执行命令。"',
        '"External tools the agent can call via Model Context Protocol."': '"智能体可通过 Model Context Protocol 调用的外部工具。"',
        '"e.g., /path/to/file"': '"例如：/path/to/file"',
        '"e.g., https://example.com"': '"例如：https://example.com"',
        '"e.g., npm test"': '"例如：npm test"',
        '"e.g., curl"': '"例如：curl"',
        '"Enter tool name or server..."': '"输入工具名称或服务器..."',
        '"Inherits from"': '"继承自"',
        '"global settings"': '"全局设置"',
        '". Local permissions have higher priority."': '"。本地权限具有更高优先级。"',
        '"Learn more about"': '"了解更多关于"',
        '"Manage project folders, agent settings, and permissions."': '"管理项目文件夹、智能体设置和权限。"',
        '"Choose a predefined security preset for the agent. This controls terminal auto-execution policy, and file access policy."': '"为智能体选择预定义的安全预设。它会控制终端自动执行策略和文件访问策略。"',
        '"Specifies Agent\'s behavior when asking for review on artifacts, which are documents it creates to enable a richer conversation experience."': '"指定智能体在请求评审产物时的行为。产物是它为提供更丰富对话体验而创建的文档。"',
        '"Inherits from global settings. Local permissions have higher priority. Learn more."': '"继承全局设置。本地权限具有更高优先级。了解更多。"',
        '"Inherits from global settings. Local permissions have higher priority. "': '"继承全局设置。本地权限具有更高优先级。"',
        '"Learn more."': '"了解更多。"',
        '"Configure allowed and denied paths for file reads and writes."': '"配置文件读写时允许和拒绝的路径。"',
        '"Configure allowed and denied URLs for reading."': '"配置读取时允许和拒绝的 URL。"',
        '"Configure allowed terminal commands."': '"配置允许的终端命令。"',
        '"Configure allowed commands outside the sandbox."': '"配置沙箱外允许执行的命令。"',
        '"Configure external tools via Model Context Protocol."': '"通过 Model Context Protocol 配置外部工具。"',
        '"The breakdown below shows token usage from customizations like skills, rules, and MCP. If the budget is exceeded, large customizations will be truncated automatically."': '"下方明细显示技能、规则、MCP 等自定义内容的 token 使用情况。如果超出预算，较大的自定义内容会被自动截断。"',
        '"of the customization budget is available."': '"的自定义预算仍可用。"',
        '"The customization budget is available."': '"自定义预算仍可用。"',
        '"Permanently delete this project and all of its conversations."': '"永久删除该项目及其所有对话。"',

        # Project Initializer Dialog
        '"Getting started with a Project"': '"项目入门指南"',
        '"Now that you\'ve created a project, configure your project\'s agent settings or start a conversation."': '"项目创建成功！现在可以配置项目智能体设置，或者直接开始对话。"',
        '"Learn more"': '"了解更多"',
        '"Learn More"': '"了解更多"',
        
        # Buttons & Actions
        '"Submit"': '"提交"',
        '"Continue"': '"继续"',
        '"Cancel"': '"取消"',
        '"Quit"': '"退出"',
        '"Approve"': '"批准"',
        '"Reject"': '"拒绝"',
        '"Allow"': '"允许"',
        '"Deny"': '"拒绝"',
        
        # Agent execution statuses
        '"Completed"': '"已完成"',
        '"Task"': '"任务"',
        '"running"': '"运行中"',
        '"Running"': '"运行中"',
        '"completed"': '"已完成"',
        '"Approved"': '"已批准"',
        '"Requested change"': '"请求变更"',
        '"Denied"': '"已拒绝"',
        
        # Header / Status titles
        '"Action Required"': '"需要操作"',
        '"Completed Operations"': '"已完成操作"',
        '"Walkthrough"': '"任务演练"',
        '"Review"': '"评审"',
        '"Wait"': '"等待"',
        'Learn more about ': '了解更多关于 ',
        'Inherits from global settings. Local permissions have higher priority. ': '继承全局设置。本地权限具有更高优先级。',
        'of the customization budget is available.': '的自定义预算仍可用。',
        'Rules\n(1.6%)': '规则\n(1.6%)',
        'Show 1 breakdown': '显示 1 项明细',
        'Learn more about Unrestricted': '了解更多关于无限制',
        'Learn more about 无限制': '了解更多关于无限制',
        'Inherits from global settings. Local permissions have higher priority. 了解更多.': '继承全局设置。本地权限具有更高优先级。了解更多。',
    }
    
    print("Applying translations...")
    replaced_count = 0
    literal_pattern = re.compile(r"""^(["']).*\1$""")

    for original, translated in translations.items():
        replaced = False
        if literal_pattern.match(original) and literal_pattern.match(translated):
            content, replaced = apply_safe_literal_replacement(content, original, translated)
        else:
            if original in content:
                content = content.replace(original, translated)
                replaced = True
            else:
                alt_original = original.replace('"', "'")
                alt_translated = translated.replace('"', "'")
                if alt_original in content:
                    content = content.replace(alt_original, alt_translated)
                    replaced = True

        if replaced:
            replaced_count += 1
            
    print(f"Replaced {replaced_count} of {len(translations)} strings.")
    
    # Save the modified file
    print(f"Writing to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Translation completed successfully!")

if __name__ == "__main__":
    main()
