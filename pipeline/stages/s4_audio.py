#!/usr/bin/env python3
"""S4 声音：两遍 loudnorm 归一到交付响度，再把配音与底片合板。"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="S4 响度归一与音画合板")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def measure(path, target):
    proc = common.run_soft(["ffmpeg", "-hide_banner", "-i", str(path),
                            "-af", "loudnorm=I=%s:TP=-1.5:LRA=11:print_format=json" % target,
                            "-f", "null", "-"])
    text = (proc.stderr or "") + (proc.stdout or "")
    start = text.rfind("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise common.StageError("loudnorm 测量失败：找不到 JSON 输出")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise common.StageError("loudnorm JSON 解析失败：%s" % exc)


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    voice = common.load_json(run_dir / "_pipeline" / "voice.json")
    manifest = common.manifest(run_dir)
    target = manifest["delivery_spec"]["loudness_lufs"]
    target = ("%.1f" % float(target)).rstrip("0").rstrip(".")

    voice_wav = run_dir / "01-素材" / "音频" / "voice.wav"
    voice_norm = run_dir / "01-素材" / "音频" / "voice_norm.wav"
    base = run_dir / "03-导出" / "preview" / "base.mp4"
    base_av = run_dir / "03-导出" / "preview" / "base_av.mp4"
    for p in (voice_wav, base):
        if not p.exists():
            raise common.StageError("缺少上游产物：%s" % common.repo_rel(p))

    before = measure(voice_wav, target)
    try:
        common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(voice_wav),
                    "-af", "loudnorm=I=%s:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:"
                           "measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true" % (
                               target, before["input_i"], before["input_tp"],
                               before["input_lra"], before["input_thresh"], before["target_offset"]),
                    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(voice_norm)])
    except common.StageError:
        common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(voice_wav),
                    "-af", "loudnorm=I=%s:TP=-1.5:LRA=11" % target,
                    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(voice_norm)])
    after = measure(voice_norm, target)

    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(base), "-i", str(voice_norm),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-shortest", "-movflags", "+faststart", str(base_av)])

    info = common.media_summary(base_av)
    payload = {"target_lufs": float(target), "before_lufs": float(before["input_i"]),
               "after_lufs": float(after["input_i"]), "video": info}
    common.save_json(run_dir / "_pipeline" / "audio.json", payload)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(voice_norm), common.repo_rel(base_av)],
        "metrics": {"lufs_before": payload["before_lufs"], "lufs_after": payload["after_lufs"],
                    "duration_s": info["duration_s"]},
        "note": "响度 %.1f → %.1f LUFS" % (payload["before_lufs"], payload["after_lufs"]),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
