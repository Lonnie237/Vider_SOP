#!/usr/bin/env python3
"""发布数据回流：把投放数据变成下一版改什么的判断。

输入：<run>/_pipeline/retro-data.json
输出：漏斗指标 + 判断 + 建议动作；供 board.py --retro 写入复盘。

用法：
  python3 pipeline/retro_data.py --run-dir pipeline/runs/demo-product-promo-collector
  python3 pipeline/retro_data.py --input pipeline/demo/retro-data.example.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

THRESHOLDS = {
    "completion_rate": 0.30,
    "asset_open_rate": 0.01,
    "workbuddy_open_rate": 0.20,
    "first_task_rate": 0.30,
    "min_views": 100,
}


def ratio(num, den):
    if not den:
        return None
    return round(float(num) / float(den), 4)


def analyze(data):
    m = data.get("metrics") or {}
    views = int(m.get("views") or 0)
    asset_opens = int(m.get("asset_opens") or 0)
    wb_opens = int(m.get("workbuddy_opens") or 0)
    first_tasks = int(m.get("first_tasks") or 0)
    completion = m.get("completion_rate")
    if completion is None:
        completion = ratio(m.get("completions") or 0, views)
    metrics = {
        "views": views,
        "completion_rate": completion,
        "asset_open_rate": ratio(asset_opens, views),
        "workbuddy_open_rate": ratio(wb_opens, asset_opens),
        "first_task_rate": ratio(first_tasks, wb_opens),
    }
    actions = []
    if views < THRESHOLDS["min_views"]:
        verdict = "样本不足，不下结论（< %d 播放）" % THRESHOLDS["min_views"]
    else:
        if metrics["completion_rate"] is not None and metrics["completion_rate"] < THRESHOLDS["completion_rate"]:
            actions.append(("完播低", "前 3 秒先给结论，删掉铺垫；或把片长压 20%"))
        if metrics["asset_open_rate"] is not None and metrics["asset_open_rate"] < THRESHOLDS["asset_open_rate"]:
            actions.append(("资产页打开低", "换钩子/封面；结尾 CTA 提前 1–2 秒"))
        if metrics["workbuddy_open_rate"] is not None and metrics["workbuddy_open_rate"] < THRESHOLDS["workbuddy_open_rate"]:
            actions.append(("WorkBuddy 打开低", "改 CTA 文案与资产页首屏；二维码放大"))
        if metrics["first_task_rate"] is not None and metrics["first_task_rate"] < THRESHOLDS["first_task_rate"]:
            actions.append(("首次任务低", "补 3 个可复制任务与上手演示，不要只放功能介绍"))
        verdict = "保持" if not actions else "需要改：%s" % "、".join(a[0] for a in actions)
    return {
        "status": "ok",
        "published_at": data.get("published_at"),
        "platforms": data.get("platforms") or [],
        "baseline": data.get("baseline") or {},
        "metrics": metrics,
        "verdict": verdict,
        "actions": [{"problem": p, "action": a} for p, a in actions],
        "thresholds": THRESHOLDS,
    }


def parse_args():
    p = argparse.ArgumentParser(description="发布数据回流分析")
    p.add_argument("--run-dir")
    p.add_argument("--input")
    return p.parse_args()


def main():
    args = parse_args()
    if args.input:
        path = Path(args.input)
    elif args.run_dir:
        path = Path(args.run_dir) / "_pipeline" / "retro-data.json"
    else:
        raise SystemExit("需要 --run-dir 或 --input")
    if not path.exists():
        raise SystemExit("数据文件不存在：%s" % path)
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(analyze(data), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
