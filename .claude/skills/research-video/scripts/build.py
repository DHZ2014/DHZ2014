"""把 timeline.json 注入 template.html，生成可渲染的 index.html。用法：python3 build.py <项目>"""
import json, sys
from pathlib import Path
from common import SKILL, load_config

proj = Path(sys.argv[1]); cfg = load_config(proj)
tl = json.loads((proj / "timeline.json").read_text(encoding="utf-8"))
tl["burn_subs"] = bool(cfg["burn_subs"])   # 字幕烧进画面
html = (proj / "template.html").read_text(encoding="utf-8")
if not (proj / "fonts").exists():   # Windows 上建不了符号链接时，直接引用 skill 里的字体
    html = html.replace('href="fonts/fonts.css"', f'href="{(SKILL / "fonts" / "fonts.css").as_uri()}"')
assert "/*TIMELINE*/null" in html, "template.html 里要有 const TL = /*TIMELINE*/null;"
(proj / "index.html").write_text(html.replace("/*TIMELINE*/null", json.dumps(tl, ensure_ascii=False)), encoding="utf-8")
print("index.html 已生成" + ("（字幕烧进画面）" if tl["burn_subs"] else ""))
