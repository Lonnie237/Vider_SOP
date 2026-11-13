#!/usr/bin/env python3
"""P3 产线：任务板 + 复盘闭环（不依赖第三方库）。

产线 = 流水线定义（pipeline/definitions/*.json）+ 任务板（_pipeline/tasks.json）+ 复盘（_pipeline/retro.md）。

用法：
  python3 pipeline/board.py --pipeline definitions/short-oral-knowledge.json --init
  python3 pipeline/board.py --pipeline ... --list
  python3 pipeline/board.py --pipeline ... --claim S1-script --owner 导演
  python3 pipeline/board.py --pipeline ... --start
  python3 pipeline/board.py --pipeline ... --done S1-script --note "12 句通过校验"
  python3 pipeline/board.py --pipeline ... --fail S1-script --note "第 5 句超 60 字"
  python3 pipeline/board.py --pipeline ... --retro
  python3 pipeline/board.py --pipeline ... --status
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

BOARD = "_pipeline/tasks.json"
RETRO = "_pipeline/retro.md"
PENDING, CLAIMED, RUNNING, DONE, FAILED, BLOCKED = (
    "pending", "claimed", "running", "done", "failed", "blocked")
FINAL = (DONE, FAILED)


def parse_args():
    p = argparse.ArgumentParser(description="P3 产线任务板")
    p.add_argument("--pipeline", default=str(HERE / "definitions" / "short-oral-knowledge.json"))
    p.add_argument("--init", action="store_true", help="按流水线定义初始化任务板")
    p.add_argument("--list", action="store_true", help="列出任务")
    p.add_argument("--status", action="store_true", help="汇总状态与门禁")
    p.add_argument("--claim", help="认领阶段（stage id）")
    p.add_argument("--owner", help="认领人/Agent 名")
    p.add_argument("--start", action="store_true", help="把 ready 任务标记 running")
    p.add_argument("--done", help="标记完成")
    p.add_argument("--fail", help="标记失败")
    p.add_argument("--block", help="标记阻塞")
    p.add_argument("--note", default="", help="结果说明/失败原因")
    p.add_argument("--show-note", help="打印某任务的说明")
    p.add_argument("--retro", action="store_true", help="生成复盘草稿")
    p.add_argument("--force", action="store_true", help="允许覆盖已有任务板")
    return p.parse_args()


def load_definition(path):
    data = common.load_json(path)
    for key in ("name", "stages", "run"):
        if key not in data:
            raise SystemExit("流水线定义缺少字段：%s" % key)
    return data


def board_path(definition):
    return REPO / definition["run"]["root"] / definition["run"]["dir_name"] / BOARD


def retro_path(definition):
    return REPO / definition["run"]["root"] / definition["run"]["dir_name"] / RETRO


def new_board(definition):
    tasks = []
    for st in definition["stages"]:
        tasks.append({
            "id": st["id"],
            "role": st["role"],
            "desc": st.get("desc", ""),
            "script": st.get("script", ""),
            "status": PENDING,
            "owner": None,
            "attempts": 0,
            "note": "",
            "updated_at": common.now(),
        })
    return {
        "pipeline": definition["name"],
        "version": definition.get("version", "0"),
        "run_dir": str(Path(definition["run"]["root"]) / definition["run"]["dir_name"]),
        "created_at": common.now(),
        "tasks": tasks,
    }


def find(board, tid):
    for t in board["tasks"]:
        if t["id"] == tid:
            return t
    raise SystemExit("未知任务：%s" % tid)


def ready_ids(board):
    ids = [t["id"] for t in board["tasks"]]
    first_open = next((t["id"] for t in board["tasks"] if t["status"] not in FINAL), None)
    return first_open, ids


def save(definition, board):
    common.save_json(board_path(definition), board)


def show(board):
    print("| 状态 | 任务 | 角色 | 负责 | 尝试 | 说明 |")
    print("|---|---|---|---|---|---|")
    for t in board["tasks"]:
        print("| %s | %s | %s | %s | %d | %s |" % (
            t["status"], t["id"], t["role"], t["owner"] or "-", t["attempts"],
            (t["note"] or "").replace("|", "/")[:48]))


def summary(board):
    counts = {}
    for t in board["tasks"]:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    first_open, ids = ready_ids(board)
    gate = "可完成" if first_open is None else "未完成：%s" % first_open
    return counts, gate


def write_retro(definition, board):
    path = retro_path(definition)
    path.parent.mkdir(parents=True, exist_ok=True)
    counts, gate = summary(board)
    total = sum(t["attempts"] for t in board["tasks"])
    slow = [t for t in board["tasks"] if t["attempts"] > 1 or t["status"] == FAILED]
    lines = [
        "# 复盘 · %s" % board["pipeline"],
        "",
        "- 流水线版本：%s" % board["version"],
        "- 运行目录：%s" % board["run_dir"],
        "- 任务总尝试次数：%d" % total,
        "- 门禁：%s" % gate,
        "",
        "## 任务",
        "",
        "| 状态 | 任务 | 角色 | 负责 | 尝试 | 说明 |",
        "|---|---|---|---|---|---|",
    ]
    for t in board["tasks"]:
        lines.append("| %s | %s | %s | %s | %d | %s |" % (
            t["status"], t["id"], t["role"], t["owner"] or "-", t["attempts"],
            (t["note"] or "").replace("|", "/")[:60]))
    lines.append("")
    lines.append("## 返工点")
    lines.append("")
    if slow:
        for t in slow:
            lines.append("- %s（%s）：尝试 %d 次；说明：%s" % (
                t["id"], t["status"], t["attempts"], t["note"] or "未记录"))
    else:
        lines.append("- 无返工（所有任务一次通过或未开始）")
    lines.append("")
    lines.append("## 结论")
    lines.append("")
    lines.append("- 数据：%s" % json.dumps(counts, ensure_ascii=False))
    lines.append("- 门禁：%s" % gate)
    lines.append("- 待补：真实数据回流后回填工时与发布数据。")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    args = parse_args()
    definition = load_definition(args.pipeline)
    path = board_path(definition)
    if args.init:
        if path.exists() and not args.force:
            print("任务板已存在：%s（加 --force 覆盖）" % common.repo_rel(path))
            return 1
        board = new_board(definition)
        save(definition, board)
        print("已初始化任务板：%s（%d 个阶段）" % (common.repo_rel(path), len(board["tasks"])))
        return 0
    if not path.exists():
        print("任务板不存在，请先 --init：%s" % common.repo_rel(path))
        return 1
    board = common.load_json(path)

    if args.claim:
        t = find(board, args.claim)
        if t["status"] in FINAL:
            print("任务已结束：%s" % t["status"])
            return 1
        t["status"] = CLAIMED
        t["owner"] = args.owner or t["owner"] or "lead"
        t["updated_at"] = common.now()
        save(definition, board)
        print("已认领 %s（%s）" % (t["id"], t["owner"]))
        return 0

    if args.start:
        first_open, _ = ready_ids(board)
        if first_open is None:
            print("全部任务已结束")
            return 0
        t = find(board, first_open)
        t["status"] = RUNNING
        t["owner"] = t["owner"] or "lead"
        t["attempts"] += 1
        t["updated_at"] = common.now()
        save(definition, board)
        print("开始 %s（第 %d 次）" % (t["id"], t["attempts"]))
        return 0

    for flag, status in ((args.done, DONE), (args.fail, FAILED), (args.block, BLOCKED)):
        if flag:
            t = find(board, flag)
            t["status"] = status
            t["note"] = args.note.strip()[:200]
            t["updated_at"] = common.now()
            save(definition, board)
            print("%s -> %s：%s" % (t["id"], status, t["note"] or "-"))
            return 0

    if args.retro:
        p = write_retro(definition, board)
        print("复盘已生成：%s" % common.repo_rel(p))
        return 0

    if args.show_note:
        t = find(board, args.show_note)
        print(t.get("note") or "")
        return 0

    if args.status:
        counts, gate = summary(board)
        print("数据：%s" % json.dumps(counts, ensure_ascii=False))
        print("门禁：%s" % gate)
        return 0

    show(board)
    counts, gate = summary(board)
    print()
    print("数据：%s" % json.dumps(counts, ensure_ascii=False))
    print("门禁：%s" % gate)
    return 0


if __name__ == "__main__":
    sys.exit(main())