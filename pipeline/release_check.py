#!/usr/bin/env python3
"""P4 发布门禁：检查四类形态、Agent 阶段、真实数据、数据回流是否齐备。

用法：
  python3 pipeline/release_check.py
  python3 pipeline/release_check.py --json

不通过时退出码 1；只缺真实投放数据时退出码 0，但明确标注“待真实数据”。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE / "stages"))
import common  # noqa: E402

FORMS = [
    ("口播知识", "short-oral-knowledge.json", "demo-oral"),
    ("数据动画（真实数据）", "data-viz-real.json", "demo-data-viz-real"),
    ("教程长视频", "long-tutorial.json", "demo-long-tutorial"),
    ("产品宣传片", "product-promo-collector.json", "demo-product-promo-collector"),
]
AGENT_RUN = ("Agent 阶段", "short-oral-knowledge-agent.json", "demo-oral-agent")


def qc_status(run_dir):
    report = run_dir / "05-交付" / "QC报告.md"
    if not report.exists():
        return "missing", ""
    text = report.read_text(encoding="utf-8")
    if "结果：**PASS**" in text:
        return "PASS", common.repo_rel(report)
    return "FAIL", common.repo_rel(report)


def final_video(run_dir):
    finals = sorted((run_dir / "05-交付" / "final").glob("*.mp4"))
    if not finals:
        return None
    return finals[-1]


def board_gate(run_dir):
    path = run_dir / "_pipeline" / "tasks.json"
    if not path.exists():
        return "missing"
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("tasks") or []
    if tasks and all(t.get("status") == "done" for t in tasks):
        return "done"
    return "unfinished"


def retro_status(run_dir):
    path = run_dir / "_pipeline" / "retro-data.json"
    if not path.exists():
        return "missing", ""
    data = json.loads(path.read_text(encoding="utf-8"))
    note = data.get("note") or ""
    if "示例" in note:
        return "sample", note
    return "real", note


def check_form(name, definition, run_name):
    run_dir = REPO / "pipeline" / "runs" / run_name
    video = final_video(run_dir)
    qc, qc_path = qc_status(run_dir)
    gate = board_gate(run_dir)
    ok = bool(video) and qc == "PASS" and gate == "done"
    return {
        "form": name,
        "definition": common.repo_rel(REPO / "pipeline" / "definitions" / definition),
        "run_dir": common.repo_rel(run_dir),
        "video": common.repo_rel(video) if video else None,
        "qc": qc,
        "qc_report": qc_path,
        "board": gate,
        "ok": ok,
    }


def check_agent():
    name, definition, run_name = AGENT_RUN
    run_dir = REPO / "pipeline" / "runs" / run_name
    video = final_video(run_dir)
    qc, _ = qc_status(run_dir)
    artifacts = [
        REPO / "pipeline" / "demo" / "brief-agent-s1.json",
        REPO / "pipeline" / "demo" / "visual-plan.json",
        REPO / "pipeline" / "demo" / "subtitle-plan.json",
    ]
    present = [common.repo_rel(p) for p in artifacts if p.exists()]
    ok = len(present) == 3 and qc == "PASS" and bool(video)
    return {"form": name, "artifacts": present, "qc": qc, "video": common.repo_rel(video) if video else None, "ok": ok}


def main():
    p = argparse.ArgumentParser(description="P4 发布门禁")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    forms = [check_form(*x) for x in FORMS]
    agent = check_agent()
    real_data = REPO / "pipeline" / "demo" / "data-viz-real" / "dataset.json"
    real_ok = real_data.exists() and '"source"' in real_data.read_text(encoding="utf-8")
    product_run = REPO / "pipeline" / "runs" / "demo-product-promo-collector"
    retro, retro_note = retro_status(product_run)

    all_forms = all(f["ok"] for f in forms)
    gate = "PASS" if (all_forms and agent["ok"] and real_ok) else "FAIL"
    data_gate = "real" if retro == "real" else ("机制就绪，待真实数据" if retro == "sample" else "未接入")
    payload = {
        "gate": gate,
        "forms": forms,
        "agent": agent,
        "real_data": {"ok": real_ok, "dataset": common.repo_rel(real_data)},
        "retro": {"status": retro, "note": retro_note},
        "data_gate": data_gate,
        "summary": {
            "forms_ok": sum(1 for f in forms if f["ok"]),
            "forms_total": len(forms),
            "agent_ok": agent["ok"],
            "real_data_ok": real_ok,
            "data_gate": data_gate,
        },
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("P4 发布门禁")
        print("")
        print("| 形态 | 成片 | QC | 任务板 | 结论 |")
        print("|---|---|---|---|---|")
        for f in forms:
            print("| %s | %s | %s | %s | %s |" % (
                f["form"], "有" if f["video"] else "缺", f["qc"], f["board"], "PASS" if f["ok"] else "FAIL"))
        print("| Agent 阶段 | %s | %s | - | %s |" % (
            "有" if agent["video"] else "缺", agent["qc"], "PASS" if agent["ok"] else "FAIL"))
        print("")
        print("真实数据：%s" % ("PASS" if real_ok else "FAIL"))
        print("数据回流：%s" % data_gate)
        print("门禁：%s" % gate)
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
