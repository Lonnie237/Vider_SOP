#!/usr/bin/env python3
"""口播知识端到端流水线编排器（不依赖第三方库）。

用法：
  python3 pipeline/orchestrator.py --plan                 # 查看阶段与角色
  python3 pipeline/orchestrator.py                        # 全量运行（默认 demo）
  python3 pipeline/orchestrator.py --force                # 覆盖已有产物重跑
  python3 pipeline/orchestrator.py --from S4-audio        # 从某阶段续跑
  python3 pipeline/orchestrator.py --only S7-qc           # 只跑某阶段
  python3 pipeline/orchestrator.py --emit-prompt S1-script  # 输出该阶段给 Agent 的提示词

产物：项目目录（默认 pipeline/runs/demo-oral/）+ _pipeline/run.json + _pipeline/run-report.md。
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE / "stages"))
import common  # noqa: E402

DEFAULT_DEF = HERE / "definitions" / "short-oral-knowledge.json"


def parse_args():
    p = argparse.ArgumentParser(description="视频流水线编排器")
    p.add_argument("--pipeline", default=str(DEFAULT_DEF), help="流水线定义 JSON")
    p.add_argument("--run-id", help="覆盖定义中的 dir_name")
    p.add_argument("--force", action="store_true", help="覆盖已有产物重跑")
    p.add_argument("--from", dest="from_stage", help="从指定 stage id 开始")
    p.add_argument("--only", help="只运行指定 stage id")
    p.add_argument("--plan", action="store_true", help="只打印阶段计划")
    p.add_argument("--emit-prompt", help="打印指定 stage 的 Agent 提示词")
    p.add_argument("--quiet", action="store_true")
    return p.parse_args()


def load_definition(path):
    data = common.load_json(path)
    for key in ("name", "stages", "run"):
        if key not in data:
            raise SystemExit("流水线定义缺少字段：%s" % key)
    return data


def stage_script(definition, stage):
    return HERE / "stages" / stage["script"]


def run_one(definition, stage, project_dir, force, quiet):
    script = stage_script(definition, stage)
    if not script.exists():
        raise SystemExit("阶段脚本不存在：%s" % common.repo_rel(script))
    if stage["id"] == definition["stages"][0]["id"]:
        run_cfg = definition["run"]
        cmd = [sys.executable, str(script),
               "--root", str(REPO / run_cfg["root"]),
               "--dir-name", run_cfg["dir_name"],
               "--brief", str(REPO / run_cfg["brief"])]
        if force:
            cmd.append("--force")
    else:
        cmd = [sys.executable, str(script), "--run-dir", str(project_dir)]
        if force:
            cmd.append("--force")
    started = time.time()
    proc = common.run_soft(cmd, timeout=1800)
    elapsed = round(time.time() - started, 2)
    output = (proc.stdout or "").strip()
    summary = None
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                summary = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if proc.returncode != 0:
        detail = (proc.stderr or output).strip().splitlines()[-15:]
        return {"id": stage["id"], "role": stage["role"], "status": "failed",
                "seconds": elapsed, "error": "\n".join(detail)}
    if not quiet:
        print("[ok] %-12s %5.1fs  %s" % (stage["id"], elapsed, stage.get("desc", "")))
    return {"id": stage["id"], "role": stage["role"], "status": "ok",
            "seconds": elapsed, "summary": summary or {}}


def emit_prompt(definition, stage):
    role_path = HERE / "roles" / (stage["role"] + ".md")
    role_text = role_path.read_text(encoding="utf-8") if role_path.exists() else "（缺少角色卡）"
    cmd = "python3 pipeline/stages/%s --run-dir pipeline/runs/%s" % (
        stage["script"], definition["run"]["dir_name"])
    print("# 阶段提示词：%s（%s）" % (stage["id"], stage["desc"]))
    print()
    print("你是本阶段的执行 Agent，角色：**%s**。只负责本阶段，不越界。" % stage["role"])
    print()
    print("## 角色卡")
    print(role_text)
    print()
    print("## 输入 / 输出契约")
    print("- 输入：项目目录 pipeline/runs/%s（初始化阶段例外）" % definition["run"]["dir_name"])
    print("- 调用：%s" % cmd)
    print("- 成功：退出码 0，stdout 末行打印 JSON 摘要 {status, artifacts, metrics}")
    print("- 失败：退出码非 0，stderr 含失败原因；不要伪造成功")
    print()
    print("## 禁止")
    print("- 不修改其他阶段产物；不修改 scripts/、docs/、templates/。")
    print("- 不跳过质检；QC FAIL 必须如实上报。")


def write_report(state, definition, status, report_path):
    lines = []
    lines.append("# 流水线运行报告 · %s" % state["run_id"])
    lines.append("")
    lines.append("- 流水线：%s v%s" % (definition["name"], definition["version"]))
    lines.append("- 项目目录：%s" % common.repo_rel(state["project_dir"]))
    lines.append("- 状态：**%s**" % ("成功" if status == "ok" else "失败"))
    lines.append("- 开始 / 结束：%s / %s" % (state["started_at"], state["updated_at"]))
    lines.append("- 总耗时：%.1fs" % state["elapsed_s"])
    lines.append("")
    lines.append("## 阶段")
    lines.append("")
    lines.append("| 阶段 | 角色 | 状态 | 耗时 | 摘要 |")
    lines.append("|---|---|---|---|---|")
    for st in state["stages"]:
        summary = st.get("summary") or {}
        note = summary.get("note") or summary.get("metrics") or ""
        if isinstance(note, (dict, list)):
            note = json.dumps(note, ensure_ascii=False)
        note = str(note).replace("|", "/")[:90]
        lines.append("| %s | %s | %s | %.1fs | %s |" % (
            st["id"], st["role"], st.get("status"), st.get("seconds", 0), note))
    lines.append("")
    lines.append("## 产物")
    lines.append("")
    for item in state.get("artifacts", []):
        lines.append("- %s" % item)
    lines.append("")
    qc = state.get("qc") or {}
    if qc:
        lines.append("## 质检")
        lines.append("")
        lines.append("- 结果：**%s**" % qc.get("status"))
        lines.append("- 统计：%s" % json.dumps(qc.get("summary", {}), ensure_ascii=False))
        if qc.get("input"):
            lines.append("- 成片：%s" % common.repo_rel(qc["input"]))
        lines.append("")
    if status != "ok":
        lines.append("## 失败原因")
        lines.append("")
        for st in state["stages"]:
            if st.get("status") == "failed":
                lines.append("- %s：%s" % (st["id"], st.get("error", "")[:800]))
        lines.append("")
    lines.append("## 下一步")
    lines.append("")
    lines.append("- 人工看片：检查前 3 秒钩子、字幕安全区、声画同步。")
    lines.append("- 修改脚本或参数后：python3 pipeline/orchestrator.py --from S1-script --force")
    lines.append("- 发布前按 05-交付/QC报告.md 与平台后台复核。")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()
    definition = load_definition(args.pipeline)
    if args.plan:
        print("流水线：%s v%s" % (definition["name"], definition["version"]))
        print("SOP：%s" % definition.get("sop"))
        print()
        print("| # | 阶段 | 角色 | 脚本 | 说明 |")
        print("|---|---|---|---|---|")
        for i, st in enumerate(definition["stages"], 1):
            print("| %d | %s | %s | %s | %s |" % (i, st["id"], st["role"], st["script"], st["desc"]))
        return
    if args.emit_prompt:
        stage = next((s for s in definition["stages"] if s["id"] == args.emit_prompt), None)
        if not stage:
            raise SystemExit("未知阶段：%s" % args.emit_prompt)
        emit_prompt(definition, stage)
        return

    run_cfg = definition["run"]
    if args.run_id:
        run_cfg["dir_name"] = args.run_id
    root = REPO / run_cfg["root"]
    project_dir = root / run_cfg["dir_name"]

    stages = definition["stages"]
    if args.only:
        stages = [s for s in stages if s["id"] == args.only]
        if not stages:
            raise SystemExit("未知阶段：%s" % args.only)
    elif args.from_stage:
        ids = [s["id"] for s in stages]
        if args.from_stage not in ids:
            raise SystemExit("未知阶段：%s" % args.from_stage)
        stages = stages[ids.index(args.from_stage):]

    state = {
        "run_id": run_cfg["dir_name"],
        "project_dir": str(project_dir),
        "definition": str(Path(args.pipeline).resolve()),
        "started_at": common.now(),
        "updated_at": common.now(),
        "elapsed_s": 0,
        "stages": [],
        "artifacts": [],
        "qc": None,
    }
    t0 = time.time()
    status = "ok"
    for stage in stages:
        if args.only and stage["id"] != stages[0]["id"] and not project_dir.exists():
            raise SystemExit("项目目录不存在，请先运行初始化：%s" % project_dir)
        result = run_one(definition, stage, project_dir, args.force, args.quiet)
        if stage["id"] == definition["stages"][0]["id"] and result.get("status") == "ok":
            info = result.get("summary") or {}
            project_dir = Path(info.get("project_dir", project_dir))
            state["project_dir"] = str(project_dir)
        state["stages"].append(result)
        summary = result.get("summary") or {}
        for art in summary.get("artifacts", []):
            state["artifacts"].append(art)
        if summary.get("qc"):
            state["qc"] = summary["qc"]
        state["updated_at"] = common.now()
        state["elapsed_s"] = round(time.time() - t0, 1)
        if result.get("status") != "ok":
            status = "failed"
            common.save_json(common.state_path(project_dir), state)
            write_report(state, definition, status, project_dir / "_pipeline" / "run-report.md")
            print(state["stages"][-1].get("error", ""), file=sys.stderr)
            print("流水线失败：%s" % stage["id"], file=sys.stderr)
            return 1
        common.save_json(common.state_path(project_dir), state)

    report_path = project_dir / "_pipeline" / "run-report.md"
    write_report(state, definition, status, report_path)
    print()
    print("流水线完成：%s" % common.repo_rel(project_dir))
    print("运行报告：%s" % common.repo_rel(report_path))
    final = [a for a in state["artifacts"] if a.endswith(".mp4") and "05-交付" in a]
    if final:
        print("成片：%s" % final[-1])
    if state.get("qc"):
        print("质检：%s" % state["qc"].get("status"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
