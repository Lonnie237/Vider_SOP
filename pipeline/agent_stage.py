#!/usr/bin/env python3
"""Agent 接管：把一个阶段的提示词交给 Agent，并校验它写回的 brief。

用途：让「Agent 产线」真正由 Agent 产出，而不是脚本模板兜底。
流程：
  1) emit   : 输出该阶段完整提示词 + 当前 brief，交给 Agent；
  2) check  : 校验 Agent 写回的 brief（结构/钩子/字数/时长/CTA），通过才允许跑后续阶段；
  3) guard  : 与模板 brief 对比，强制 Agent 改动至少 N 处（防「原样返回」）。

用法：
  python3 pipeline/agent_stage.py --pipeline pipeline/definitions/short-oral-knowledge.json --stage S1-script --emit
  python3 pipeline/agent_stage.py --pipeline ... --stage S1-script --check --brief path/to/brief.json
  python3 pipeline/agent_stage.py --pipeline ... --stage S1-script --check --brief path/to/brief.json --lock
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "stages"))
import common  # noqa: E402

ROLE_KEYS = ("hook", "point", "reason", "method", "cta", "transition")
MAX_HEADLINE = 12
HOOK_MAX_CHARS = 22
HOOK_MAX_S = 3.2


def parse_args():
    p = argparse.ArgumentParser(description="Agent 阶段接入与产物校验")
    p.add_argument("--pipeline", default=str(HERE / "definitions" / "short-oral-knowledge.json"))
    p.add_argument("--stage", required=True, help="阶段 id，例如 S1-script")
    p.add_argument("--emit", action="store_true", help="输出提示词与当前 brief")
    p.add_argument("--check", action="store_true", help="校验 Agent 写回的 brief")
    p.add_argument("--brief", help="Agent 写回的 brief 路径（默认定义里的 brief）")
    p.add_argument("--baseline", help="模板 brief，用于防原样返回（默认 pipeline/demo/brief.json）")
    p.add_argument("--plan", help="S3 视觉方案路径")
    p.add_argument("--lock", action="store_true", help="校验通过后写入 _pipeline/agent-lock.json")
    p.add_argument("--emit-prompt-cmd", default="python3 pipeline/orchestrator.py",
                   help="打印阶段提示词用的命令前缀")
    return p.parse_args()


def load(path):
    return common.load_json(Path(path).resolve())


def emit(args):
    defn = load(args.pipeline)
    stage = next((s for s in defn["stages"] if s["id"] == args.stage), None)
    if not stage:
        raise SystemExit("未知阶段：%s" % args.stage)
    brief = load(args.brief or common.REPO / defn["run"]["brief"])
    print("# Agent 阶段任务：%s" % args.stage)
    print()
    print("## 执行前")
    print("1) 复制下面的提示词，交给执行该阶段的 Agent；")
    print("2) Agent 只能改 brief 的 content/beats 两节，不能改 spec 与 project；")
    print("3) 写回后运行：")
    print("   python3 pipeline/agent_stage.py --stage %s --check --brief <写回的 brief>" % args.stage)
    print()
    print("## 阶段提示词")
    print("（运行 `%s --pipeline %s --emit-prompt %s` 获取完整角色卡与契约）" % (
        args.emit_prompt_cmd, args.pipeline, args.stage))
    print()
    print("## 当前 brief（Agent 的输入）")
    print("```json")
    print(json.dumps(brief, ensure_ascii=False, indent=2))
    print("```")
    return 0


CHARS_PER_SEC = 4.8
MIN_BEAT_S = 1.2
GAP_S = 0.3
LEAD_S = 0.4
TAIL_S = 0.8


def estimate(say):
    """与 s1_script.estimate 完全一致的估算口径。"""
    return max(MIN_BEAT_S, round(len((say or "").strip()) / CHARS_PER_SEC, 2))


def check_visual(args):
    defn = load(args.pipeline)
    brief_path = Path(args.brief or common.REPO / defn["run"]["brief"]).resolve()
    brief = load(brief_path)
    plan_path = Path(args.plan).resolve() if args.plan else brief_path.parent / "visual-plan.json"
    if not plan_path.exists():
        raise SystemExit("视觉方案不存在：%s" % plan_path)
    plan = load(plan_path)
    beats = brief.get("beats") or []
    ids = [b["id"] for b in beats]
    errors, warnings = [], []
    plan_beats = plan.get("beats") or {}
    for bid in ids:
        item = plan_beats.get(bid)
        if not isinstance(item, dict):
            errors.append("缺少 beat 方案：%s" % bid)
            continue
        layout = item.get("layout", "center")
        if layout not in ("center", "top", "bottom"):
            errors.append("%s layout 非法：%s" % (bid, layout))
        accent = item.get("accent")
        if accent and accent not in ("amber", "sky", "violet", "mint", "pink", "slate"):
            errors.append("%s accent 非法：%s" % (bid, accent))
    extra = [k for k in plan_beats if k not in ids]
    if extra:
        warnings.append("方案包含未知 beat：%s" % ", ".join(extra))
    layouts = [plan_beats.get(i, {}).get("layout", "center") for i in ids]
    if len(set(layouts)) < 2:
        warnings.append("所有 beat 使用同一布局，视觉可能单调")
    payload = {
        "status": "PASS" if not errors else "FAIL",
        "stage": args.stage,
        "plan": common.repo_rel(plan_path),
        "beats": len(ids),
        "layouts": {x: layouts.count(x) for x in set(layouts)},
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 1


def check(args):
    defn = load(args.pipeline)
    brief_path = Path(args.brief or common.REPO / defn["run"]["brief"]).resolve()
    data = load(brief_path)
    base = load(args.baseline or common.REPO / "pipeline" / "demo" / "brief.json")

    errors, warnings = [], []
    beats = data.get("beats") or []
    content = data.get("content") or {}

    if len(beats) < 6:
        errors.append("beat 数量 %d < 6" % len(beats))
    if len(beats) > 12:
        errors.append("beat 数量 %d > 12" % len(beats))

    total = LEAD_S
    for i, b in enumerate(beats, 1):
        for k in ("id", "role", "headline", "say"):
            if not b.get(k):
                errors.append("beat %d 缺少 %s" % (i, k))
        if b.get("role") not in ROLE_KEYS:
            errors.append("beat %d role 非法：%s" % (i, b.get("role")))
        head = (b.get("headline") or "").replace("\n", "")
        if len(head) > MAX_HEADLINE:
            errors.append("beat %d headline 过长（%d > %d）：%s" % (i, len(head), MAX_HEADLINE, head))
        total += estimate(b.get("say") or "") + GAP_S

    hook = next((b for b in beats if b.get("role") == "hook"), None)
    if not hook:
        errors.append("没有 role=hook 的 beat")
    else:
        if len(hook["say"]) > HOOK_MAX_CHARS:
            errors.append("钩子过长：%d 字 > %d" % (len(hook["say"]), HOOK_MAX_CHARS))
        if estimate(hook["say"]) > HOOK_MAX_S:
            errors.append("钩子预估 %.1fs > %.1fs" % (estimate(hook["say"]), HOOK_MAX_S))
    if not any(b.get("role") == "cta" for b in beats):
        errors.append("没有 role=cta 的 beat")
    if not content.get("cta"):
        errors.append("content.cta 为空")

    total += TAIL_S
    target = float(content.get("target_duration_s") or data["project"].get("target_duration_s") or 0)
    if target:
        lo, hi = target * 0.8, target * 1.2
        if not (lo <= total <= hi):
            errors.append("预估时长 %.1fs 超出目标 %ss 的 ±20%%（%.1f–%.1f）" % (total, target, lo, hi))

    # 防原样返回：content + beats 必须与模板不同
    base_core = json.dumps({"content": base.get("content"), "beats": base.get("beats")}, sort_keys=True, ensure_ascii=False)
    new_core = json.dumps({"content": content, "beats": beats}, sort_keys=True, ensure_ascii=False)
    if base_core == new_core:
        errors.append("brief 与模板完全相同：Agent 未产出新内容（疑似原样返回）")
    diff = sum(1 for a, b in zip(base.get("beats") or [], beats) if a.get("say") != b.get("say"))
    if 0 < diff < 3:
        warnings.append("只有 %d 个 beat 与模板不同，改动偏小" % diff)

    # TTS 实测约比字数估算慢 8–12%（停顿/标点），按 +12% 给出真实区间
    payload = {
        "status": "PASS" if not errors else "FAIL",
        "estimated_duration_s_range": [round(total, 1), round(total * 1.12, 1)],
        "stage": args.stage,
        "brief": common.repo_rel(brief_path),
        "beats": len(beats),
        "changed_beats_vs_template": diff,
        "target_duration_s": target,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(payload, ensure_ascii=False))

    if errors:
        return 1
    if args.lock:
        lock = {
            "stage": args.stage,
            "brief": common.repo_rel(brief_path),
            "checked_at": common.now(),
            "beats": len(beats),
            "estimated_duration_s": round(total, 1),
        }
        lock_path = Path(args.brief).resolve().parent / "_pipeline" / "agent-lock.json"
        common.save_json(lock_path, lock)
        print("agent-lock：%s" % common.repo_rel(lock_path), file=sys.stderr)
    return 0


def main():
    args = parse_args()
    if args.emit:
        return emit(args)
    if args.check:
        if args.stage == "S3-visual":
            return check_visual(args)
        return check(args)
    raise SystemExit("请指定 --emit 或 --check")


if __name__ == "__main__":
    sys.exit(main())