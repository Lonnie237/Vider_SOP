#!/usr/bin/env python3
"""S5 字幕：按 beat 时间轴切分字幕、生成 SRT、校验并用 subtitle-pipeline 烧录。"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

MAX_CHARS = 16
MIN_CUE_S = 0.8


def parse_args():
    p = argparse.ArgumentParser(description="S5 字幕生成与烧录")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--font-size", type=int, default=58)
    p.add_argument("--margin-v", type=int, default=280)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def srt_time(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def split_text(text):
    parts = re.findall(r"[^，。；：？！,.;:?!]+[，。；：？！,.;:?!]?", text)
    cues = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        while len(part) > MAX_CHARS:
            cut = MAX_CHARS
            cues.append(part[:cut])
            part = part[cut:]
        if part:
            cues.append(part)
    return cues or [text]


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    voice = common.load_json(run_dir / "_pipeline" / "voice.json")
    audio = run_dir / "03-导出" / "preview" / "base_av.mp4"
    if not audio.exists():
        raise common.StageError("缺少上游产物：%s" % common.repo_rel(audio))

    cues = []
    cursor = 0.0
    for beat in voice["beats"]:
        chunks = split_text(beat["text"])
        weights = [max(1, len(c)) for c in chunks]
        total_w = float(sum(weights))
        start = max(beat["start"], cursor)
        span = max(MIN_CUE_S * len(chunks), beat["end"] - start)
        t = start
        for chunk, weight in zip(chunks, weights):
            dur = max(MIN_CUE_S, span * weight / total_w)
            end = min(t + dur, beat["end"] + 0.15)
            if end - t < MIN_CUE_S:
                end = t + MIN_CUE_S
            cues.append((t, end, chunk))
            t = end + 0.04
            cursor = t
    # 保证不重叠
    fixed = []
    prev_end = 0.0
    for start, end, text in cues:
        start = max(start, prev_end + 0.02)
        end = max(end, start + MIN_CUE_S)
        fixed.append((start, end, text))
        prev_end = end

    srt_lines = []
    for i, (start, end, text) in enumerate(fixed, 1):
        srt_lines.append(str(i))
        srt_lines.append("%s --> %s" % (srt_time(start), srt_time(end)))
        srt_lines.append(text)
        srt_lines.append("")
    srt_path = run_dir / "04-字幕" / "srt" / "voice.srt"
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    validator = common.REPO / "skills" / "subtitle-pipeline" / "scripts" / "subtitle.py"
    valid = common.run_soft([sys.executable, str(validator), "validate", "--input", str(srt_path)])
    validation_ok = valid.returncode == 0
    validation_note = ((valid.stdout or "") + (valid.stderr or "")).strip().splitlines()[-3:]

    burn = common.REPO / "skills" / "subtitle-pipeline" / "scripts" / "burn.py"
    subbed = run_dir / "03-导出" / "preview" / "subbed.mp4"
    burn_cmd = [sys.executable, str(burn), "--input", str(audio), "--srt", str(srt_path),
                "--output", str(subbed), "--engine", "auto", "--position", "bottom",
                "--font-size", str(args.font_size), "--max-width-ratio", "0.86", "--margin-v", str(args.margin_v),
                "--bg", "box", "--bg-opacity", "0.45", "--crf", "18", "--preset", "veryfast"]
    if args.force:
        burn_cmd.append("--force")
    common.run(burn_cmd)

    info = common.media_summary(subbed)
    common.save_json(run_dir / "_pipeline" / "subtitle.json", {
        "cues": len(fixed), "validation_ok": validation_ok,
        "validation_note": validation_note, "video": info,
    })
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(srt_path), common.repo_rel(subbed)],
        "metrics": {"cues": len(fixed), "validation_ok": validation_ok, "video": info},
        "note": "%d 条字幕，校验%s" % (len(fixed), "通过" if validation_ok else "有告警"),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)