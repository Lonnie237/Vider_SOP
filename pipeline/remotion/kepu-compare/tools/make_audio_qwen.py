#!/usr/bin/env python3
"""用阿里云百炼 Qwen TTS 生成旁白、时间轴，并记录 token 用量（计费统计）。"""
import json, subprocess
from datetime import datetime
from pathlib import Path

import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[2]
PUBLIC = ROOT / "public"
SRC = ROOT / "src"
TMP = ROOT / ".work"
BILLING = ROOT / "billing"
for d in (PUBLIC, SRC, TMP, BILLING):
    d.mkdir(parents=True, exist_ok=True)

MODEL = "qwen-audio-3.1-tts-flash"
VOICE = "longanhuan_v3.1"
BASE_WS = "wss://cn-beijing.maas.qianwenaiapi.com/api-ws/v1/inference"
SPEECH_RATE = 1.05
LEAD, GAP, TAIL = 0.45, 0.42, 0.9

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


def main():
    key = (REPO / ".secrets" / "dashscope_key").read_text().strip()
    dashscope.api_key = key
    dashscope.base_websocket_api_url = BASE_WS

    lead = TMP / "lead.wav"; gap = TMP / "gap.wav"; tail = TMP / "tail.wav"
    silence(lead, LEAD); silence(gap, GAP); silence(tail, TAIL)

    items = [lead]
    timings = []
    usage_rows = []
    t = LEAD
    total_in = total_out = total_tokens = total_chars = 0

    for i, (bid, section, headline, text) in enumerate(BEATS):
        synth = SpeechSynthesizer(model=MODEL, voice=VOICE, speech_rate=SPEECH_RATE)
        audio = synth.call(text)
        if not audio:
            raise SystemExit("TTS 返回空音频：%s" % bid)
        mp3 = TMP / (bid + ".mp3")
        mp3.write_bytes(audio)
        resp = synth.get_response() or {}
        usage = ((resp.get("payload") or {}).get("usage") or {})
        task_id = ((resp.get("header") or {}).get("task_id"))
        wav = TMP / (bid + ".wav")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3),
             "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
        d = duration(wav)
        timings.append({"id": bid, "section": section, "headline": headline,
                        "text": text, "start": round(t, 3), "end": round(t + d, 3),
                        "duration": round(d, 3)})
        row = {
            "id": bid, "chars": len(text),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "characters": usage.get("characters"),
            "task_id": task_id,
            "audio_duration_s": round(d, 3),
            "text": text,
        }
        usage_rows.append(row)
        total_in += int(usage.get("input_tokens") or 0)
        total_out += int(usage.get("output_tokens") or 0)
        total_tokens += int(usage.get("total_tokens") or 0)
        total_chars += int(usage.get("characters") or len(text))
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

    now = datetime.now()
    report = {
        "generated_at": now.isoformat(timespec="seconds"),
        "provider": "Alibaba Cloud Model Studio (DashScope)",
        "model": MODEL,
        "voice": VOICE,
        "speech_rate": SPEECH_RATE,
        "base_websocket_api_url": BASE_WS,
        "beats": usage_rows,
        "totals": {
            "beats": len(usage_rows),
            "input_tokens": total_in,
            "output_tokens": total_out,
            "total_tokens": total_tokens,
            "characters": total_chars,
            "audio_duration_s": round(total, 3),
        },
    }
    run_name = "tts-" + now.strftime("%Y%m%d-%H%M%S") + ".json"
    (BILLING / run_name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# TTS 计费统计 · WorkBuddy vs Qoder",
        "",
        "- 生成时间：%s" % now.isoformat(timespec="seconds"),
        "- 服务：阿里云百炼 DashScope（%s）" % BASE_WS,
        "- 模型：%s" % MODEL,
        "- 音色：%s（speech_rate=%.2f）" % (VOICE, SPEECH_RATE),
        "- 明细文件：%s" % run_name,
        "",
        "| 指标 | 合计 |",
        "|---|---|",
        "| 调用次数 | %d |" % len(usage_rows),
        "| 输入 tokens | %d |" % total_in,
        "| 输出 tokens | %d |" % total_out,
        "| 总 tokens | %d |" % total_tokens,
        "| 字符数 | %d |" % total_chars,
        "| 音频时长 | %.2f s |" % total,
        "",
        "## 逐句明细",
        "",
        "| Beat | 字符 | input | output | total | 音频秒 | task_id |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in usage_rows:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["chars"], r["input_tokens"], r["output_tokens"],
            r["total_tokens"], r["audio_duration_s"], r["task_id"]))
    (ROOT / "TTS_BILLING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"duration": total, "frames": timeline["frames"],
                      "input_tokens": total_in, "output_tokens": total_out,
                      "total_tokens": total_tokens, "characters": total_chars,
                      "billing": run_name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
