#!/usr/bin/env python3
"""P2 渲染：调用 Remotion 工程渲染产品宣传片，并把成片落到 05-交付/final。"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="产品宣传片 Remotion 渲染")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    brief = common.load_json(run_dir / "_pipeline" / "brief.json")
    cfg = brief.get("render") or {}
    project = common.REPO / cfg["project_dir"]
    composition = cfg.get("composition", "CollectorPromoClean")
    out_dir = common.ensure_dir(run_dir / "05-交付" / "final")
    project_meta = brief.get("project") or {}
    slug = project_meta.get("slug", "product-promo")
    date = project_meta.get("date", "2026-11-03")
    raw = out_dir / (composition + "-raw.mp4")
    final = out_dir / (slug + "-v1-" + date + ".mp4")

    chrome = os.path.expanduser(cfg.get(
        "browser", "~/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))
    if not Path(chrome).exists():
        raise common.StageError("缺少浏览器：%s" % chrome)
    env = dict(os.environ)
    env["npm_config_cache"] = "/tmp/npm-cache"
    cmd = ["npx", "remotion", "render", "src/index.ts", composition, str(raw),
           "--codec", "h264", "--crf", "18", "--audio-codec", "aac", "--audio-bitrate", "192k",
           "--concurrency", "2", "--browser-executable", chrome]
    proc = subprocess.run(cmd, cwd=str(project), capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-12:]
        raise common.StageError("Remotion 渲染失败：\n%s" % "\n".join(tail))

    # 统一响度到 -16 LUFS
    common.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
                "-c:v", "libx264", "-preset", "slow", "-b:v", "7M", "-maxrate", "9M", "-bufsize", "14M",
                "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-movflags", "+faststart", str(final)])
    raw.unlink(missing_ok=True)
    info = common.media_summary(final)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(final)],
        "metrics": {"video": info, "composition": composition},
        "note": "成片 %ss / %.1f MB" % (info["duration_s"], info["size_mb"]),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)