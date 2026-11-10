#!/usr/bin/env python3
"""全片 QC：机器指标 + 抽帧。用法：python3 tools/qc_full.py [video.mp4]"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "full-raw.mp4"
QC = ROOT / "out" / "qc-full"; QC.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p

def probe(path):
    p = run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames","-of","json",str(path)])
    return json.loads(p.stdout)

def loudness(path):
    p = run(["ffmpeg","-hide_banner","-i",str(path),"-af","loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json","-f","null","-"])
    t = (p.stderr or "") + (p.stdout or ""); s = t.rfind("{"); e = t.rfind("}")
    return json.loads(t[s:e+1]) if s >= 0 else {}

def blackdetect(path):
    # pix_th=0.02：只判真正黑帧（≈#000）。黑板底 #101418 亮度≈0.075，属 intentional 深色设计，
    # 用 0.10 会把「标题+深色底」误判为黑帧；0.02 才能区分渲染缺陷与深色版式。
    p = run(["ffmpeg","-hide_banner","-i",str(path),"-vf","blackdetect=d=0.1:pix_th=0.02","-an","-f","null","-"])
    return [l for l in (p.stderr or "").splitlines() if "black_start" in l]

info = probe(VIDEO)
v = next(s for s in info["streams"] if s["codec_type"] == "video")
a = next(s for s in info["streams"] if s["codec_type"] == "audio")
dur = float(info["format"]["duration"])
loud = loudness(VIDEO)
black = blackdetect(VIDEO)

cues = json.load(open(ROOT / "src" / "cues-full.json"))
tl = json.load(open(ROOT / "src" / "timeline-full.json"))
overlaps = sum(1 for x, y in zip(cues, cues[1:]) if x["end"] > y["start"] + 0.001)
maxlen = max(len(c["text"]) for c in cues)

# 抽帧：首帧 + 每 12s 一帧 contact sheet
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(VIDEO),"-frames:v","1",str(QC / "first.png")])
run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(VIDEO),"-vf","fps=1/12,scale=480:-1,tile=5x5","-frames:v","1",str(QC / "contact.png")])

report = {
    "video": str(VIDEO),
    "duration_s": round(dur, 3),
    "duration_target": "245–265s (4:15±10s)",
    "duration_pass": 245 <= dur <= 265,
    "frames": int(v.get("nb_frames", 0)),
    "frames_expected": tl["frames"],
    "resolution": "%sx%s" % (v["width"], v["height"]),
    "fps": v["r_frame_rate"],
    "video_codec": v["codec_name"],
    "audio_codec": a["codec_name"],
    "lufs": float(loud.get("input_i", 0)),
    "lufs_pass": -17 <= float(loud.get("input_i", 0)) <= -15,
    "true_peak": float(loud.get("input_tp", 0)),
    "black_segments": black,
    "black_pass": len(black) == 0,
    "cues": len(cues),
    "cue_max_chars": maxlen,
    "cue_max_pass": maxlen <= 16,
    "cue_overlaps": overlaps,
    "cue_overlap_pass": overlaps == 0,
}
(QC / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=1))