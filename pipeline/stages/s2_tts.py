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
    p.add_argument("--voice", default=None, help="say 语音名，默认读 brief.voice.name 或 Tingting")
    p.add_argument("--rate-multiplier", type=float, default=None,
                   help="语速倍数（相对 say 默认 180 wpm），默认读 brief.voice.rate_multiplier")
    p.add_argument("--rate-wpm", type=int, default=None, help="直接指定 say -r 的 wpm")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def make_silence(path, seconds):
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-t", "%.3f" % seconds, "-c:a", "pcm_s16le", str(path)])


def say_audio(text, voice, aiff, rate=None):
    cmd = ["say", "-v", voice]
    if rate:
        cmd += ["-r", str(int(rate))]
    cmd += ["-o", str(aiff), text]
    common.run(cmd, timeout=120)
    return common.duration_of(aiff)


def say_wav(text, voice, out_wav, rate=None):
    aiff = out_wav.with_suffix(".aiff")
    say_audio(text, voice, aiff, rate)
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(aiff), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out_wav)])
    if aiff.exists():
        aiff.unlink()


def calibrate_rate(voice, multiplier, tmp_dir, base_wpm=180.0):
    """用一段校准文本二分/迭代，找到使时长 = 默认时长 / multiplier 的 say -r 值。"""
    text = "口播语速校准，一二三四五六七八九十。"
    base_aiff = tmp_dir / "calib_base.aiff"
    base = say_audio(text, voice, base_aiff)
    target = base / multiplier
    rate = int(round(base_wpm * multiplier))
    used_aiff = tmp_dir / "calib_used.aiff"
    duration = say_audio(text, voice, used_aiff, rate)
    best = (abs(duration - target), rate, duration)
    for _ in range(2):
        if abs(duration - target) / target < 0.03:
            break
        rate2 = max(80, int(round(rate * duration / target)))
        if rate2 == rate:
            break
        duration2 = say_audio(text, voice, used_aiff, rate2)
        if abs(duration2 - target) < best[0]:
            best = (abs(duration2 - target), rate2, duration2)
        rate, duration = rate2, duration2
    return best[1], {"base_s": round(base, 3), "target_s": round(target, 3),
                     "effective_wpm": best[1], "calibrated_s": round(best[2], 3)}


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    data = common.brief(run_dir)
    voice_cfg = data.get("voice", {}) or {}
    voice = args.voice or voice_cfg.get("name") or "Tingting"
    multiplier = args.rate_multiplier if args.rate_multiplier is not None else voice_cfg.get("rate_multiplier", 1.0)
    beats = data.get("beats") or []
    if not beats:
        raise common.StageError("brief 中没有 beats")
    if shutil.which("say") is None:
        raise common.StageError("本机缺少 macOS say 命令，无法合成配音")
    if multiplier <= 0:
        raise common.StageError("语速倍数必须大于 0：%s" % multiplier)

    audio_dir = common.ensure_dir(run_dir / "01-素材" / "音频")
    beats_dir = common.ensure_dir(audio_dir / "beats")
    tmp_dir = common.ensure_dir(run_dir / "_pipeline" / "tts")
    if args.force:
        for f in beats_dir.glob("*.wav"):
            f.unlink()

    rate = args.rate_wpm
    rate_info = None
    if rate is None and abs(float(multiplier) - 1.0) > 0.01:
        rate, rate_info = calibrate_rate(voice, float(multiplier), tmp_dir)

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
        say_wav(beat["say"], voice, beat_wav, rate)
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
        "voice": voice,
        "rate_multiplier": float(multiplier),
        "rate_wpm": rate,
        "rate_calibration": rate_info,
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
        "metrics": {"voice": voice, "duration_s": round(actual, 3),
                    "chars_per_sec": payload["chars_per_sec"], "beats": len(beats),
                    "rate_multiplier": float(multiplier), "rate_wpm": rate},
        "note": "配音 %.1fs（%s）" % (actual, args.voice),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)