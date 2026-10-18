#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Creation & Community Topics Publishing Helper
Automatically creates GitHub repo and binds community topics:
antigravity, antigravity-ide, antigravity-tools, antigravity-chinese, antigravity-zh
"""

import os
import sys
import subprocess
import shutil

COMMUNITY_TOPICS = [
    "antigravity",
    "antigravity-ide",
    "antigravity-tools",
    "antigravity-chinese",
    "antigravity-zh",
    "localization"
]

def check_gh():
    gh_cmd = shutil.which("gh")
    if not gh_cmd:
        # Check standard installation path
        cand = r"C:\Program Files\GitHub CLI\gh.exe"
        if os.path.exists(cand):
            return cand
        return None
    return gh_cmd

def check_git():
    git_cmd = shutil.which("git")
    if not git_cmd:
        candidates = [
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files\Git\bin\git.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Git\cmd\git.exe")
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None
    return git_cmd

def main():
    print("=" * 65)
    print("     Google Antigravity 开源仓库创建与社区标签绑定助手")
    print("=" * 65)

    gh_cmd = check_gh()
    if not gh_cmd:
        print("[-] 错误: 未检测到 GitHub CLI (gh)。请先运行 winget install GitHub.cli 进行安装。")
        sys.exit(1)

    # Check login status
    auth_check = subprocess.run([gh_cmd, "auth", "status"], capture_output=True, text=True)
    if auth_check.returncode != 0:
        print("[-] 提示: GitHub CLI 尚未登录，请先运行: gh auth login")
        sys.exit(1)

    # Get logged in username
    user_name = "zengshuai001"
    for line in auth_check.stdout.splitlines() + auth_check.stderr.splitlines():
        if "Logged in to" in line and "account" in line:
            parts = line.split("account")
            if len(parts) > 1:
                user_name = parts[1].strip().split()[0]
                break

    print(f"[+] 当前登录 GitHub 账号: {user_name}")

    git_cmd = check_git()
    if not git_cmd:
        print("[!] 检测到系统尚未安装 Git。正在通过 winget 为您安装 Git...")
        install_res = subprocess.run(["winget", "install", "--id", "Git.Git", "-e", "--accept-source-agreements", "--accept-package-agreements"])
        git_cmd = check_git()
        if not git_cmd:
            print("[-] 安装完成，请重新打开终端使 PATH 生效后重试。")
            sys.exit(1)

    default_repo_name = "Antigravity-CN"
    try:
        repo_name = input(f"请输入要创建的 GitHub 仓库名称 (默认: {default_repo_name}): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已退出。")
        return
    if not repo_name:
        repo_name = default_repo_name

    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # Init git if not initialized
    if not os.path.exists(os.path.join(root_dir, ".git")):
        print("[*] 正在初始化本地 Git 仓库...")
        subprocess.run([git_cmd, "init", "-b", "main"], check=True)
        subprocess.run([git_cmd, "add", "."], check=True)
        subprocess.run([git_cmd, "commit", "-m", "feat: initial commit for Antigravity Chinese localization"], check=True)

    # Create remote repo
    print(f"[*] 正在 GitHub 创建公开仓库: {user_name}/{repo_name} ...")
    create_args = [
        gh_cmd, "repo", "create", repo_name,
        "--public",
        "--source=.",
        "--remote=origin",
        "--push",
        "--description", "Google Antigravity 界面中文本地化通用版 (支持 1.x 与 2.0+ 架构，一键汉化与还原)"
    ]
    res = subprocess.run(create_args)
    if res.returncode != 0:
        print(f"[!] 提示：创建仓库返回退出码 {res.returncode}，可能仓库已存在。正在尝试直接绑定标签...")

    # Add community topics
    print("[*] 正在绑定社区标签 (Topics):", ", ".join(COMMUNITY_TOPICS))
    target_repo = f"{user_name}/{repo_name}"
    edit_cmd = [gh_cmd, "repo", "edit", target_repo]
    for topic in COMMUNITY_TOPICS:
        edit_cmd.extend(["--add-topic", topic])
    
    topic_res = subprocess.run(edit_cmd, capture_output=True, text=True)
    if topic_res.returncode == 0:
        print(f"[+] 社区标签绑定成功！标签清单: {', '.join(COMMUNITY_TOPICS)}")
    else:
        print(f"[!] 标签添加提示: {topic_res.stderr.strip() or topic_res.stdout.strip()}")

    print("\n" + "=" * 65)
    print("  [SUCCESS] 恭喜！项目已成功发布至 GitHub！")
    print(f"  项目主页: https://github.com/{user_name}/{repo_name}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
