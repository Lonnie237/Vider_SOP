#!/usr/bin/env python3
"""生成 54s 轻氛围 BGM（numpy，无第三方音频库）。"""
import json, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
data = json.loads((ROOT / "src" / "timeline.json").read_text())
DUR = float(data["duration"])
N = int(SR * DUR)
t = np.arange(N) / SR
out = np.zeros(N, dtype=np.float64)

chords = [
    [110.00, 164.81, 220.00, 261.63],  # A2 C3 A3 C4
    [87.31, 130.81, 174.61, 220.00],   # F2 C3 F3 A3
    [98.00, 146.83, 196.00, 246.94],   # G2 D3 G3 B3
    [82.41, 123.47, 164.81, 207.65],   # E2 B2 E3 G#3
]
seg = 8.0
for i in range(int(np.ceil(DUR / seg))):
    start = i * seg
    end = min(DUR, start + seg)
    a, b = int(start * SR), int(end * SR)
    if a >= N:
        break
    ch = chords[i % len(chords)]
    local = np.zeros(b - a, dtype=np.float64)
    for j, f in enumerate(ch):
        amp = 0.5 if j == 0 else 0.22
        local += amp * np.sin(2 * np.pi * f * t[a:b] + j * 0.6)
        local += 0.06 * np.sin(2 * np.pi * f * 2 * t[a:b])
    env = np.ones_like(local)
    fade = min(int(0.8 * SR), len(local) // 2)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    out[a:b] += local * env * 0.35

# 缓慢呼吸 + 归一
out *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.08 * t)
out = out / max(1e-9, np.max(np.abs(out))) * 0.22
stereo = np.stack([out, np.roll(out, 240)], axis=1)
pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
with wave.open(str(ROOT / "public" / "bgm.wav"), "wb") as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes(pcm.tobytes())
print("bgm", round(DUR, 2), "s")
