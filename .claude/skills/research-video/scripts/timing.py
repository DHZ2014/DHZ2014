"""由各段旁白时长排出场景时间轴和字幕时间，写 <项目>/timeline.json 与 <项目>/out/<项目名>.srt。

每个场景 = lead（场景开始到旁白开口）+ 旁白 + tail；场景 0 的 lead 留给片头（config.leads）。
字幕按逗号句号切块，按字数（英文单词计 1.5 字）分配时间，再吸附到旁白里最近的停顿上。
MiniMax 的逐字时间戳文件放在阿里云 OSS，云端环境访问不到，所以用停顿检测代替。
"""
import json, re, subprocess, sys
from pathlib import Path
from common import load_config, cn_digits

proj = Path(sys.argv[1]); cfg = load_config(proj)
lines = json.loads((proj / "vo.json").read_text(encoding="utf-8"))
leads = {int(k): v for k, v in cfg["leads"].items()}


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))


def pauses(f):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=noise=-35dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return [(a + b) / 2 for a, b in zip(s, e)]


t = 0.0; scenes = []; caps = []
for i, text in enumerate(lines):
    f = proj / f"audio/vo{i}.mp3"; d = dur(f); ps = pauses(f)
    vo0 = t + leads.get(i, cfg["lead"])
    chunks = [c for c in re.split(r"[，。：；！？]", text) if c.strip()]
    w = [len(re.sub(r"[A-Za-z]+|\s", "", c)) + 1.5 * len(re.findall(r"[A-Za-z]+", c)) for c in chunks]
    tot = sum(w); bounds = [0.0]; acc = 0
    for x in w[:-1]:
        acc += x; b = d * acc / tot
        near = min(ps, key=lambda p: abs(p - b)) if ps else b
        bounds.append(near if abs(near - b) < .7 and near > bounds[-1] + .45 else max(b, bounds[-1] + .45))
    bounds.append(d)
    for c, a, b in zip(chunks, bounds, bounds[1:]):
        caps.append({"t0": round(vo0 + a, 3), "t1": round(vo0 + b, 3), "text": cn_digits(c.strip(), cfg["digits"])})
    end = vo0 + d + cfg["tail"]
    scenes.append({"i": i, "t0": round(t, 3), "t1": round(end, 3), "vo": round(vo0, 3)})
    t = end

tl = {"duration": round(t + cfg["end_pad"], 2), "scenes": scenes, "captions": caps}
(proj / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")


def ts(x):
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round((x % 1) * 1000)) % 1000:03d}"


(proj / "out").mkdir(exist_ok=True)
(proj / "out" / f"{proj.name}.srt").write_text(
    "".join(f"{k + 1}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{c['text']}\n\n" for k, c in enumerate(caps)), encoding="utf-8")
print(f"时长 {tl['duration']}s，{len(scenes)} 个场景，{len(caps)} 条字幕")
for k, c in enumerate(caps):
    print(f"C({k}) {c['t0']:7.2f}–{c['t1']:7.2f}  {c['text']}")
