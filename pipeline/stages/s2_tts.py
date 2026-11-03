#!/usr/bin/env python3
"""S2 配音：macOS say 逐 beat 合成，拼接为整轨，输出精确时间轴。"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

LEAD_S = 0.4
GAP_S = 0.3
TAIL_S = 0.8


def parse_args():
    p = argparse.ArgumentParser(description="S2 TTS 配音")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--voice", default="Tingting", help="say 语音名，默认 Tingting")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def make_silence(path, seconds):
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-t", "%.3f" % seconds, "-c:a", "pcm_s16le", str(path)])


def say_wav(text, voice, out_wav):
    aiff = out_wav.with_suffix(".aiff")
    common.run(["say", "-v", voice, "-o", str(aiff), text], timeout=120)
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(aiff), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out_wav)])
    if aiff.exists():
        aiff.unlink()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    data = common.brief(run_dir)
    beats = data.get("beats") or []
    if not beats:
        raise common.StageError("brief 中没有 beats")
    if shutil.which("say") is None:
        raise common.StageError("本机缺少 macOS say 命令，无法合成配音")

    audio_dir = common.ensure_dir(run_dir / "01-素材" / "音频")
    beats_dir = common.ensure_dir(audio_dir / "beats")
    tmp_dir = common.ensure_dir(run_dir / "_pipeline" / "tts")
    if args.force:
        for f in beats_dir.glob("*.wav"):
            f.unlink()

    lead = tmp_dir / "silence_lead.wav"
    gap = tmp_dir / "silence_gap.wav"
    tail = tmp_dir / "silence_tail.wav"
    make_silence(lead, LEAD_S)
    make_silence(gap, GAP_S)
    make_silence(tail, TAIL_S)

    concat_items = [str(lead)]
    timings = []
    t = LEAD_S
    for i, beat in enumerate(beats, 1):
        beat_wav = beats_dir / ("%02d-%s.wav" % (i, beat["id"]))
        say_wav(beat["say"], args.voice, beat_wav)
        dur = common.duration_of(beat_wav)
        timings.append({
            "id": beat["id"], "index": i, "role": beat["role"],
            "headline": beat["headline"], "text": beat["say"],
            "start": round(t, 3), "end": round(t + dur, 3), "duration": round(dur, 3),
        })
        concat_items.append(str(beat_wav))
        t += dur
        if i < len(beats):
            concat_items.append(str(gap))
            t += GAP_S
    total = t - 0 + TAIL_S
    concat_items.append(str(tail))

    list_path = tmp_dir / "concat.txt"
    lines = []
    for item in concat_items:
        lines.append("file '%s'" % item.replace("'", "'\\''"))
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    voice_wav = audio_dir / "voice.wav"
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(list_path),
                "-c", "copy", str(voice_wav)])
    actual = common.duration_of(voice_wav)
    payload = {
        "voice": args.voice,
        "total_duration_s": round(actual, 3),
        "lead_in_s": LEAD_S,
        "gap_s": GAP_S,
        "tail_s": TAIL_S,
        "beats": timings,
        "chars_per_sec": round(sum(len(b["say"]) for b in beats) / max(0.01, actual), 2),
    }
    common.save_json(run_dir / "_pipeline" / "voice.json", payload)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(voice_wav), common.repo_rel(run_dir / "_pipeline" / "voice.json")],
        "metrics": {"voice": args.voice, "duration_s": round(actual, 3),
                    "chars_per_sec": payload["chars_per_sec"], "beats": len(beats)},
        "note": "配音 %.1fs（%s）" % (actual, args.voice),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
