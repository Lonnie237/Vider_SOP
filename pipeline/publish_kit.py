#!/usr/bin/env python3
"""发布包：把成片、封面、字幕、文案、数据回收表打包到 05-交付/publish/。"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE / "stages"))
import common  # noqa: E402

FIELDS = ["date", "platform", "views", "completions", "asset_opens", "workbuddy_opens", "first_tasks", "note"]


def parse_args():
    p = argparse.ArgumentParser(description="生成发布包")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--platform", default="视频号")
    p.add_argument("--title", default="")
    p.add_argument("--copy", default="")
    p.add_argument("--cover")
    p.add_argument("--vertical")
    return p.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    finals = sorted((run_dir / "05-交付" / "final").glob("*.mp4"))
    if not finals:
        raise SystemExit("没有成片：%s" % run_dir)
    out = common.ensure_dir(run_dir / "05-交付" / "publish")
    video = out / finals[-1].name
    shutil.copyfile(finals[-1], video)

    copied = [video.name]
    if args.cover and Path(args.cover).exists():
        cover = out / ("cover" + Path(args.cover).suffix)
        shutil.copyfile(args.cover, cover)
        copied.append(cover.name)
    if args.vertical and Path(args.vertical).exists():
        v = out / ("vertical" + Path(args.vertical).suffix)
        shutil.copyfile(args.vertical, v)
        copied.append(v.name)
    srt = next((run_dir / "04-字幕" / "srt").glob("*.srt"), None)
    if srt:
        shutil.copyfile(srt, out / "captions.srt")
        copied.append("captions.srt")

    title = args.title or "网站采集工程师：每天 9:30 自动出表"
    copy_text = args.copy or "给网址和字段，自动定位数据接口，按天采集、去重、失败通报。"
    (out / "发布文案.md").write_text(
        "# 发布文案\n\n"
        "- 平台：%s\n- 标题：%s\n\n## 正文\n\n%s\n\n"
        "## 话题\n\n#WorkBuddy #网站采集 #数据采集 #效率工具\n" % (args.platform, title, copy_text),
        encoding="utf-8")
    copied.append("发布文案.md")

    with open(out / "数据回收.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerow({"date": "", "platform": args.platform, "views": "", "completions": "",
                    "asset_opens": "", "workbuddy_opens": "", "first_tasks": "", "note": "发布后每天填一行"})
    copied.append("数据回收.csv")

    template = {
        "note": "发布后填入真实数据，不要填示例",
        "published_at": "",
        "platforms": [args.platform],
        "baseline": {"usage": 131},
        "metrics": {"views": 0, "completions": 0, "asset_opens": 0, "workbuddy_opens": 0, "first_tasks": 0},
    }
    (out / "retro-data.template.json").write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    copied.append("retro-data.template.json")

    print(json.dumps({"status": "ok", "out": common.repo_rel(out), "files": copied}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
