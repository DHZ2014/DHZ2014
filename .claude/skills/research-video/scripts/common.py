"""研报视频工程的公共工具：读配置、中文数字转阿拉伯数字。"""
import json, os, re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "style": "news", "size": "1080x1920", "fps": 30,
    "tts_model": "speech-2.6-hd", "voice_id": "male-qn-jingying", "speed": 1.15,
    "lead": 0.45, "tail": 0.6, "leads": {"0": 1.9}, "end_pad": 3.2,
    "digits": [],
    "burn_subs": False,      # true：字幕烧进画面（发小红书、静音观看时用）
}


def load_config(proj):
    cfg = dict(DEFAULTS)
    p = Path(proj) / "config.json"
    if p.exists():
        cfg.update(json.loads(p.read_text(encoding="utf-8")))
    return cfg


_D = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_U = {"十": 10, "百": 100, "千": 1000}
_NUM = "[零〇一二两三四五六七八九十百千]+"


def _int(s):
    if s and all(c in _D for c in s) and len(s) > 1:       # 二零二七 → 2027
        return int("".join(str(_D[c]) for c in s))
    total, cur = 0, 0
    for c in s:
        if c in _D:
            cur = _D[c]
        elif c in _U:
            total += (cur or 1) * _U[c]; cur = 0
    return total + cur


def _num(s):
    if "点" in s:
        a, b = s.split("点", 1)
        return f"{_int(a)}." + "".join(str(_D[c]) for c in b)
    return str(_int(s))


def cn_digits(text, extra=()):
    """口播是中文数字，屏上和字幕用阿拉伯数字。只转换带单位的数，避免把「一致」「四件事」之类改坏。"""
    for a, b in extra:
        text = text.replace(a, b)
    text = re.sub(f"百分之({_NUM}(?:点[零一二三四五六七八九]+)?)", lambda m: _num(m.group(1)) + "%", text)
    text = re.sub(f"({_NUM})分之({_NUM})", lambda m: f"{_num(m.group(2))}/{_num(m.group(1))}", text)
    text = re.sub(f"({_NUM}(?:点[零一二三四五六七八九]+)?)(?=[亿万颗倍]|美元|个百分点|年|月)",
                  lambda m: _num(m.group(1)), text)
    return text


if __name__ == "__main__":
    for s in ["九月季度收入八十二点二亿美元", "环比只增百分之四点六", "贡献了约四分之三的增量", "研报作者认为一致预期",
              "今天看四件事", "封装从八颗 HBM 做到十二颗", "下半财年季均收入需要约九十亿美元", "二零二七年一月下旬", "NAND 同比增长百分之一百三十四"]:
        print(s, "→", cn_digits(s))
