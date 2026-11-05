#!/usr/bin/env python3
"""从 timeline.json 生成 SRT 字幕（已烧录字幕的文本备份）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "src" / "timeline.json").read_text(encoding="utf-8"))

def ts(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

lines = []
for i, b in enumerate(data["beats"], 1):
    lines += [str(i), ts(b["start"]) + " --> " + ts(b["end"]), b["text"], ""]
(ROOT / "subtitles.srt").write_text("\n".join(lines), encoding="utf-8")
print("subtitles.srt", len(data["beats"]), "cues")
