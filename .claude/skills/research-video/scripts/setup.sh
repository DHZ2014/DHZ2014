#!/usr/bin/env bash
# 检查依赖、下载字体。用法：bash setup.sh [--install]
#   --install  顺带 pip 安装 playwright numpy scipy 并安装 Chromium（电脑端第一次用时加上）
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
if [[ "${1:-}" == "--install" ]]; then
  "$PY" -m pip install --quiet playwright numpy scipy
  "$PY" -m playwright install chromium
fi
ok=1
for c in ffmpeg ffprobe "$PY"; do command -v "$c" >/dev/null || { echo "缺少 $c"; ok=0; }; done
"$PY" -c "import playwright, numpy, scipy" 2>/dev/null || { echo "缺少 Python 包：$PY -m pip install playwright numpy scipy（或 bash setup.sh --install）"; ok=0; }
# 字体：Noto Sans SC / Barlow Condensed / IBM Plex Mono（均为 OFL），本地加载保证每次渲染一致
if [[ ! -f "$SKILL/fonts/fonts.css" ]]; then
  mkdir -p "$SKILL/fonts"
  "$PY" - "$SKILL/fonts" <<'PY'
import re, sys, urllib.request
out = sys.argv[1]
css = urllib.request.urlopen(urllib.request.Request(
    "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&family=IBM+Plex+Mono:wght@500&family=Noto+Sans+SC:wght@700;900&display=swap",
    headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
rules = []
for fam, w, url in re.findall(r"font-family: '([^']+)';.*?font-weight: (\d+);.*?src: url\(([^)]+)\)", css, re.S):
    fn = f"{fam.replace(' ', '')}-{w}.ttf"
    open(f"{out}/{fn}", "wb").write(urllib.request.urlopen(url, timeout=120).read())
    rules.append(f"@font-face {{ font-family: '{fam}'; font-weight: {w}; src: url('{fn}'); }}")
open(f"{out}/fonts.css", "w").write("\n".join(rules) + "\n")
print("字体已下载：", len(rules), "个")
PY
fi
[[ $ok == 1 ]] && echo "环境就绪" || { echo "请先补齐上面缺的依赖"; exit 1; }
