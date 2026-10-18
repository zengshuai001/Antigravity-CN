import os
import sys
import time
import subprocess


def is_pid_running(pid):
    try:
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}"', shell=True)
        return str(pid) in str(output)
    except Exception:
        return False


def log(msg, log_file):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def main():
    if len(sys.argv) < 4:
        print("Usage: python bg_install.py <parent_pid> <antigravity_path> <project_root> [--enable-ai-ui]")
        sys.exit(1)

    parent_pid = int(sys.argv[1])
    antigravity_path = sys.argv[2]
    project_root = sys.argv[3]
    enable_ai_ui = "--enable-ai-ui" in sys.argv[4:]

    log_file = os.path.join(project_root, "bg_install.log")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("")

    log(f"Starting background installer. Waiting for PID {parent_pid} to exit...", log_file)
    log(f"Antigravity Path: {antigravity_path}", log_file)
    log(f"Project Root: {project_root}", log_file)
    log(f"AI UI patch requested: {enable_ai_ui}", log_file)

    wait_count = 0
    while is_pid_running(parent_pid):
        time.sleep(1.0)
        wait_count += 1
        if wait_count % 10 == 0:
            log(f"Still waiting for PID {parent_pid} to exit (waited {wait_count}s)...", log_file)

    log(f"PID {parent_pid} has exited. Starting localization install...", log_file)
    time.sleep(2.0)

    try:
        apply_script = os.path.join(project_root, "scripts", "apply.ps1")
        command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            apply_script,
            "-AntigravityPath",
            antigravity_path,
            "-NoProcessPrompt",
        ]
        if enable_ai_ui:
            command.append("-EnableAiUi")

        subprocess.check_call(command)
        log("Localization files successfully applied! Relaunching Antigravity...", log_file)

        exe_path = os.path.join(antigravity_path, "Antigravity.exe")
        subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        log("Relaunch command sent successfully.", log_file)

    except Exception as e:
        log(f"CRITICAL ERROR: {str(e)}", log_file)
        import traceback
        log(traceback.format_exc(), log_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
