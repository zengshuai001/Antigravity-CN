#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Antigravity Chinese Localization Automation Tool (auto_localize.py)
Supports both 1.x and 2.0+ architectures (including 2.23.x, 2.24.x+) with zero external dependencies.
"""

import os
import sys
import json
import struct
import hashlib
import shutil
import base64
import argparse
import subprocess
import time
import string

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(SCRIPT_DIR, "zh_cn_dict.json")
INJECT_JS_PATH = os.path.join(SCRIPT_DIR, "ag_zh_inject.js")

# ---------------------------------------------------------------------------
# Path & Environment Detection (Fully Dynamic)
# ---------------------------------------------------------------------------

def detect_install_path(custom_path=None):
    """
    Dynamically detect Antigravity installation path via:
    1. Custom path (--install-dir)
    2. Environment variables: ANTIGRAVITY_PATH, ANTIGRAVITY_DIR
    3. Windows: %LOCALAPPDATA%, %APPDATA%, %ProgramFiles%, %ProgramFiles(x86)%, %ProgramW6432%, dynamic drive scan, running process
    4. macOS: /Applications, ~/Applications, Spotlight (mdfind)
    5. Linux: ~/.local/share, /opt, /usr/share, PATH (which)
    """
    if custom_path:
        cand = os.path.abspath(custom_path)
        if os.path.isdir(cand) or os.path.isfile(cand):
            return cand

    # 1. Environment variable override
    env_path = os.environ.get("ANTIGRAVITY_PATH") or os.environ.get("ANTIGRAVITY_DIR")
    if env_path and (os.path.isdir(env_path) or os.path.isfile(env_path)):
        return os.path.abspath(env_path)

    # 2. Windows dynamic path detection
    if sys.platform == "win32":
        local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
        roaming_app = os.environ.get("APPDATA") or os.path.expanduser(r"~\AppData\Roaming")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        program_w6432 = os.environ.get("ProgramW6432")

        candidates = [
            os.path.join(local_app, "Programs", "Antigravity"),
            os.path.join(local_app, "Programs", "antigravity"),
            os.path.join(roaming_app, "Programs", "Antigravity"),
            os.path.join(program_files, "Antigravity"),
            os.path.join(program_files_x86, "Antigravity"),
        ]
        if program_w6432:
            candidates.append(os.path.join(program_w6432, "Antigravity"))

        # Check running process executable location
        try:
            cmd = ['powershell', '-NoProfile', '-Command',
                   "(Get-Process Antigravity -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path -First 1)"]
            proc_out = subprocess.run(cmd, capture_output=True, text=True, timeout=3).stdout.strip()
            if proc_out and os.path.exists(proc_out):
                candidates.insert(0, os.path.dirname(proc_out))
        except Exception:
            pass

        # Dynamically scan all available drive roots for custom installations
        for letter in string.ascii_uppercase:
            drive_root = f"{letter}:\\"
            if os.path.exists(drive_root):
                candidates.extend([
                    os.path.join(drive_root, "Antigravity"),
                    os.path.join(drive_root, "Program Files", "Antigravity"),
                    os.path.join(drive_root, "Programs", "Antigravity"),
                ])

        for c in candidates:
            if c and os.path.exists(c):
                return c

    # 3. macOS dynamic path detection
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/Antigravity.app",
            os.path.expanduser("~/Applications/Antigravity.app"),
            "/Applications/Google Antigravity.app",
            os.path.expanduser("~/Applications/Google Antigravity.app")
        ]
        try:
            mdfind_out = subprocess.run(["mdfind", "kMDItemFSName == 'Antigravity.app'"],
                                        capture_output=True, text=True, timeout=3).stdout.strip()
            if mdfind_out:
                for line in mdfind_out.splitlines():
                    p = line.strip()
                    if p and os.path.exists(p):
                        candidates.insert(0, p)
        except Exception:
            pass

        for c in candidates:
            if os.path.exists(c):
                return c

    # 4. Linux dynamic path detection
    elif sys.platform.startswith("linux"):
        candidates = [
            os.path.expanduser("~/.local/share/antigravity"),
            "/opt/Antigravity",
            "/opt/antigravity",
            "/usr/share/antigravity"
        ]
        try:
            which_out = shutil.which("antigravity")
            if which_out:
                candidates.insert(0, os.path.dirname(os.path.realpath(which_out)))
        except Exception:
            pass

        for c in candidates:
            if os.path.exists(c):
                return c

    return None

def detect_architecture(install_path):
    """
    Detect architecture version:
      - '1.x': uses unpacked resources/app/out/.../workbench.html and product.json
      - '2.0+': uses resources/app.asar
    """
    if not install_path:
        return 'unknown', None

    base_dir = install_path
    if os.path.isfile(install_path):
        base_dir = os.path.dirname(install_path)

    if sys.platform == 'darwin' and base_dir.endswith('.app'):
        resources_dir = os.path.join(base_dir, 'Contents', 'Resources')
    else:
        resources_dir = os.path.join(base_dir, 'resources')

    asar_path = os.path.join(resources_dir, 'app.asar')
    if os.path.exists(asar_path):
        return '2.0+', {
            'type': '2.0+',
            'install_dir': base_dir,
            'resources_dir': resources_dir,
            'asar_path': asar_path,
            'asar_bak': asar_path + '.bak'
        }

    v1_paths = [
        os.path.join(resources_dir, 'app', 'out', 'vs', 'code', 'electron-browser', 'workbench', 'workbench.html'),
        os.path.join(resources_dir, 'app', 'out', 'vs', 'code', 'electron-browser', 'workbench', 'workbench-jetski-agent.html')
    ]
    for p in v1_paths:
        if os.path.exists(p):
            product_json = os.path.join(resources_dir, 'app', 'product.json')
            return '1.x', {
                'type': '1.x',
                'install_dir': base_dir,
                'resources_dir': resources_dir,
                'workbench_html': p,
                'workbench_bak': p + '.bak',
                'product_json': product_json,
                'product_bak': product_json + '.bak'
            }

    return 'unknown', {'install_dir': base_dir, 'resources_dir': resources_dir}

# ---------------------------------------------------------------------------
# Pure Python ASAR Processing
# ---------------------------------------------------------------------------

def read_asar(asar_path):
    with open(asar_path, 'rb') as f:
        h = f.read(16)
        size1, size2, size3, size4 = struct.unpack('<IIII', h)
        header_json_bytes = f.read(size4)
        base_offset = 8 + size2
        header = json.loads(header_json_bytes.decode('utf-8'))
        
        files_data = {}
        def extract_files(path, node):
            if 'files' in node:
                for name, subnode in node['files'].items():
                    subpath = f"{path}/{name}" if path else name
                    extract_files(subpath, subnode)
            else:
                if not node.get('unpacked') and 'offset' in node:
                    offset = int(node['offset'])
                    size = node['size']
                    f.seek(base_offset + offset)
                    files_data[path] = f.read(size)
        
        extract_files('', header)
        return header, files_data

def safe_replace_file(src_tmp, dst_file, max_retries=15, delay=0.6):
    for attempt in range(max_retries):
        try:
            if os.path.exists(dst_file):
                os.remove(dst_file)
            os.rename(src_tmp, dst_file)
            return True
        except (PermissionError, OSError):
            time.sleep(delay)
    
    # Fallback to copy and remove
    try:
        shutil.copy2(src_tmp, dst_file)
        os.remove(src_tmp)
        return True
    except Exception as e:
        raise PermissionError(f"无法替换目标文件 {dst_file}，文件可能被系统占用: {e}")

def pack_asar(header_template, files_data, output_asar_path):
    new_header = json.loads(json.dumps(header_template))
    current_offset = 0
    concatenated_data = bytearray()
    
    def update_offsets(path, node):
        nonlocal current_offset
        if 'files' in node:
            for name, subnode in node['files'].items():
                subpath = f"{path}/{name}" if path else name
                update_offsets(subpath, subnode)
        else:
            if not node.get('unpacked') and path in files_data:
                data = files_data[path]
                node['offset'] = str(current_offset)
                node['size'] = len(data)
                
                sha = hashlib.sha256(data).hexdigest()
                node['integrity'] = {
                    'algorithm': 'SHA256',
                    'hash': sha,
                    'blockSize': 4194304,
                    'blocks': [sha]
                }
                
                concatenated_data.extend(data)
                current_offset += len(data)

    update_offsets('', new_header)
    header_json = json.dumps(new_header, separators=(',', ':')).encode('utf-8')
    header_len = len(header_json)
    
    pad = (4 - (header_len % 4)) % 4
    header_json_padded = header_json + (b'\x00' * pad)
    
    size4 = header_len
    size3 = 4 + len(header_json_padded)
    size2 = 4 + size3
    size1 = 4
    
    pickle_header = struct.pack('<IIII', size1, size2, size3, size4)
    
    tmp_path = output_asar_path + ".tmp"
    with open(tmp_path, 'wb') as out_f:
        out_f.write(pickle_header)
        out_f.write(header_json_padded)
        out_f.write(concatenated_data)

    safe_replace_file(tmp_path, output_asar_path)

# ---------------------------------------------------------------------------
# Payload Generator
# ---------------------------------------------------------------------------

def generate_injection_payload():
    dict_content = {}
    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, 'r', encoding='utf-8') as f:
            dict_content = json.load(f)
    
    js_engine = ""
    if os.path.exists(INJECT_JS_PATH):
        with open(INJECT_JS_PATH, 'r', encoding='utf-8') as f:
            js_engine = f.read()

    dict_json = json.dumps(dict_content, ensure_ascii=False)
    
    payload = f"""
// [AGY-ZH] Antigravity Chinese Localization Injection v2.0
(() => {{
    window.__AG_ZH_DICT__ = {dict_json};
    {js_engine}
}})();
"""
    return payload

# ---------------------------------------------------------------------------
# Version Check & Compatibility Guard
# ---------------------------------------------------------------------------

MAX_TESTED_VERSION = "2.24.x"
MAX_SUPPORTED_TUPLE = (2, 24, 99)

def get_antigravity_version(install_path):
    """
    Extract installed Antigravity version.
    Returns (version_str, version_tuple).
    """
    try:
        if sys.platform == "win32":
            exe = os.path.join(install_path, "Antigravity.exe") if os.path.isdir(install_path) else install_path
            if os.path.exists(exe):
                cmd = ['powershell', '-NoProfile', '-Command', f'(Get-Item -LiteralPath "{exe}").VersionInfo.FileVersion']
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
                if out:
                    parts = []
                    for seg in out.split('.'):
                        if seg.isdigit():
                            parts.append(int(seg))
                    if parts:
                        return out, tuple(parts)
        elif sys.platform == "darwin":
            base_dir = install_path
            if base_dir.endswith('.app'):
                plist_path = os.path.join(base_dir, 'Contents', 'Info.plist')
                if os.path.exists(plist_path):
                    cmd = ['defaults', 'read', plist_path, 'CFBundleShortVersionString']
                    out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
                    if out:
                        parts = [int(p) for p in out.split('.') if p.isdigit()]
                        return out, tuple(parts)
    except Exception:
        pass
    return "未知", (0, 0, 0)

def verify_version_compatibility(install_path, force=False):
    """
    Check if the installed software version exceeds the tested compatible version.
    Prompts with GUI dialog / console warning if version mismatch.
    Returns True to proceed, False to abort.
    """
    if force:
        return True

    ver_str, ver_tuple = get_antigravity_version(install_path)
    if ver_tuple == (0, 0, 0):
        return True

    if ver_tuple > MAX_SUPPORTED_TUPLE:
        msg = (
            f"【版本不匹配安全预警】\n\n"
            f"检测到您当前的 Antigravity 软件版本为 [{ver_str}]，\n"
            f"高于本汉化包目前经过适配与验证的最高版本 [{MAX_TESTED_VERSION}]。\n\n"
            f"由于官方更新可能变更了前端底层结构或启动机制，\n"
            f"强行汉化可能导致界面异常或白屏！\n\n"
            f"是否仍要强行继续汉化？\n"
            f"(点击【确定】继续尝试，注入前会自动备份；点击【取消】安全退出)"
        )
        print("\n" + "!" * 65)
        print(f"[!] 警告：软件版本 [{ver_str}] 高于汉化包已适配版本 [{MAX_TESTED_VERSION}]！")
        print("[!] 官方新版本的底层变动可能会导致界面异常或白屏。")
        print("!" * 65 + "\n")

        # Windows GUI Dialog (MessageBox)
        if sys.platform == "win32":
            try:
                import ctypes
                MB_OKCANCEL = 0x01
                MB_ICONWARNING = 0x30
                IDOK = 1
                result = ctypes.windll.user32.MessageBoxW(0, msg, "Antigravity 汉化版本兼容性提示", MB_OKCANCEL | MB_ICONWARNING)
                if result != IDOK:
                    print("[-] 用户已取消操作，汉化已安全终止。")
                    return False
                return True
            except Exception:
                pass

        # macOS GUI Dialog
        elif sys.platform == "darwin":
            try:
                osa_cmd = (
                    f'display dialog "{msg}" with title "Antigravity 汉化版本兼容性提示" '
                    'buttons {"取消", "继续"} default button "取消" with icon caution'
                )
                res = subprocess.run(['osascript', '-e', osa_cmd], capture_output=True, text=True)
                if "继续" not in res.stdout:
                    print("[-] 用户已取消操作，汉化已安全终止。")
                    return False
                return True
            except Exception:
                pass

        # Console fallback
        try:
            ans = input("检测到软件版本较高，强行汉化可能导致异常，是否仍要继续？(y/N): ").strip().lower()
            return ans in ['y', 'yes']
        except Exception:
            return False

    return True

# ---------------------------------------------------------------------------
# Localization Handlers
# ---------------------------------------------------------------------------

INJECTION_MARKER = "/* === ANTIGRAVITY_CHINESE_LOCALIZATION_START === */"
INJECTION_MARKER_END = "/* === ANTIGRAVITY_CHINESE_LOCALIZATION_END === */"

def backup_localization(info):
    """
    Safely backup clean original files before any modifications.
    Will never overwrite an existing clean backup.
    """
    arch = info.get('type')
    if arch == '2.0+':
        asar_path = info['asar_path']
        asar_bak = info['asar_bak']
        if not os.path.exists(asar_bak):
            print(f"[*] 正在创建安全备份: {asar_bak}")
            shutil.copy2(asar_path, asar_bak)
            print(f"[+] 原版备份完成！备份文件保存在: {asar_bak}")
            return True
        else:
            print(f"[*] 原版备份已存在，保留初始纯净备份: {asar_bak}")
            return True
    elif arch == '1.x':
        html_path = info['workbench_html']
        html_bak = info['workbench_bak']
        product_json = info['product_json']
        product_bak = info['product_bak']

        if not os.path.exists(html_bak) and os.path.exists(html_path):
            print(f"[*] 备份原始 workbench.html: {html_bak}")
            shutil.copy2(html_path, html_bak)
        else:
            print(f"[*] 原始 workbench.html 备份已存在: {html_bak}")

        if not os.path.exists(product_bak) and os.path.exists(product_json):
            print(f"[*] 备份原始 product.json: {product_bak}")
            shutil.copy2(product_json, product_bak)
        else:
            print(f"[*] 原始 product.json 备份已存在: {product_bak}")

        print("[+] 1.x 原版文件备份检查完成！")
        return True
    return False

def apply_2x_localization(info):
    asar_path = info['asar_path']
    print(f"[*] 目标 ASAR: {asar_path}")

    # Step 1: Backup clean version
    backup_localization(info)

    # Step 2: Unpack
    print("[*] 读取并解析 app.asar ...")
    header, files_data = read_asar(asar_path)

    # Step 3: Modify dist/preload.js
    preload_key = "dist/preload.js"
    if preload_key not in files_data:
        raise RuntimeError(f"在 asar 归档中未找到 {preload_key}")

    preload_js = files_data[preload_key].decode('utf-8', errors='ignore')

    # Remove existing injection if present
    if INJECTION_MARKER in preload_js:
        print("[*] 清除旧版注入代码...")
        start_idx = preload_js.find(INJECTION_MARKER)
        end_idx = preload_js.find(INJECTION_MARKER_END) + len(INJECTION_MARKER_END)
        preload_js = preload_js[:start_idx] + preload_js[end_idx:]

    payload = generate_injection_payload()
    escaped_payload = json.dumps(payload)

    # Dual-context injection:
    # 1. Runs directly in Preload context (CSP-safe, immediate, shares DOM)
    # 2. Also injects into Main World (Shadow DOM hook, webFrame execution)
    injection_code = f"""
{INJECTION_MARKER}
try {{
    const __agy_zh_code = {escaped_payload};
    
    // Direct DOM observer execution in Preload context (shares the same DOM)
    try {{
        if (typeof window !== 'undefined') {{
            const runInPreload = () => {{
                try {{
                    const fn = new Function(__agy_zh_code);
                    fn();
                }} catch (e) {{}}
            }};
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', runInPreload, {{ once: true }});
            }} else {{
                runInPreload();
            }}
        }}
    }} catch (e) {{}}

    // Main World injection via script element and webFrame
    const __agy_zh_inject_main = () => {{
        try {{
            if (typeof window !== 'undefined' && document) {{
                const s = document.createElement('script');
                s.textContent = __agy_zh_code;
                (document.head || document.documentElement).appendChild(s);
                s.remove();
            }}
        }} catch (e) {{}}
        try {{
            const {{ webFrame }} = require('electron');
            if (webFrame && typeof webFrame.executeJavaScript === 'function') {{
                webFrame.executeJavaScript(__agy_zh_code);
            }}
        }} catch (e) {{}}
    }};

    if (typeof document !== 'undefined') {{
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', __agy_zh_inject_main, {{ once: true }});
        }} else {{
            __agy_zh_inject_main();
        }}
    }}
}} catch (err) {{
    console.error('[AGY-ZH] Preload injection error:', err);
}}
{INJECTION_MARKER_END}
"""

    new_preload_js = preload_js.strip() + "\n\n" + injection_code
    files_data[preload_key] = new_preload_js.encode('utf-8')

    # Step 4: Repack asar
    print("[*] 重新打包 app.asar 并生成 SHA256 完整性校验...")
    pack_asar(header, files_data, asar_path)
    print("[+] 汉化注入成功！Antigravity 启动时将自动加载全套中文界面。")
    return True

def restore_2x_localization(info):
    asar_path = info['asar_path']
    asar_bak = info['asar_bak']

    if not os.path.exists(asar_bak):
        print(f"[-] 备份文件不存在: {asar_bak}，无法执行回滚。")
        return False

    print(f"[*] 正在从原始备份恢复: {asar_bak} -> {asar_path}")
    safe_replace_file(asar_bak, asar_path)
    print("[+] 回滚成功！Antigravity 已恢复为官方原版英文状态。")
    return True

def apply_1x_localization(info):
    html_path = info['workbench_html']
    product_json = info['product_json']

    print(f"[*] 目标 1.x 界面文件: {html_path}")

    # Ensure clean backup exists
    backup_localization(info)

    target_dir = os.path.dirname(html_path)
    target_js = os.path.join(target_dir, "ag_zh_inject.js")
    
    payload = generate_injection_payload()
    with open(target_js, 'w', encoding='utf-8') as f:
        f.write(payload)

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    script_tag = '<script src="./ag_zh_inject.js"></script>'
    if script_tag not in html_content:
        print("[*] 向 HTML 注入汉化引导标签...")
        if '</html>' in html_content:
            html_content = html_content.replace('</html>', f'{script_tag}\n</html>')
        else:
            html_content += f"\n{script_tag}\n"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    if os.path.exists(product_json):
        print("[*] 计算新文件哈希并同步 product.json 校验值...")
        with open(html_path, 'rb') as f:
            h_data = f.read()
        sha256_b64 = base64.b64encode(hashlib.sha256(h_data).digest()).decode('utf-8')
        md5_b64 = base64.b64encode(hashlib.md5(h_data).digest()).decode('utf-8')

        with open(product_json, 'r', encoding='utf-8') as f:
            prod_data = json.load(f)

        if 'checksums' in prod_data:
            rel_path = os.path.relpath(html_path, os.path.dirname(product_json)).replace('\\', '/')
            for k in prod_data['checksums']:
                if k.endswith('workbench.html') or k == rel_path:
                    curr = prod_data['checksums'][k]
                    if len(curr) > 30:
                        prod_data['checksums'][k] = sha256_b64
                    else:
                        prod_data['checksums'][k] = md5_b64

            with open(product_json, 'w', encoding='utf-8') as f:
                json.dump(prod_data, f, indent=2)
            print("[+] product.json 校验和已同步，消除客户端受损警告。")

    print("[+] 1.x 汉化注入成功！")
    return True

def restore_1x_localization(info):
    html_path = info['workbench_html']
    html_bak = info['workbench_bak']
    product_json = info['product_json']
    product_bak = info['product_bak']

    if os.path.exists(html_bak):
        print(f"[*] 恢复 workbench.html: {html_bak} -> {html_path}")
        shutil.copy2(html_bak, html_path)
    if os.path.exists(product_bak):
        print(f"[*] 恢复 product.json: {product_bak} -> {product_json}")
        shutil.copy2(product_bak, product_json)

    target_js = os.path.join(os.path.dirname(html_path), "ag_zh_inject.js")
    if os.path.exists(target_js):
        os.remove(target_js)

    print("[+] 1.x 回滚完成，已恢复官方原版。")
    return True

# ---------------------------------------------------------------------------
# Process Control
# ---------------------------------------------------------------------------

def check_process_running():
    try:
        if sys.platform == "win32":
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Antigravity.exe"],
                capture_output=True, text=True, timeout=5
            ).stdout or ""
            return "antigravity.exe" in out.lower()
        elif sys.platform == "darwin":
            return subprocess.run(
                ["pgrep", "-x", "Antigravity"],
                capture_output=True, timeout=5
            ).returncode == 0
    except Exception:
        pass
    return False

def kill_antigravity():
    print("[*] 正在关闭 Antigravity 进程以释放文件锁定...")
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", "Antigravity.exe", "/T"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "language_server.exe", "/T"], capture_output=True)
    elif sys.platform == "darwin":
        subprocess.run(["killall", "Antigravity"], capture_output=True)
    
    # Wait until all Antigravity processes have exited
    for _ in range(12):
        if not check_process_running():
            break
        time.sleep(0.5)
    time.sleep(1)
    print("[+] Antigravity 进程已完全退出。")

def launch_antigravity(install_path):
    print("[*] 正在启动 Antigravity...")
    try:
        if sys.platform == "win32":
            exe = os.path.join(install_path, "Antigravity.exe") if os.path.isdir(install_path) else install_path
            if not os.path.exists(exe):
                exe = "Antigravity.exe"
            subprocess.Popen([exe], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            print("[+] 已为您重新启动 Antigravity！")
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Antigravity"])
            print("[+] 已为您重新启动 Antigravity！")
    except Exception as e:
        print(f"[!] 启动失败: {e}，请手动点击快捷方式打开 Antigravity。")

# ---------------------------------------------------------------------------
# Interactive Menu
# ---------------------------------------------------------------------------

def interactive_menu(install_path, arch, info):
    while True:
        ver_str, _ = get_antigravity_version(install_path)
        print("\n" + "=" * 60)
        print("     Google Antigravity 界面中文本地化工具 (通用开源版)")
        print("=" * 60)
        print(f"安装路径: {install_path}")
        print(f"架构版本: {arch}")
        print(f"软件版本: {ver_str} (汉化包适配测试: <= {MAX_TESTED_VERSION})")

        is_running = check_process_running()
        print(f"运行状态: {'【运行中 - 文件已锁定】' if is_running else '【已完全退出 - 文件可用】'}")

        is_injected = False
        has_bak = False
        if arch == '2.0+':
            has_bak = os.path.exists(info['asar_bak'])
            try:
                _, f_data = read_asar(info['asar_path'])
                preload = f_data.get('dist/preload.js', b'').decode('utf-8', errors='ignore')
                is_injected = INJECTION_MARKER in preload
            except Exception:
                pass
        elif arch == '1.x':
            has_bak = os.path.exists(info['workbench_bak'])
            try:
                with open(info['workbench_html'], 'r', encoding='utf-8') as f:
                    is_injected = 'ag_zh_inject.js' in f.read()
            except Exception:
                pass

        print(f"原版备份: {'【已安全备份】' if has_bak else '【未备份（将在首次汉化时自动创建）】'}")
        print(f"汉化状态: {'【已汉化】' if is_injected else '【官方原版英文】'}")
        print("-" * 60)
        print("请选择操作：")
        print("  [1] 一键执行中文汉化注入（若运行中将自动关闭并重启，自动备份）")
        print("  [2] 一键还原回滚为官方原版英文")
        print("  [3] 仅备份官方原版文件")
        print("  [4] 刷新并查看当前状态")
        print("  [5] 退出")
        print("-" * 60)

        try:
            choice = input("请输入选项编号 (默认 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break
        if not choice:
            choice = "1"

        if choice == "1":
            if not verify_version_compatibility(install_path):
                continue
            if check_process_running():
                kill_antigravity()
            try:
                if arch == '2.0+':
                    apply_2x_localization(info)
                else:
                    apply_1x_localization(info)
                
                print("\n========================================================")
                print("  [SUCCESS] 恭喜！Antigravity 界面中文本地化注入成功！")
                print("========================================================")
                try:
                    ask_restart = input("是否立即重新启动 Antigravity？(Y/n): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    ask_restart = "y"
                if ask_restart in ['', 'y', 'yes']:
                    launch_antigravity(install_path)
            except Exception as e:
                print(f"[-] 汉化失败: {e}")
            break

        elif choice == "2":
            if check_process_running():
                kill_antigravity()
            if arch == '2.0+':
                restore_2x_localization(info)
            else:
                restore_1x_localization(info)
            try:
                ask_restart = input("是否重新启动 Antigravity 查看英文原版？(Y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                ask_restart = "n"
            if ask_restart in ['', 'y', 'yes']:
                launch_antigravity(install_path)
            break

        elif choice == "3":
            backup_localization(info)
            continue

        elif choice == "4":
            continue

        elif choice == "5":
            print("已退出。")
            break
        else:
            print("[!] 无效选项，请重新输入。")

# ---------------------------------------------------------------------------
# Main Controller
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Google Antigravity 中文本地化（汉化）通用工具")
    parser.add_argument("--install-dir", help="指定 Antigravity 安装根目录")
    parser.add_argument("--apply", action="store_true", help="非交互模式直接执行汉化注入")
    parser.add_argument("--backup", action="store_true", help="仅执行原版文件备份")
    parser.add_argument("--restore", action="store_true", help="一键还原回滚至官方原版英文状态")
    parser.add_argument("--status", action="store_true", help="探测并输出当前环境与汉化状态")
    parser.add_argument("--force", action="store_true", help="即使检测到进程运行或高版本也强行尝试修改")
    args = parser.parse_args()

    install_path = detect_install_path(args.install_dir)
    if not install_path:
        print("[-] 错误: 未能自动检测到 Antigravity 安装路径。")
        print("    请使用 --install-dir <路径> 手动指定，或设置环境变量 ANTIGRAVITY_PATH。")
        sys.exit(1)

    arch, info = detect_architecture(install_path)
    if arch == 'unknown':
        print(f"[-] 错误: 无法识别当前安装目录的文件架构: {install_path}")
        sys.exit(1)

    # Status check
    if args.status:
        ver_str, _ = get_antigravity_version(install_path)
        is_running = check_process_running()
        print(f"[i] 操作系统: {sys.platform}")
        print(f"[i] 安装根目录: {install_path}")
        print(f"[i] 架构版本: {arch}")
        print(f"[i] 软件版本: {ver_str} (汉化包适配测试: <= {MAX_TESTED_VERSION})")
        print(f"[i] 进程运行状态: {'运行中' if is_running else '已退出'}")
        if arch == '2.0+':
            has_bak = os.path.exists(info['asar_bak'])
            print(f"[i] 原版备份状态: {'已备份 (' + info['asar_bak'] + ')' if has_bak else '未备份'}")
            try:
                _, f_data = read_asar(info['asar_path'])
                preload = f_data.get('dist/preload.js', b'').decode('utf-8', errors='ignore')
                is_injected = INJECTION_MARKER in preload
                print(f"[i] 当前汉化状态: {'【已汉化】' if is_injected else '【官方原版英文】'}")
            except Exception as e:
                print(f"[!] 无法读取 asar: {e}")
        elif arch == '1.x':
            has_bak = os.path.exists(info['workbench_bak'])
            print(f"[i] 原版备份状态: {'已备份 (' + info['workbench_bak'] + ')' if has_bak else '未备份'}")
            try:
                with open(info['workbench_html'], 'r', encoding='utf-8') as f:
                    is_injected = 'ag_zh_inject.js' in f.read()
                print(f"[i] 当前汉化状态: {'【已汉化】' if is_injected else '【官方原版英文】'}")
            except Exception as e:
                print(f"[!] 无法读取 html: {e}")
        return

    # Backup only
    if args.backup:
        backup_localization(info)
        return

    # Restore
    if args.restore:
        if check_process_running() and not args.force:
            kill_antigravity()
        if arch == '2.0+':
            restore_2x_localization(info)
        else:
            restore_1x_localization(info)
        return

    # Apply directly
    if args.apply:
        if not verify_version_compatibility(install_path, force=args.force):
            sys.exit(1)
        if check_process_running() and not args.force:
            kill_antigravity()
        if arch == '2.0+':
            apply_2x_localization(info)
        else:
            apply_1x_localization(info)
        return

    # Default interactive menu
    interactive_menu(install_path, arch, info)

if __name__ == "__main__":
    main()
