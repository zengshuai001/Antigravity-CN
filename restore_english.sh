#!/usr/bin/env bash
# ================================================================
# Google Antigravity 一键还原原版英文脚本 (macOS / Linux)
# ================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================================================"
echo "          Google Antigravity 一键还原回滚至官方原版英文"
echo "================================================================"
echo ""

PY_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
fi

if [ -z "$PY_CMD" ]; then
    echo "[错误] 未检测到 Python 运行环境！"
    echo "请先在系统中安装 Python 3 后重试。"
    echo ""
    read -n 1 -s -r -p "按任意键退出..."
    echo ""
    exit 1
fi

"$PY_CMD" "$DIR/auto_localize.py" --restore
EXIT_CODE=$?

echo ""
read -n 1 -s -r -p "按任意键退出..."
echo ""
exit $EXIT_CODE
