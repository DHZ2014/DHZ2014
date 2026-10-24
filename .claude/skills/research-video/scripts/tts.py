"""逐段合成旁白：<项目>/vo.json 里每一项是一个场景的口播，输出 <项目>/audio/vo{i}.mp3。

用法：python3 tts.py <项目> [段号 ...]      # 不给段号就全部合成
凭据：环境变量 MINIMAX_API_KEY（电脑端必填）；云端 Claude Code 环境由代理自动注入，可以不设。
      MINIMAX_API_HOST 默认 api.minimax.cn（国际站用 api.minimax.io），MINIMAX_GROUP_ID 按账号需要设置。
"""
import json, os, sys, urllib.request
from pathlib import Path
from common import load_config

proj = Path(sys.argv[1]); cfg = load_config(proj)
lines = json.loads((proj / "vo.json").read_text(encoding="utf-8"))
only = [int(x) for x in sys.argv[2:]] or range(len(lines))
host = os.environ.get("MINIMAX_API_HOST", "api.minimax.cn")
url = f"https://{host}/v1/t2a_v2"
if os.environ.get("MINIMAX_GROUP_ID"):
    url += "?GroupId=" + os.environ["MINIMAX_GROUP_ID"]
headers = {"Content-Type": "application/json"}
if os.environ.get("MINIMAX_API_KEY"):
    headers["Authorization"] = "Bearer " + os.environ["MINIMAX_API_KEY"]
(proj / "audio").mkdir(exist_ok=True)
for i in only:
    body = {"model": cfg["tts_model"], "text": lines[i], "stream": False,
            "voice_setting": {"voice_id": cfg["voice_id"], "speed": cfg["speed"]},
            "audio_setting": {"sample_rate": 32000, "format": "mp3"}}
    req = urllib.request.Request(url, json.dumps(body).encode(), headers)
    d = json.load(urllib.request.urlopen(req, timeout=120))
    if d.get("base_resp", {}).get("status_code") != 0:
        sys.exit(f"MiniMax 返回错误：{d.get('base_resp')}（电脑端请检查 MINIMAX_API_KEY / MINIMAX_GROUP_ID）")
    (proj / f"audio/vo{i}.mp3").write_bytes(bytes.fromhex(d["data"]["audio"]))
    print(i, d["extra_info"]["audio_length"], "ms")
