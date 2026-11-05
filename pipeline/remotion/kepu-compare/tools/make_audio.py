#!/usr/bin/env python3
"""生成科普视频旁白、时间轴与字幕（macOS say）。"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SRC = ROOT / "src"
TMP = ROOT / ".work"
for d in (PUBLIC, SRC, TMP):
    d.mkdir(parents=True, exist_ok=True)

VOICE = "Tingting"
RATE = "261"  # 约 1.45x（say 默认 180 wpm）
LEAD, GAP, TAIL = 0.4, 0.35, 0.8

BEATS = [
    ("b01", "hook", "WorkBuddy 和 Qoder", "WorkBuddy 和 Qoder，到底差在哪？"),
    ("b02", "define", "一句话定位", "一句话：一个是腾讯的 AI 办公工作台，一个是阿里的 AI 编程工作台。"),
    ("b03", "workbuddy", "WorkBuddy", "WorkBuddy 管办公：写文档、做表格、查资料、开会，还能接腾讯文档、会议和企业微信。"),
    ("b04", "qoder", "Qoder", "Qoder 管写代码：补全、对话、自主编程，还有 Repo Wiki 项目知识库。"),
    ("b05", "why", "为什么是两款", "为什么两家各推一款？腾讯的基因是办公生态，阿里的基因是云和开发者。"),
    ("b06", "why", "分工不同", "腾讯用 CodeBuddy 管编程、WorkBuddy 管办公；阿里用 Qoder 管代码、QoderWork 管办公。"),
    ("b07", "choose", "怎么选", "普通人怎么选？先看你每天产出的是文档还是代码；再看你已经在用哪家的生态。"),
    ("b08", "choose", "两条路线", "写代码为主，选 Qoder；文档表格会议为主，选 WorkBuddy；两个都干，可以先用免费版各试一周。"),
    ("b09", "caution", "注意", "价格和功能会变，商用前看官网和合规要求；工具是壳，工作流才是核心。"),
    ("b10", "cta", "结尾", "能接进你工作流的，才是好工具。"),
]

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("命令失败：%s\n%s" % (" ".join(cmd), p.stderr[-500:]))
    return p

def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)]).stdout.strip()
    return float(out)

def silence(path, seconds):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
         "-i", "anullsrc=r=48000:cl=mono", "-t", "%.3f" % seconds,
         "-c:a", "pcm_s16le", str(path)])

def say(text, aiff):
    run(["say", "-v", VOICE, "-r", RATE, "-o", str(aiff), text])
    wav = aiff.with_suffix(".wav")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(aiff),
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
    aiff.unlink(missing_ok=True)
    return wav

lead = TMP / "lead.wav"; gap = TMP / "gap.wav"; tail = TMP / "tail.wav"
silence(lead, LEAD); silence(gap, GAP); silence(tail, TAIL)

items = [lead]
timings = []
t = LEAD
for i, (bid, section, headline, text) in enumerate(BEATS):
    raw = TMP / (bid + ".wav")
    wav = say(text, raw.with_suffix(".aiff"))
    d = duration(wav)
    timings.append({"id": bid, "section": section, "headline": headline,
                    "text": text, "start": round(t, 3), "end": round(t + d, 3),
                    "duration": round(d, 3)})
    items.append(wav)
    t += d
    if i < len(BEATS) - 1:
        items.append(gap); t += GAP
total = t + TAIL
items.append(tail)

list_path = TMP / "concat.txt"
list_path.write_text("".join("file '%s'\n" % str(p) for p in items), encoding="utf-8")
voice = PUBLIC / "voice.wav"
run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
     "-safe", "0", "-i", str(list_path), "-c", "copy", str(voice)])
total = duration(voice)

timeline = {"fps": 30, "width": 1920, "height": 1080,
            "duration": round(total, 3),
            "frames": int(round(total * 30)),
            "beats": timings}
(SRC / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"duration": total, "frames": timeline["frames"],
                  "beats": len(timings)}, ensure_ascii=False))
