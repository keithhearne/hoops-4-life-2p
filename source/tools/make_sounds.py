"""Builds the game's sound pack from CC0 recordings (Freesound, via RinkGM's credits).
usage: python3 -I make_sounds.py <src_audio_dir> <out_dir>
Writes trimmed mono WAVs and a sounds.js with base64 MP3s for the game."""
import sys, os, subprocess, base64, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
SR = 22050

def load(n):
    sr, x = wavfile.read(os.path.join(src, n + ".wav"))
    assert sr == SR
    if x.dtype == np.int16: x = x.astype(np.float32) / 32768.0
    elif x.dtype == np.int32: x = x.astype(np.float32) / 2147483648.0
    else: x = x.astype(np.float32)
    return x

def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def norm(x, peak=0.89): return x / (np.abs(x).max() + 1e-9) * peak
def fade(x, a=0.003, b=0.05):
    n = len(x); x = x.copy()
    na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x
def onset(x, thr=0.08):
    return int(np.argmax(np.abs(x) > thr * np.abs(x).max()))

def room(x, secs=0.35, wet=0.12, seed=1):
    """a short, soft gym tail so dry hits sit in the same arena as the crowd"""
    rng = np.random.default_rng(seed)
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (secs / 5))
    ir = lp(ir, 3500); ir[0] = 0
    y = np.convolve(x, ir)[: len(x) + n] * wet / np.sqrt((ir ** 2).sum())
    y[: len(x)] += x
    return y

S = {}

# --- the referee: one real pea-whistle blast in a gym ---
w = load("ref_whistle")
w = hp(w, 600, 4)
S["whistle"] = fade(norm(w[onset(w):][: int(1.6 * SR)]), 0.002, 0.4)

# --- crowd ---
c = load("crowd_cheer"); S["cheer"] = fade(norm(hp(c, 70)), 0.002, 0.6)
a = load("crowd_applause"); S["applause"] = fade(norm(hp(a, 70)), 0.002, 0.6)
o = load("crowd_ooh"); S["ooh"] = fade(norm(hp(o, 80)), 0.002, 0.4)
g = load("crowd_gasp"); S["gasp"] = fade(norm(hp(g, 80)[onset(g, 0.03):][: int(1.8 * SR)]), 0.002, 0.4)
m = load("crowd_murmur"); S["murmur"] = norm(hp(m, 90), 0.7)   # already a seamless 8 s loop: no fades

# --- the basketball: three real bounces off a hard floor ---
for i in (1, 2, 3):
    b = load(f"ball_bounce_{i}")
    b = b[max(0, onset(b) - 20):][: int(0.32 * SR)]
    S[f"bounce{i}"] = fade(norm(hp(b, 45)), 0.001, 0.12)

# --- ball on the rim: a rubber thump + only the first instant of a real hoop strike, choked fast ---
pipe = load("puck_post"); pipe = pipe[onset(pipe):]
ball = S["bounce1"]
def rim_hit(choke, bright, seed):
    n = int(0.42 * SR); t = np.arange(n) / SR
    ring = pipe[:n] * np.exp(-t / choke)              # a rim with a ball on it doesn't sing: kill the ring
    ring = lp(ring, bright, 2); ring = hp(ring, 250)
    thump = np.zeros(n); bb = lp(ball, 1800)[:n]; thump[: len(bb)] = bb
    y = 0.75 * norm(thump) + 0.55 * norm(ring)
    return fade(norm(room(y, 0.3, 0.10, seed)), 0.001, 0.08)
S["rim1"] = rim_hit(0.045, 3200, 3)    # a softer "clunk"
S["rim2"] = rim_hit(0.075, 4200, 4)    # a harder "clank"

# --- ball on the backboard: a deeper, woodier thud with a little frame rattle ---
bb = lp(load("ball_bounce_2"), 1400)
bb = bb[max(0, onset(bb) - 20):][: int(0.3 * SR)]
x = np.arange(int(len(bb) / 0.78)) * 0.78                 # pitched down ~25%: a big flat board
bd = np.interp(x, np.arange(len(bb)), bb)
n = int(0.3 * SR); t = np.arange(n) / SR
rat = pipe[:n] * np.exp(-t / 0.02); rat = hp(lp(rat, 2500), 400)
y = np.zeros(max(len(bd), n)); y[: len(bd)] += norm(bd) * 0.9; y[:n] += norm(rat) * 0.18
S["board"] = fade(norm(room(y, 0.3, 0.1, 5)), 0.001, 0.08)

# write WAVs + MP3s, then a JS file with the MP3s as base64
js = {}
total = 0
for k, v in S.items():
    wp = os.path.join(out, k + ".wav")
    wavfile.write(wp, SR, (np.clip(v, -1, 1) * 32767).astype(np.int16))
    mp = os.path.join(out, k + ".mp3")
    br = "40k" if k in ("bounce1", "bounce2", "bounce3", "rim1", "rim2", "board") else "48k"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wp, "-ac", "1", "-ar", "22050", "-b:a", br, mp], check=True)
    d = open(mp, "rb").read(); total += len(d)
    js[k] = base64.b64encode(d).decode()
open(os.path.join(out, "sounds.js"), "w").write(
    "// Real recordings, all CC0 (public domain) from Freesound: see README credits\n"
    "const SND_DATA=" + json.dumps(js, separators=(",", ":")) + ";\n")
print("mp3 bytes", total, "js bytes", os.path.getsize(os.path.join(out, "sounds.js")))
