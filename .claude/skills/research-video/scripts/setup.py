"""检查依赖、下载字体（Windows / macOS / Linux 通用）。

用法：python setup.py [--install]
  --install  顺带 pip 安装 playwright numpy scipy 并安装 Chromium（电脑端第一次用时加上）
"""
import re, shutil, subprocess, sys, urllib.request
from common import SKILL

if "--install" in sys.argv:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "playwright", "numpy", "scipy"])
    # 装不上也没关系：渲染器会退回系统里的 Chrome / Edge
    subprocess.call([sys.executable, "-m", "playwright", "install", "chromium"])

ok = True
for c in ("ffmpeg", "ffprobe"):
    if not shutil.which(c):
        print(f"缺少 {c}：Windows 用 winget install Gyan.FFmpeg，macOS 用 brew install ffmpeg，装完重开终端")
        ok = False
try:
    import playwright, numpy, scipy  # noqa: F401
except ImportError as e:
    print(f"缺少 Python 包（{e.name}）：python setup.py --install")
    ok = False

# 字体：Noto Sans SC / Barlow Condensed / IBM Plex Mono（均为 OFL），本地加载保证每次渲染一致
fonts = SKILL / "fonts"
if not (fonts / "fonts.css").exists():
    fonts.mkdir(exist_ok=True)
    css = urllib.request.urlopen(urllib.request.Request(
        "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&family=IBM+Plex+Mono:wght@500&family=Noto+Sans+SC:wght@700;900&display=swap",
        headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
    rules = []
    for fam, w, url in re.findall(r"font-family: '([^']+)';.*?font-weight: (\d+);.*?src: url\(([^)]+)\)", css, re.S):
        fn = f"{fam.replace(' ', '')}-{w}.ttf"
        (fonts / fn).write_bytes(urllib.request.urlopen(url, timeout=120).read())
        rules.append(f"@font-face {{ font-family: '{fam}'; font-weight: {w}; src: url('{fn}'); }}")
    (fonts / "fonts.css").write_text("\n".join(rules) + "\n", encoding="utf-8")
    print("字体已下载：", len(rules), "个")

print("环境就绪" if ok else "请先补齐上面缺的依赖")
sys.exit(0 if ok else 1)
