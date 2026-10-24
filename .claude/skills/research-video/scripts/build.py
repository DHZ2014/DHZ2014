"""把 timeline.json 注入 template.html，生成可渲染的 index.html。用法：python3 build.py <项目>"""
import sys
from pathlib import Path

proj = Path(sys.argv[1])
tl = (proj / "timeline.json").read_text(encoding="utf-8")
html = (proj / "template.html").read_text(encoding="utf-8")
assert "/*TIMELINE*/null" in html, "template.html 里要有 const TL = /*TIMELINE*/null;"
(proj / "index.html").write_text(html.replace("/*TIMELINE*/null", tl), encoding="utf-8")
print("index.html 已生成")
