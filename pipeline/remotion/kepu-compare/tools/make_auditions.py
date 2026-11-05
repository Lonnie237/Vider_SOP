#!/usr/bin/env python3
"""生成音色 / 语速 / 音高试听包（edge-tts）。输出到 out/auditions/。"""
import shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = ROOT / ".venv-tts" / "bin" / "edge-tts"
OUT = ROOT / "out" / "auditions"
TMP = ROOT / ".work" / "auditions"
for d in (OUT, TMP):
    d.mkdir(parents=True, exist_ok=True)

SAMPLE = "WorkBuddy 和 Qoder，到底差在哪？一句话：一个是腾讯的 AI 办公工作台，一个是阿里的 AI 编程工作台。"
RATE = "+12%"

VOICES = [
    ("A", "zh-CN-XiaoxiaoNeural", "晓晓", "温暖女声"),
    ("B", "zh-CN-XiaoyiNeural", "晓伊", "轻快女声"),
    ("C", "zh-CN-YunxiNeural", "云希", "活力男声"),
    ("D", "zh-CN-YunyangNeural", "云扬", "新闻男声"),
    ("E", "zh-CN-YunjianNeural", "云健", "激情男声"),
    ("F", "zh-CN-YunxiaNeural", "云夏", "可爱男声"),
    ("G", "zh-CN-liaoning-XiaobeiNeural", "晓北", "东北女声"),
    ("H", "zh-CN-shaanxi-XiaoniNeural", "晓妮", "陕西女声"),
]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("命令失败：%s\n%s" % (" ".join(cmd), p.stderr[-400:]))


def tts(text, voice, out_wav, rate=RATE, pitch="+0Hz"):
    mp3 = out_wav.with_suffix(".mp3")
    run([str(EDGE), "--voice", voice, "--rate=" + rate, "--pitch=" + pitch,
         "--text", text, "--write-media", str(mp3)])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3),
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out_wav)])
    mp3.unlink(missing_ok=True)


def silence(path, seconds=0.35):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
         "-i", "anullsrc=r=48000:cl=mono", "-t", "%.3f" % seconds,
         "-c:a", "pcm_s16le", str(path)])


def concat(items, out_mp3):
    gap = TMP / "gap.wav"
    silence(gap)
    seq = []
    for i, item in enumerate(items):
        seq.append(item)
        if i < len(items) - 1:
            seq.append(gap)
    listfile = TMP / "list.txt"
    listfile.write_text("".join("file '%s'\n" % str(p) for p in seq), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
         "-safe", "0", "-i", str(listfile), "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)])


# 1) 音色包
voice_items = []
for tag, code, name, style in VOICES:
    intro = TMP / (tag + "-intro.wav")
    sample = TMP / (tag + "-sample.wav")
    tts(tag + "，" + name + "，" + style + "。", code, intro)
    tts(SAMPLE, code, sample)
    voice_items.extend([intro, sample])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", str(TMP / "list.txt"), "-c", "copy", str(OUT / (tag + "-" + name + ".mp3"))]) if False else None
concat(voice_items, OUT / "audition-voices.mp3")

# 2) 语速包（晓晓）
pace_items = []
for pct in (5, 10, 15, 20):
    intro = TMP / ("pace-%d-intro.wav" % pct)
    sample = TMP / ("pace-%d-sample.wav" % pct)
    tts("语速加百分之%d。" % pct, "zh-CN-XiaoxiaoNeural", intro, rate="+%d%%" % pct)
    tts(SAMPLE, "zh-CN-XiaoxiaoNeural", sample, rate="+%d%%" % pct)
    pace_items.extend([intro, sample])
concat(pace_items, OUT / "audition-pace.mp3")

# 3) 音高包（晓晓 +12%）
pitch_items = []
for hz in (-6, 0, 6):
    intro = TMP / ("pitch-%d-intro.wav" % hz)
    sample = TMP / ("pitch-%d-sample.wav" % hz)
    label = "音高降低六赫兹。" if hz < 0 else ("音高不变。" if hz == 0 else "音高提高六赫兹。")
    tts(label, "zh-CN-XiaoxiaoNeural", intro, pitch="%+dHz" % hz)
    tts(SAMPLE, "zh-CN-XiaoxiaoNeural", sample, pitch="%+dHz" % hz)
    pitch_items.extend([intro, sample])
concat(pitch_items, OUT / "audition-pitch.mp3")

print("done", [p.name for p in OUT.glob("audition-*.mp3")])
