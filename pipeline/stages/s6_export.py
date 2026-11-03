#!/usr/bin/env python3
"""S6 导出：调用 ffmpeg-render 技能，按交付规格导出成片。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="S6 按规格导出成片")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def final_name(manifest):
    spec = manifest["delivery_spec"]
    pattern = spec.get("naming") or "%s-v1-2026-11-03.mp4" % manifest["project"]["slug"]
    date = manifest.get("project", {}).get("delivery_date") or "2026-11-03"
    name = pattern.replace("<version>", "v1").replace("<date>", date).replace("<slug>", manifest["project"]["slug"])
    return name


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    manifest = common.manifest(run_dir)
    source = run_dir / "03-导出" / "preview" / "subbed.mp4"
    if not source.exists():
        raise common.StageError("缺少上游产物：%s" % common.repo_rel(source))
    final_dir = common.ensure_dir(run_dir / "05-交付" / "final")
    output = final_dir / final_name(manifest)

    render = common.REPO / "skills" / "ffmpeg-render" / "scripts" / "render.py"
    if not render.exists():
        raise common.StageError("缺少 ffmpeg-render 技能脚本")
    render_cmd = [sys.executable, str(render),
                  "--input", str(source), "--output", str(output),
                  "--project", str(run_dir), "--mode", "export",
                  "--preset", "medium", "--no-audio-normalize", "--json"]
    if args.force:
        render_cmd.append("--force")
    proc = common.run(render_cmd)
    parsed = None
    text = (proc.stdout or "").strip()
    start = text.find("{")
    if start >= 0:
        try:
            parsed = json.loads(text[start:])
        except json.JSONDecodeError:
            parsed = None

    info = common.media_summary(output)
    common.save_json(run_dir / "_pipeline" / "export.json", {"final": str(output), "video": info,
                                                             "render": parsed})
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(output)],
        "metrics": {"video": info, "bitrate_kbps": round(info["size_mb"] * 8192 / info["duration_s"], 0)},
        "note": "成片 %ss / %.1f MB" % (info["duration_s"], info["size_mb"]),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)