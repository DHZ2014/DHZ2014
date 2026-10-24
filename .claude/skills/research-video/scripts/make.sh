#!/usr/bin/env bash
# 研报视频流水线。用法：bash make.sh <项目目录> <步骤> [参数]
#   lint              花叔 storyboard_lint 检查 镜头表.md（并核对屏上数字是否出现在口播里）
#   tts [段号...]      MiniMax 合成旁白（只重做某几段就写段号）
#   timing            排时间轴、字幕，生成 out/<项目>.srt
#   stills t1 t2 ...  构建并渲染若干静帧，拼成 qa/sheet.png（自检用）
#   audio             运行项目里的 mix.py → 标准化到 -14 LUFS → 出波形图
#   render            渲染整片 out/<项目>.mp4 并出抽帧图 qa/final-sheet.png
#   all               tts → timing → audio → render
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"; S="$SKILL/scripts"; V="$S/vendor"
PY="${PYTHON:-python3}"
P="$(cd "$1" && pwd)"; NAME="$(basename "$P")"; STEP="$2"; shift 2
export SKILL_DIR="$SKILL"
cfg() { "$PY" -c "import sys; sys.path.insert(0, '$S'); from common import load_config; print(load_config('$P')['$1'])"; }
case "$STEP" in
  lint)
    "$PY" -c "import json; print(''.join(json.load(open('$P/vo.json', encoding='utf-8'))))" > "$P/qa/文稿.txt"
    "$PY" "$V/huashu/storyboard_lint.py" "$P/镜头表.md" --script "$P/qa/文稿.txt" ;;
  tts)    (cd "$S" && "$PY" tts.py "$P" "$@") ;;
  timing) (cd "$S" && "$PY" timing.py "$P") ;;
  stills)
    "$PY" "$S/build.py" "$P"; rm -f "$P"/qa/s_*.png
    for t in "$@"; do "$PY" "$V/xilo/render.py" "$P/index.html" "$P/qa/s_$(printf '%06.2f' "$t").png" --still "$t" --size "$(cfg size)" >/dev/null; done
    ffmpeg -y -loglevel error -pattern_type glob -i "$P/qa/s_*.png" -vf "scale=270:-1,tile=$#x1" -frames:v 1 "$P/qa/sheet.png"
    echo "拼图：$P/qa/sheet.png" ;;
  audio)
    (cd "$P" && "$PY" mix.py)
    "$PY" "$V/xilo/audio_tools.py" normalize "$P/audio/mix_raw.wav" "$P/audio/mix.wav"
    "$PY" "$V/xilo/audio_tools.py" check "$P/audio/mix.wav" --out "$P/qa/audio" ;;
  render)
    "$PY" "$S/build.py" "$P"
    D=$("$PY" -c "import json; print(json.load(open('$P/timeline.json'))['duration'])")
    "$PY" "$V/xilo/render.py" "$P/index.html" "$P/out/$NAME.mp4" --size "$(cfg size)" --fps "$(cfg fps)" --duration "$D" --audio "$P/audio/mix.wav"
    "$PY" "$V/xilo/analyze_video.py" "$P/out/$NAME.mp4" --out "$P/qa/final" --cell-width 270 ;;
  all)
    bash "$0" "$P" tts; bash "$0" "$P" timing; bash "$0" "$P" audio; bash "$0" "$P" render ;;
  *) echo "未知步骤：$STEP"; exit 2 ;;
esac
