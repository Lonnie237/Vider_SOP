#!/usr/bin/env python3
"""指定 Qwen 音色 + 语速区间，生成试听音频并记录 token 用量。"""
import json, subprocess
from datetime import datetime
from pathlib import Path

import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[2]
OUT = ROOT / "out" / "auditions-qwen"
TMP = ROOT / ".work" / "auditions-qwen"
BILLING = ROOT / "billing"
for d in (OUT, TMP, BILLING):
    d.mkdir(parents=True, exist_ok=True)

MODEL = "qwen-audio-3.1-tts-flash"
VOICE = "longanzhi_v3.1"
NAME = "龙安智"
BASE_WS = "wss://cn-beijing.maas.qianwenaiapi.com/api-ws/v1/inference"
SAMPLE = "WorkBuddy 和 Qoder，到底差在哪？一句话：一个是腾讯的 AI 办公工作台，一个是阿里的 AI 编程工作台。"
RATES = [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("命令失败：%s\n%s" % (" ".join(cmd), p.stderr[-400:]))
    return p


def cn_rate(r):
    s = ("%.2f" % r).rstrip("0").rstrip(".")
    whole, _, frac = s.partition(".")
    digits = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
              "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
    out = "点" + "".join(digits[c] for c in frac) if frac else ""
    return "语速 " + "".join(digits[c] for c in whole) + out + "。"


def silence(path, seconds=0.45):
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


def main():
    dashscope.api_key = (REPO / ".secrets" / "dashscope_key").read_text().strip()
    dashscope.base_websocket_api_url = BASE_WS

    rows = []
    items = []
    totals = {"input": 0, "output": 0, "total": 0, "chars": 0, "calls": 0}
    for rate in RATES:
        text = cn_rate(rate) + SAMPLE
        out = OUT / ("longanzhi-" + str(rate).replace(".", "_") + ".mp3")
        syn = SpeechSynthesizer(model=MODEL, voice=VOICE, speech_rate=rate)
        audio = syn.call(text)
        if not audio:
            raise SystemExit("空音频 rate=%s" % rate)
        out.write_bytes(audio)
        resp = syn.get_response() or {}
        usage = ((resp.get("payload") or {}).get("usage") or {})
        row = {"rate": rate, "text": text, "file": out.name,
               "input_tokens": int(usage.get("input_tokens") or 0),
               "output_tokens": int(usage.get("output_tokens") or 0),
               "total_tokens": int(usage.get("total_tokens") or 0),
               "characters": int(usage.get("characters") or 0),
               "task_id": ((resp.get("header") or {}).get("task_id"))}
        rows.append(row)
        items.append(out)
        for k in ("input", "output", "total", "chars"):
            totals[k] += row[{"input": "input_tokens", "output": "output_tokens",
                              "total": "total_tokens", "chars": "characters"}[k]]
        totals["calls"] += 1

    combined = OUT / "audition-longanzhi-rate.mp3"
    concat(items, combined)

    now = datetime.now()
    report = {"generated_at": now.isoformat(timespec="seconds"),
              "provider": "Alibaba Cloud Model Studio (DashScope)",
              "model": MODEL, "voice": VOICE, "name": NAME,
              "base_websocket_api_url": BASE_WS, "rates": RATES,
              "rows": rows, "totals": totals}
    run_name = "tts-rate-" + now.strftime("%Y%m%d-%H%M%S") + ".json"
    (BILLING / run_name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Qwen TTS 语速试听 · %s（%s）" % (NAME, VOICE), "",
             "- 生成时间：%s" % now.isoformat(timespec="seconds"),
             "- 模型：%s" % MODEL,
             "- 范围：0.9–1.4（步长 0.05）",
             "- 明细：%s" % run_name, "",
             "| 指标 | 合计 |", "|---|---|",
             "| 调用次数 | %d |" % totals["calls"],
             "| 输入 tokens | %d |" % totals["input"],
             "| 输出 tokens | %d |" % totals["output"],
             "| 总 tokens | %d |" % totals["total"],
             "| 字符数 | %d |" % totals["chars"], "",
             "## 明细", "",
             "| rate | 字符 | input | output | total |",
             "|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["rate"], len(r["text"]), r["input_tokens"], r["output_tokens"], r["total_tokens"]))
    (ROOT / "TTS_RATE_AUDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"voice": VOICE, "calls": totals["calls"],
                      "input": totals["input"], "output": totals["output"],
                      "total": totals["total"], "chars": totals["chars"],
                      "combined": combined.name, "billing": run_name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
