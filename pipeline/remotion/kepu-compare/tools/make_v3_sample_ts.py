#!/usr/bin/env python3
"""v3 30s 样片：Qwen TTS（字级时间戳）+ 精确字幕对齐。"""
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".work"
PUB = ROOT / "public"
SRC = ROOT / "src"
BILLING = ROOT / "billing"
for d in (TMP, PUB, SRC, BILLING):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tools"))
import qwen_tts_ts as q

VOICE = "longanlingxin_v3.1"
RATE = 1.05
LEAD, GAP, TAIL = 0.45, 0.42, 0.8

BEATS = [
    {"id": "b01", "section": "hook", "headline": "周一 9:00",
     "text": "周一早上九点，你打开电脑：左边是没写完的周报，右边是等着修的 bug。如果只能装一个 AI 工作台，你装哪个？",
     "cues": ["周一早上九点", "你打开电脑", "左边是没写完的周报", "右边是等着修的 bug", "如果只能装一个 AI 工作台", "你装哪个？"]},
    {"id": "b03", "section": "define", "headline": "一句话定义",
     "text": "它们都是 AI 工作台：能拆任务、调工具、把结果直接交给你。区别在主场：WorkBuddy 是腾讯的办公工作台，Qoder 是阿里的编程工作台。",
     "cues": ["它们都是 AI 工作台", "能拆任务、调工具", "把结果直接交给你", "区别在主场", "WorkBuddy 是腾讯的", "办公工作台", "Qoder 是阿里的", "编程工作台"]},
    {"id": "b04", "section": "context", "headline": "差异① 上下文",
     "text": "先看上下文。WorkBuddy 读的是文档、表格、会议纪要，还有腾讯文档和企业微信；Qoder 读的是代码、仓库、PR 和终端。",
     "cues": ["先看上下文", "WorkBuddy 读的是文档", "表格、会议纪要", "还有腾讯文档和企业微信", "Qoder 读的是代码", "仓库、PR 和终端"]},
]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("失败：%s\n%s" % (" ".join(cmd), p.stderr[-500:]))
    return p


def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)]).stdout)


def silence(path, seconds):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "%.3f" % seconds, "-c:a", "pcm_s16le", str(path)])


def main():
    lead = TMP / "v3ts-lead.wav"; gap = TMP / "v3ts-gap.wav"; tail = TMP / "v3ts-tail.wav"
    silence(lead, LEAD); silence(gap, GAP); silence(tail, TAIL)
    items = [lead]; beats = []; cues = []; wordmap = {}; t = LEAD
    total = {"input": 0, "output": 0, "total": 0, "chars": 0, "calls": 0}
    rows = []
    for i, b in enumerate(BEATS):
        r = q.synthesize(b["text"], VOICE, rate=RATE)
        mp3 = TMP / (b["id"] + ".mp3"); mp3.write_bytes(r["audio"])
        wav = TMP / (b["id"] + ".wav")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
        d = dur(wav)
        bstart = t
        beats.append({"id": b["id"], "section": b["section"], "headline": b["headline"], "text": b["text"],
                      "start": round(bstart, 3), "end": round(bstart + d, 3), "duration": round(d, 3)})
        beat_cues = q.cue_times(b["text"], r["words"], bstart, b["cues"])
        for c in beat_cues:
            c["tokens"] = [
                {"text": w.get("text", ""), "start": round(bstart + w.get("begin_time", 0) / 1000.0, 3),
                 "end": round(bstart + w.get("end_time", 0) / 1000.0, 3)}
                for w in r["words"]
                if c["start"] - 0.02 <= bstart + w.get("begin_time", 0) / 1000.0 <= c["end"] + 0.02
            ]
        cues.extend(beat_cues)
        wordmap[b["id"]] = {"text": b["text"], "words": r["words"]}
        usage = r["usage"]
        row = {"id": b["id"], "chars": len(b["text"]), "input_tokens": usage.get("input_tokens", 0),
               "output_tokens": usage.get("output_tokens", 0), "total_tokens": usage.get("total_tokens", 0),
               "characters": usage.get("characters", 0), "words": len(r["words"])}
        rows.append(row)
        for k, src in (("input", "input_tokens"), ("output", "output_tokens"), ("total", "total_tokens"), ("chars", "characters")):
            total[k] += int(usage.get(src) or 0)
        total["calls"] += 1
        items.append(wav); t += d
        if i < len(BEATS) - 1:
            items.append(gap); t += GAP
    items.append(tail)
    listf = TMP / "v3ts-list.txt"
    listf.write_text("".join("file '%s'\n" % str(p.resolve()) for p in items), encoding="utf-8")
    voice = PUB / "voice-v3-sample.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(voice)])
    duration = dur(voice)

    timeline = {"fps": 30, "width": 1920, "height": 1080, "duration": round(duration, 3), "frames": int(round(duration * 30)), "beats": beats}
    (SRC / "timeline-v3-sample.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    (SRC / "cues-v3-sample.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    (SRC / "words-v3-sample.json").write_text(json.dumps(wordmap, ensure_ascii=False, indent=2), encoding="utf-8")

    now = datetime.now()
    report = {"generated_at": now.isoformat(timespec="seconds"), "voice": VOICE, "rate": RATE,
              "rows": rows, "totals": total, "duration": duration}
    name = "tts-v3-sample-" + now.strftime("%Y%m%d-%H%M%S") + ".json"
    (BILLING / name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# TTS 计费 · v3 30s 样片", "", "- 音色：%s（rate %.2f）" % (VOICE, RATE), "- 明细：%s" % name, "",
             "| 指标 | 合计 |", "|---|---|", "| 调用 | %d |" % total["calls"],
             "| 输入 tokens | %d |" % total["input"], "| 输出 tokens | %d |" % total["output"],
             "| 总 tokens | %d |" % total["total"], "| API characters | %d |" % total["chars"],
             "| 音频 | %.2fs |" % duration, "", "| Beat | input | output | total | 字数 |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s |" % (r["id"], r["input_tokens"], r["output_tokens"], r["total_tokens"], r["chars"]))
    (ROOT / "TTS_BILLING_V3_SAMPLE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"duration": duration, "frames": timeline["frames"], "total": total, "cues": len(cues), "billing": name}, ensure_ascii=False))


if __name__ == "__main__":
    main()