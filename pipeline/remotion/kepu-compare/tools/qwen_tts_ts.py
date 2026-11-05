#!/usr/bin/env python3
"""Qwen-Audio-TTS 字级时间戳（HTTP SSE）。仅用标准库，便于在本仓复现。

接口：POST {base}/services/audio/tts/SpeechSynthesizer
必须显式传 word_timestamp_enabled=true；时间戳在 sentence-end 帧的 words 里返回。
"""
import base64
import json
import urllib.request
from pathlib import Path

MODEL = "qwen-audio-3.1-tts-flash"
BASE = "https://cn-beijing.maas.qianwenaiapi.com/api/v1"
KEY_FILE = Path(__file__).resolve().parents[4] / ".secrets" / "dashscope_key"


def _iter_events(resp):
    event, data = None, []
    for raw in resp:
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if not line:
            if data:
                yield event, "\n".join(data)
            event, data = None, []
        elif line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:])
    if data:
        yield event, "\n".join(data)


def synthesize(text, voice, rate=1.05, timeout=90):
    key = KEY_FILE.read_text().strip()
    body = {
        "model": MODEL,
        "input": {
            "text": text, "voice": voice, "format": "mp3", "sample_rate": 48000,
            "rate": rate, "word_timestamp_enabled": True, "language_hints": ["zh"],
        },
    }
    req = urllib.request.Request(
        BASE + "/services/audio/tts/SpeechSynthesizer",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "X-DashScope-SSE": "enable"})
    audio = bytearray(); words = []; usage = {}; ended = False
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for _ev, payload in _iter_events(resp):
            try:
                msg = json.loads(payload)
            except ValueError:
                raise RuntimeError("SSE 帧不是合法 JSON（流可能被截断）")
            if msg.get("code"):
                raise RuntimeError("%s: %s" % (msg.get("code"), msg.get("message")))
            out = msg.get("output") or {}
            b64 = (out.get("audio") or {}).get("data")
            if b64:
                audio.extend(base64.b64decode(b64))
            if out.get("type") == "sentence-end":
                words.extend((out.get("sentence") or {}).get("words") or [])
            if msg.get("usage"):
                usage = msg["usage"]
            if out.get("finish_reason") not in (None, "", "null"):
                ended = True
    if not ended:
        raise RuntimeError("读流提前结束：没有收到 finish_reason=stop")
    return {"audio": bytes(audio), "words": words, "usage": usage}


def cue_times(text, words, beat_start, cues):
    """把 cue 文本映射到字级时间戳；返回 [{text,start,end}]。"""
    norm = "".join(w.get("text", "") for w in words)
    # 逐字时间轴
    char_t = []
    for w in words:
        t = w.get("begin_time", 0) / 1000.0
        e = w.get("end_time", 0) / 1000.0
        n = max(1, len(w.get("text", "")))
        for i in range(n):
            char_t.append((t + (e - t) * i / n, t + (e - t) * (i + 1) / n))
    out = []
    cursor = 0
    for cue in cues:
        search = cue.replace(" ", "")
        p = norm.find(search, cursor)
        if p < 0:
            p = min(cursor, max(0, len(char_t) - 1))
        q = min(len(norm), p + len(search))
        cursor = q
        p = min(p, max(0, len(char_t) - 1))
        q = max(p + 1, min(q, len(char_t)))
        start = char_t[p][0] + beat_start
        end = char_t[q - 1][1] + beat_start
        out.append({"text": cue, "start": round(start, 3), "end": round(end, 3)})
    return out