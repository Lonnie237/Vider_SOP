#!/usr/bin/env python3
"""P3 产线：按视频形态编排子 Agent 的调度器。

一条命令把「任务板 + 阶段执行 + 质检门禁 + 复盘」串起来：
  1) 读流水线定义，初始化/续用任务板；
  2) 逐阶段：start -> 跑 stage 脚本 -> done/fail（失败即停，返回非 0）；
  3) 质检阶段用 s7_qc 结果写门禁；
  4) 收尾生成复盘与运行报告。

用法：
  python3 pipeline/run_agent_pipeline.py --pipeline pipeline/definitions/short-oral-knowledge.json
  python3 pipeline/run_agent_pipeline.py --pipeline ... --from S4-audio --force
  python3 pipeline/run_agent_pipeline.py --pipeline ... --only S7-qc
  python3 pipeline/run_agent_pipeline.py --pipeline ... --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "stages"))
import common  # noqa: E402

BOARD = HERE / "board.py"
ORCH = HERE / "orchestrator.py"


def parse_args():
    p = argparse.ArgumentParser(description="P3 Agent 产线调度器")
    p.add_argument("--pipeline", default=str(HERE / "definitions" / "short-oral-knowledge.json"))
    p.add_argument("--from", dest="from_stage", help="从指定阶段开始")
    p.add_argument("--only", help="只跑一个阶段")
    p.add_argument("--force", action="store_true", help="覆盖产物重跑")
    p.add_argument("--dry-run", action="store_true", help="只打印计划，不执行")
    p.add_argument("--keep-board", action="store_true", help="不重置任务板，续用已有状态")
    return p.parse_args()


def load(path):
    from pathlib import Path as P
    return common.load_json(P(path).resolve())


def board_call(cmd_args, quiet=False):
    cmd = [sys.executable, str(BOARD)] + cmd_args
    proc = common.run_soft(cmd)
    return proc


def orch_call(cmd_args):
    cmd = [sys.executable, str(ORCH)] + cmd_args
    started = time.time()
    proc = common.run_soft(cmd, timeout=3600)
    return proc, round(time.time() - started, 1)


def summary_from_report(defn, sid):
    """编排器只打印 ok 行，阶段 JSON 落在 project/_pipeline/run.json 的 stages 摘要里。"""
    run_dir = Path(defn["run"]["root"]) / defn["run"]["dir_name"]
    state = run_dir / "_pipeline" / "run.json"
    if not state.exists():
        return {}
    try:
        data = common.load_json(state)
    except Exception:
        return {}
    for st in reversed(data.get("stages") or []):
        if st.get("id") == sid:
            return st.get("summary") or {}
    return {}


def parse_summary(stdout):
    """编排器最后几行是人读文本；阶段 JSON 摘要带 "status" 字段，按此识别。"""
    best = None
    for line in (stdout or "").strip().splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "status" in data:
            best = data
    return best or {}


def main():
    args = parse_args()
    defn = load(args.pipeline)
    stages = defn["stages"]
    ids = [s["id"] for s in stages]
    if args.only:
        if args.only not in ids:
            raise SystemExit("未知阶段：%s" % args.only)
        stages = [s for s in stages if s["id"] == args.only]
    elif args.from_stage:
        if args.from_stage not in ids:
            raise SystemExit("未知阶段：%s" % args.from_stage)
        stages = stages[ids.index(args.from_stage):]

    base = ["--pipeline", str(args.pipeline)]
    if args.dry_run:
        print("流水线：%s v%s" % (defn["name"], defn.get("version")))
        for s in stages:
            print("  %-12s %-10s %s" % (s["id"], s["role"], s.get("desc", "")))
        return 0

    # 初始化 / 续用任务板
    init_args = base + (["--init", "--force"] if (args.force or not args.keep_board) else ["--init"])
    proc = board_call(init_args)
    if proc.returncode != 0 and "已存在" not in (proc.stdout or ""):
        print((proc.stderr or proc.stdout).strip(), file=sys.stderr)
        return 1

    ok_count = 0
    for s in stages:
        sid = s["id"]
        board_call(base + ["--claim", sid, "--owner", s["role"]])
        board_call(base + ["--start"])
        print("[run ] %-12s %-10s %s" % (sid, s["role"], s.get("desc", "")))
        if sid == "S3-visual":
            plan = Path(args.pipeline).resolve().parent.parent / "demo" / "visual-plan.json"
            if plan.exists():
                run_dir = Path(defn["run"]["root"]) / defn["run"]["dir_name"]
                dst = run_dir / "_pipeline" / "visual-plan.json"
                dst.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copyfile(plan, dst)
        orch_args = ["--pipeline", str(args.pipeline), "--only", sid]
        if args.force:
            orch_args.append("--force")
        proc, elapsed = orch_call(orch_args)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
            board_call(base + ["--fail", sid, "--note", " ".join(tail)[:180]])
            board_call(base + ["--retro"])
            print("[FAIL] %-12s %5.1fs" % (sid, elapsed), file=sys.stderr)
            print("\n".join(tail), file=sys.stderr)
            return 1
        summary = summary_from_report(defn, sid)
        if not summary:
            summary = parse_summary(proc.stdout)
        note = summary.get("note") or ""
        if not note:
            metrics = summary.get("metrics") or {}
            if metrics:
                note = " ".join("%s=%s" % (k, v) for k, v in metrics.items() if not isinstance(v, (list, dict)))
            elif summary.get("qc"):
                note = "QC " + str(summary["qc"].get("status"))
            else:
                note = "ok"
        board_call(base + ["--done", sid, "--note", str(note)[:180]])
        ok_count += 1
        print("[ok  ] %-12s %5.1fs" % (sid, elapsed))

    board_call(base + ["--retro"])
    run_dir = Path(defn["run"]["root"]) / defn["run"]["dir_name"]
    retro = run_dir / "_pipeline" / "retro.md"
    print()
    print("完成阶段：%d" % ok_count)
    print("复盘：%s" % common.repo_rel(retro))
    report = run_dir / "_pipeline" / "run-report.md"
    if report.exists():
        print("运行报告：%s" % common.repo_rel(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())