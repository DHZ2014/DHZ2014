"""新建一个研报视频项目。用法：python3 new.py <项目目录> [--style news|editorial]

会复制对应风格的 template.html（和 mix.py），生成 vo.json、config.json、镜头表.md 草稿，并链接字体目录。
template.html 里的场景是上一支片子（Lam Research）的，作为写法参考：保留包装系统的函数，场景函数按新研报重写。
"""
import argparse, json, os, shutil
from pathlib import Path
from common import SKILL, DEFAULTS

ap = argparse.ArgumentParser(); ap.add_argument("proj"); ap.add_argument("--style", default="news", choices=["news", "editorial"])
a = ap.parse_args()
proj = Path(a.proj); proj.mkdir(parents=True, exist_ok=True)
for sub in ("audio", "qa", "out"):
    (proj / sub).mkdir(exist_ok=True)
tpl = SKILL / "templates" / a.style
for f in tpl.iterdir():
    if not (proj / f.name).exists():
        shutil.copy(f, proj / f.name)
cfg = dict(DEFAULTS, style=a.style)
if a.style == "editorial":
    cfg.update(speed=1.12, leads={}, lead=0.45, tail=0.75, end_pad=0.8)
if not (proj / "config.json").exists():
    (proj / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
if not (proj / "vo.json").exists():
    (proj / "vo.json").write_text('[\n "场景 0 的口播",\n "场景 1 的口播"\n]\n', encoding="utf-8")
if not (proj / "镜头表.md").exists():
    shutil.copy(SKILL / "examples" / "lam-news" / "镜头表.md", proj / "镜头表.md")
fonts = SKILL / "fonts"
if fonts.exists() and not (proj / "fonts").exists():
    try:
        os.symlink(fonts, proj / "fonts", target_is_directory=True)
    except OSError:          # Windows 普通用户不能建符号链接：build.py 会改为直接引用 skill 里的字体
        pass
(proj / ".gitignore").write_text("fonts\nindex.html\naudio/*.mp3\naudio/*.wav\nqa/\nout/*.mp4\n", encoding="utf-8")
print(f"已建好 {proj}（风格 {a.style}）。下一步：写 vo.json 和 镜头表.md，再跑 python make.py {proj} lint")
