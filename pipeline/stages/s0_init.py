#!/usr/bin/env python3
"""S0 初始化：调用 video-project-init 技能建项目，落盘 brief 副本与运行状态。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="S0 初始化项目")
    p.add_argument("--root", required=True)
    p.add_argument("--dir-name", required=True)
    p.add_argument("--brief", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    data = common.load_json(args.brief)
    project = data["project"]
    spec = data.get("spec", {})
    content = data.get("content", {})
    init_script = common.REPO / "skills" / "video-project-init" / "scripts" / "init_project.py"
    if not init_script.exists():
        raise common.StageError("缺少 video-project-init 技能脚本：%s" % init_script)

    duration = content.get("target_duration_s", project.get("target_duration_s", 60))
    cmd = [sys.executable, str(init_script),
           "--name", project["name"], "--form", project["form"],
           "--platform", project["platform"], "--root", args.root,
           "--dir-name", args.dir_name, "--duration", str(duration),
           "--date", project.get("date", "2026-11-03")]
    if project.get("slug"):
        cmd += ["--slug", project["slug"]]
    if project.get("owner"):
        cmd += ["--owner", project["owner"]]
    for key, flag in (("width", "--width"), ("height", "--height"), ("fps", "--fps")):
        if spec.get(key) is not None:
            cmd += [flag, str(spec[key])]
    if spec.get("video_bitrate_kbps"):
        cmd += ["--video-bitrate", str(spec["video_bitrate_kbps"])]
    if spec.get("loudness_lufs") is not None:
        cmd += ["--loudness", str(spec["loudness_lufs"])]
    if args.force:
        cmd.append("--force")
    common.run(cmd)

    project_dir = Path(args.root) / args.dir_name
    if not (project_dir / "manifest.json").exists():
        raise common.StageError("初始化失败：%s 下没有 manifest.json" % project_dir)

    pipeline_dir = common.ensure_dir(project_dir / "_pipeline")
    common.save_json(pipeline_dir / "brief.json", data)
    state = {
        "run_id": args.dir_name,
        "project_dir": str(project_dir),
        "started_at": common.now(),
        "updated_at": common.now(),
        "stages": [],
        "artifacts": [],
        "qc": None,
    }
    common.save_state(project_dir, state)

    spec_out = common.manifest(project_dir)["delivery_spec"]
    artifacts = [
        common.repo_rel(project_dir / "manifest.json"),
        common.repo_rel(project_dir / "项目Brief.md"),
        common.repo_rel(project_dir / "05-交付" / "交付规格.md"),
    ]
    common.emit({
        "status": "ok",
        "project_dir": str(project_dir),
        "artifacts": artifacts,
        "metrics": {
            "name": project["name"],
            "form": project["form"],
            "platform": project["platform"],
            "target_duration_s": duration,
            "delivery_spec": spec_out,
        },
        "note": "项目目录与交付规格已就绪",
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
