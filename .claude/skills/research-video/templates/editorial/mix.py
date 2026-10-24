# 纸面编辑部风格：配乐 + 音效 + 旁白 → audio/mix_raw.wav
# 在项目目录里运行（make.py audio 会处理）。「音效」一节的时间点按 C(i)（第 i 条字幕开始）写，换研报后要按新画面改。
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.join(os.environ.get('SKILL_DIR', os.path.join(os.path.dirname(__file__), '..', '..')), 'scripts', 'vendor', 'lemo'))
import sfx as X
SR = X.SR
tl = json.load(open('timeline.json', encoding='utf-8')); S = tl['scenes']; CAP = tl['captions']; DUR = tl['duration']
C = lambda i: CAP[i]['t0']
N = int(DUR * SR) + SR
mus = np.zeros(N); fx = np.zeros(N); vo = np.zeros(N)
def add(buf, x, at, g=1.0):
    i = int(at * SR); m = min(len(x), N - i)
    if m > 0: buf[i:i + m] += x[:m] * g
def note(f, t0, length, amp, decay=.6):
    t = X.t_(length)
    sig = sum(np.sin(2 * np.pi * f * k * (1 + d) * t) / k for k, d in ((1, 0), (2, .002), (3, -.003)))
    add(mus, sig * np.minimum(1, t / .04) * np.exp(-t / decay) * amp, t0)
# ── 配乐：96 BPM，Cmaj7 – Am7 – Fmaj7 – G6，每两小节换；kick 从第二个场景进
B = 60 / 96
chords = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 329.6]]
for b in range(int(DUR / (4 * B)) + 1):
    c = chords[(b // 2) % 4]; t0 = b * 4 * B
    for f in c: note(f, t0, 4 * B + .3, .05, 1.6)
    for k in range(4): note(c[0] / 2, t0 + k * B, B, .12, .25)
for k in range(int(DUR / B)):
    if k * B >= S[1]['t0']: add(mus, X.thump(.35, 55), k * B)
x = np.arange(N) / SR; mus *= np.minimum(1, x / .5) * np.clip((DUR - x) / 1.2, 0, 1)
# ── 音效（示例来自 Lam 9月季度一片）
for s in S[1:]: add(fx, X.whoosh(.3, .6), s['t0'] - .3)
for t in (C(1) + .4, C(9), C(11), C(17), C(21)): add(fx, X.thump(.8, 50), t); add(fx, X.click(1.2, .5), t)
for t in (C(5), C(6), C(13), C(24)): add(fx, X.click(1.4, .5), t)
for t in (C(25), C(26), C(28)): add(fx, X.pop(.5), t)
# ── 旁白 + 闪避
for i, s in enumerate(S):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'audio/vo{i}.mp3', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    add(vo, np.frombuffer(raw, np.float32), s['vo'])
env = np.convolve(np.abs(vo), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
duck = 1 - .7 * np.clip(env / (env.max() * .25), 0, 1)
mix = mus * .55 * duck + fx * .5 + vo
mix /= np.abs(mix).max() * 1.1
with wave.open('audio/mix_raw.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
