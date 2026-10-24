# 配乐 + 音效 + 旁白 → audio/mix_raw.wav（lemo sfx 做音效，numpy 写 E 小调新闻主题）
# 在项目目录里运行（make.py audio 会处理）。「音效」一节的时间点按 C(i)（第 i 条字幕开始）写，换研报后要按新画面改。
import json, sys, os, subprocess
import numpy as np
sys.path.insert(0, os.path.join(os.environ.get('SKILL_DIR', os.path.join(os.path.dirname(__file__), '..', '..')), 'scripts', 'vendor', 'lemo'))
import sfx as X
SR = X.SR
tl = json.load(open('timeline.json', encoding='utf-8')); S = tl['scenes']; CAP = tl['captions']; DUR = tl['duration']
C = lambda i: CAP[i]['t0']
N = int(DUR * SR) + SR
mus = np.zeros(N); fx = np.zeros(N)
def add(buf, x, at, g=1.0):
    i = int(at * SR); m = min(len(x), N - i)
    if m > 0: buf[i:i + m] += x[:m] * g
# ── 配乐：120 BPM，E 小调，片头之后进拍
BPM, T0 = 120, 1.9; B = 60 / BPM
NOTE = {'E': 40, 'C': 36, 'G': 43, 'D': 38, 'A': 45, 'B': 47}
prog = ['E', 'C', 'G', 'D']
def tone(f, d, amp, tau, harm=((1, 1), (2, .35), (3, .15))):
    t = X.t_(d); return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in harm) * np.exp(-t / tau) * np.minimum(1, t / .01) * amp
mf = lambda n: 440 * 2 ** ((n - 69) / 12)
end = S[-1]['t1']
bars = int((end - T0) / (4 * B)) + 1
for b in range(bars):
    t0 = T0 + b * 4 * B; root = NOTE[prog[b % 4]]; minor = prog[b % 4] in ('E',)
    chord = [root + 24, root + 24 + (3 if minor else 4), root + 31]
    for n in chord: add(mus, tone(mf(n), 4 * B + .2, .05, 1.4), t0)          # 铺底
    for k in range(8):                                                       # 八分音符贝斯
        add(mus, tone(mf(root), B / 2, .14, .12), t0 + k * B / 2)
    for k in range(4):                                                       # kick + 反拍 hat
        add(mus, X.thump(.5, 60), t0 + k * B)
        add(mus, X.hp(X.noise(.05), 6000) * X.env_exp(.05, .012) * .12, t0 + k * B + B / 2)
    arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]      # 每两小节一个琶音动机
    if b % 2 == 0:
        for k, n in enumerate(arp): add(mus, tone(mf(n), .5, .06, .25), t0 + k * B / 2)
mus *= np.minimum(1, np.arange(N) / SR / 2.0)
fade0 = int((end - 1.0) * SR); mus[fade0:] *= np.linspace(1, 0, N - fade0) ** 2
# 片尾：E 大三和弦
for n in (52, 56, 59, 64): add(mus, tone(mf(n), 3.0, .09, 1.2), end + .35)
# ── 音效
add(fx, X.whoosh(.3, .8), .02); add(fx, X.whoosh(.3, .7), .08)               # 两道斜线
add(fx, X.crash(.6), .16); add(fx, X.thump(1.0, 55), .16)                   # 品牌板砸入
for i in range(4): add(fx, X.click(1.4, .5), .42 + i * .07)
add(fx, X.ding(.35), 1.1)
for s in S[1:]: add(fx, X.whoosh(.32, .7), s['t0'] - .17)                  # 色带擦除
add(fx, X.whoosh(.32, .6), 1.45)
for i in range(4): add(fx, X.clack(1.0, .6), C(2 + i) - .1)                # 串联单翻入
def flap(t0, n):
    for i in range(n): add(fx, X.clack(1.3, .45), t0 + i * .07 + .17)
flap(C(7) + .1, 5); flap(C(15) + 1.0, 3); flap(C(24) + .3, 5)
for t in (C(11), C(26) + .2, C(36) + .1, C(22) + 1.1 + .35): add(fx, X.thump(1.0, 48), t); add(fx, X.crash(.35), t)   # 印章
add(fx, X.ding(.6), C(22) + 1.1)                                            # 冲过 40%
for t in (C(9) - .1, C(16) - .1, C(22) - .1, C(23) - .1, C(28) - .1, C(38) - .1): add(fx, X.thump(.6, 90), t)  # 故事内硬切
for i in range(3): add(fx, X.clack(1.0, .6), C(38 + i) - .05); add(fx, X.ding(.3), C(38 + i) + .55)
add(fx, X.whoosh(.45, .8), CAP[40]['t1'] + .35)
# ── 旁白
vo = np.zeros(N)
for i, s in enumerate(S):
    wav = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'audio/vo{i}.mp3', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    add(vo, np.frombuffer(wav, np.float32), s['vo'])
# 旁白出现时音乐压低（包络跟随）
env = np.convolve(np.abs(vo), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
duck = 1 - .72 * np.clip(env / (env.max() * .25), 0, 1)
mix = mus * .55 * duck + fx * .5 + vo * 1.0
mix /= np.abs(mix).max() * 1.1
import wave
with wave.open('audio/mix_raw.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
