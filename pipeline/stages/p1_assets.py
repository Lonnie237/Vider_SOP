#!/usr/bin/env python3
"""P1 素材检查：产品宣传片依赖的真实录屏、配音、二维码、Remotion 工程是否齐全。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="产品宣传片素材检查")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    brief = common.load_json(run_dir / "_pipeline" / "brief.json")
    assets = brief.get("assets") or []
    missing = []
    total = 0
    for rel in assets:
        path = common.REPO / rel
        if not path.exists():
            missing.append(rel)
        else:
            total += path.stat().st_size
    if missing:
        raise common.StageError("缺少素材：%s" % ", ".join(missing))
    project = brief.get("render", {}).get("project_dir")
    if project and not (common.REPO / project).exists():
        raise common.StageError("缺少 Remotion 工程：%s" % project)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(run_dir / "_pipeline" / "brief.json")],
        "metrics": {"assets": len(assets), "bytes": total, "project": project},
        "note": "素材齐全：%d 个" % len(assets),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
