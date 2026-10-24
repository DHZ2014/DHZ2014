"""研报视频流水线（Windows / macOS / Linux 通用）。用法：python make.py <项目目录> <步骤> [参数]

  lint              花叔 storyboard_lint 检查 镜头表.md（并核对屏上数字是否出现在口播里）
  tts [段号...]      MiniMax 合成旁白（只重做某几段就写段号）
  timing            排时间轴、字幕，生成 out/<项目>.srt
  stills t1 t2 ...  构建并渲染若干静帧，拼成 qa/sheet.png（自检用）
  audio             运行项目里的 mix.py → 标准化到 -14 LUFS → 出波形图
  render            渲染整片 out/<项目>.mp4 并出抽帧图 qa/final-sheet.png
  all               tts → timing → audio → render
"""
import json, os, subprocess, sys
from pathlib import Path
from common import SKILL, load_config

if len(sys.argv) < 3:
    sys.exit(__doc__)
P = Path(sys.argv[1]).resolve(); STEP = sys.argv[2]; ARGS = sys.argv[3:]
S = SKILL / "scripts"; V = S / "vendor"; PY = sys.executable
NAME = P.name; cfg = load_config(P)
# Windows 默认按 GBK 读写文件、打印中文，统一切到 UTF-8
ENV = dict(os.environ, SKILL_DIR=str(SKILL), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
for sub in ("audio", "qa", "out"):
    (P / sub).mkdir(exist_ok=True)


def run(*cmd, cwd=None):
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env=ENV)
    if r.returncode:
        sys.exit(r.returncode)


def step(name, args=()):
    if name == "lint":
        lines = json.loads((P / "vo.json").read_text(encoding="utf-8"))
        (P / "qa" / "文稿.txt").write_text("".join(lines), encoding="utf-8")
        run(PY, V / "huashu" / "storyboard_lint.py", P / "镜头表.md", "--script", P / "qa" / "文稿.txt")
    elif name == "tts":
        run(PY, S / "tts.py", P, *args)
    elif name == "timing":
        run(PY, S / "timing.py", P)
    elif name == "stills":
        run(PY, S / "build.py", P)
        for f in (P / "qa").glob("s_*.png"):
            f.unlink()
        for k, t in enumerate(args):
            run(PY, V / "xilo" / "render.py", P / "index.html", P / "qa" / f"s_{k:02d}.png", "--still", t, "--size", cfg["size"])
        run("ffmpeg", "-y", "-loglevel", "error", "-i", P / "qa" / "s_%02d.png",
            "-vf", f"scale=270:-1,tile={len(args)}x1", "-frames:v", "1", P / "qa" / "sheet.png")
        print("拼图：", P / "qa" / "sheet.png")
    elif name == "audio":
        run(PY, "mix.py", cwd=P)
        run(PY, V / "xilo" / "audio_tools.py", "normalize", P / "audio" / "mix_raw.wav", P / "audio" / "mix.wav")
        run(PY, V / "xilo" / "audio_tools.py", "check", P / "audio" / "mix.wav", "--out", P / "qa" / "audio")
    elif name == "render":
        run(PY, S / "build.py", P)
        dur = json.loads((P / "timeline.json").read_text(encoding="utf-8"))["duration"]
        if dur < cfg["min_duration"]:
            sys.exit(f"时长 {dur}s 不足 {cfg['min_duration']} 秒，先补口播再渲染（config.json 的 min_duration 可调）")
        if cfg["size"] != "1080x1920":
            print(f"⚠ 画幅 {cfg['size']} 不是竖屏 1080x1920")
        run(PY, V / "xilo" / "render.py", P / "index.html", P / "out" / f"{NAME}.mp4", "--size", cfg["size"],
            "--fps", cfg["fps"], "--duration", dur, "--audio", P / "audio" / "mix.wav")
        run(PY, V / "xilo" / "analyze_video.py", P / "out" / f"{NAME}.mp4", "--out", P / "qa" / "final", "--cell-width", 270)
    elif name == "all":
        for s in ("tts", "timing", "audio", "render"):
            step(s)
    else:
        sys.exit(f"未知步骤：{name}\n{__doc__}")


step(STEP, ARGS)
