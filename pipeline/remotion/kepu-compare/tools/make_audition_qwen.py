#!/usr/bin/env python3
"""Qwen-Audio-TTS 试听包：音色候选 + 语速档位；记录 token 用量。"""
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
BASE_WS = "wss://cn-beijing.maas.qianwenaiapi.com/api-ws/v1/inference"
SAMPLE = "WorkBuddy 和 Qoder，到底差在哪？一句话：一个是腾讯的 AI 办公工作台，一个是阿里的 AI 编程工作台。"

# 官方音色列表：https://www.alibabacloud.com/help/zh/model-studio/qwen-audio-tts-voice-list
VOICES = [
    ("A", "longanlingxin_v3.1", "龙安灵心", "旗舰女声，温柔自然"),
    ("B", "longanfengyue_v3.1", "龙安风悦", "女声，叙述感强"),
    ("C", "yuxiaoyun_v3.1", "于小云", "元气亲切，适合旁白"),
    ("D", "wenhuaiqing_v3.1", "温怀清", "清亮柔和，新闻/旁白"),
    ("E", "xuyuyuan_v3.1", "许玉远", "知性成熟，质感旁白"),
    ("F", "xunanchuan_v3.1", "许南川", "男声，磁性叙事"),
    ("G", "anmingyuan_v3.1", "安明远", "男声，清亮自然"),
    ("H", "longshu_v3.1", "龙书", "男声，沉稳磁性，新闻播报"),
]
RATES = [0.9, 1.0, 1.05, 1.1, 1.2]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("命令失败：%s\n%s" % (" ".join(cmd), p.stderr[-400:]))
    return p


def silence(path, seconds=0.4):
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


def synth(text, voice, rate, out_mp3):
    syn = SpeechSynthesizer(model=MODEL, voice=voice, speech_rate=rate)
    audio = syn.call(text)
    if not audio:
        raise SystemExit("空音频：%s" % voice)
    out_mp3.write_bytes(audio)
    resp = syn.get_response() or {}
    usage = ((resp.get("payload") or {}).get("usage") or {})
    return {
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
        "characters": int(usage.get("characters") or 0),
        "task_id": ((resp.get("header") or {}).get("task_id")),
    }


def main():
    dashscope.api_key = (REPO / ".secrets" / "dashscope_key").read_text().strip()
    dashscope.base_websocket_api_url = BASE_WS

    rows = []
    voice_items = []
    used = {"input": 0, "output": 0, "total": 0, "chars": 0, "calls": 0}

    for tag, voice, name, desc in VOICES:
        text = tag + "，" + name + "，" + desc + "。" + SAMPLE
        out = OUT / (tag + "-" + name + ".mp3")
        usage = synth(text, voice, 1.05, out)
        voice_items.append(out)
        rows.append({"kind": "voice", "tag": tag, "voice": voice, "name": name,
                     "rate": 1.05, "text": text, **usage})
        used["input"] += usage["input_tokens"]; used["output"] += usage["output_tokens"]
        used["total"] += usage["total_tokens"]; used["chars"] += usage["characters"]; used["calls"] += 1

    concat(voice_items, OUT / "audition-qwen-voices.mp3")

    rate_items = []
    for rate in RATES:
        label = str(rate).replace(".", "点")
        text = "语速 " + label + "。" + SAMPLE
        out = OUT / ("rate-" + str(rate).replace(".", "_") + ".mp3")
        usage = synth(text, "longanlingxin_v3.1", rate, out)
        rate_items.append(out)
        rows.append({"kind": "rate", "tag": "R" + str(rate), "voice": "longanlingxin_v3.1",
                     "name": "龙安灵心", "rate": rate, "text": text, **usage})
        used["input"] += usage["input_tokens"]; used["output"] += usage["output_tokens"]
        used["total"] += usage["total_tokens"]; used["chars"] += usage["characters"]; used["calls"] += 1

    concat(rate_items, OUT / "audition-qwen-rate.mp3")

    now = datetime.now()
    report = {"generated_at": now.isoformat(timespec="seconds"),
              "provider": "Alibaba Cloud Model Studio (DashScope)",
              "model": MODEL, "base_websocket_api_url": BASE_WS,
              "rows": rows, "totals": used}
    run_name = "tts-audition-" + now.strftime("%Y%m%d-%H%M%S") + ".json"
    (BILLING / run_name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Qwen TTS 试听会话 · 计费记录", "",
             "- 生成时间：%s" % now.isoformat(timespec="seconds"),
             "- 模型：%s" % MODEL,
             "- 明细：%s" % run_name, "",
             "| 指标 | 合计 |", "|---|---|",
             "| 调用次数 | %d |" % used["calls"],
             "| 输入 tokens | %d |" % used["input"],
             "| 输出 tokens | %d |" % used["output"],
             "| 总 tokens | %d |" % used["total"],
             "| 字符数 | %d |" % used["chars"], "",
             "## 明细", "",
             "| 类型 | 音色 | rate | 字符 | input | output | total |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["kind"], r["name"], r["rate"], len(r["text"]),
            r["input_tokens"], r["output_tokens"], r["total_tokens"]))
    (ROOT / "TTS_AUDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"calls": used["calls"], "input": used["input"],
                      "output": used["output"], "total": used["total"],
                      "chars": used["chars"], "billing": run_name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
