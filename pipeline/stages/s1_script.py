#!/usr/bin/env python3
"""S1 脚本：校验口播稿（钩子 / 字数 / 预估时长），生成 脚本.md 与 分镜表.md。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

CHARS_PER_SEC = 4.8
MIN_BEAT_S = 1.2
GAP_S = 0.3
LEAD_S = 0.4
TAIL_S = 0.8
ROLES = {"hook", "point", "reason", "method", "cta", "transition"}


def parse_args():
    p = argparse.ArgumentParser(description="S1 校验脚本并生成分镜")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def estimate(text):
    return max(MIN_BEAT_S, round(len(text) / CHARS_PER_SEC, 2))


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    data = common.brief(run_dir)
    content = data.get("content", {})
    beats = data.get("beats") or []
    if len(beats) < 3:
        raise common.StageError("口播稿至少需要 3 个 beat，当前 %d" % len(beats))

    warnings = []
    total_chars = 0
    total_est = LEAD_S
    for i, beat in enumerate(beats, 1):
        for key in ("id", "role", "headline", "say"):
            if not beat.get(key):
                raise common.StageError("beat %d 缺少字段 %s" % (i, key))
        if beat["role"] not in ROLES:
            raise common.StageError("beat %d 的 role 非法：%s" % (i, beat["role"]))
        beat["est_s"] = estimate(beat["say"])
        total_chars += len(beat["say"])
        total_est += beat["est_s"] + (GAP_S if i < len(beats) else 0)
    total_est += TAIL_S - GAP_S + GAP_S

    hook = next((b for b in beats if b["role"] == "hook"), None)
    if not hook:
        warnings.append("没有 role=hook 的 beat：前 3 秒可能没有钩子")
    elif hook["est_s"] > 3.2 or len(hook["say"]) > 26:
        warnings.append("钩子偏长（%ss / %d 字）：建议 <= 3s、<= 24 字" % (hook["est_s"], len(hook["say"])))
    if not any(b["role"] == "cta" for b in beats):
        warnings.append("没有 role=cta 的 beat：结尾缺少行动引导")
    if total_est > 180:
        warnings.append("预估时长 %.1fs 超过短视频建议上限 180s" % total_est)

    # 脚本.md
    meta = content
    lines = []
    lines.append("# 口播脚本 · %s" % meta.get("title", data["project"]["name"]))
    lines.append("")
    lines.append("> 由 S1-script 阶段生成；口播时长按 %.1f 字/秒估算，最终以 TTS 实际时长为准。" % CHARS_PER_SEC)
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 目标受众 | %s |" % meta.get("audience", ""))
    lines.append("| 核心结论 | %s |" % meta.get("core_message", ""))
    lines.append("| CTA | %s |" % meta.get("cta", ""))
    lines.append("| beat 数 | %d |" % len(beats))
    lines.append("| 总字数 | %d |" % total_chars)
    lines.append("| 预估时长 | %.1fs |" % total_est)
    lines.append("")
    lines.append("## 口播稿")
    lines.append("")
    for i, beat in enumerate(beats, 1):
        lines.append("### %02d · %s（%s）" % (i, beat["headline"].replace("\n", " / "), beat["role"]))
        lines.append("")
        lines.append(beat["say"])
        lines.append("")
        lines.append("- 预估：%.1fs｜字数：%d" % (beat["est_s"], len(beat["say"])))
        lines.append("")
    lines.append("## 自检")
    lines.append("")
    lines.append("- 钩子在前 3 秒：" + ("是" if hook and hook["est_s"] <= 3.2 else "需检查"))
    lines.append("- 结论先行：" + ("是" if any(b["role"] == "point" for b in beats) else "需检查"))
    lines.append("- 结尾 CTA：" + ("有" if any(b["role"] == "cta" for b in beats) else "缺失"))
    lines.append("")
    if warnings:
        lines.append("## 告警")
        lines.append("")
        for wmsg in warnings:
            lines.append("- " + wmsg)
        lines.append("")
    script_md = run_dir / "02-工程" / "脚本.md"
    script_md.parent.mkdir(parents=True, exist_ok=True)
    script_md.write_text("\n".join(lines), encoding="utf-8")

    # 分镜表.md
    rows = []
    rows.append("# 分镜表 · %s" % meta.get("title", data["project"]["name"]))
    rows.append("")
    rows.append("> 由 S1-script 阶段生成；画面为图文卡（无实拍素材时的默认实现），有实拍可替换 S3 的素材来源。")
    rows.append("")
    rows.append("| # | 时间点 | 画面 / 卡片 | 口播 | 预估时长 | 备注 |")
    rows.append("|---|---|---|---|---|---|")
    t = LEAD_S
    for i, beat in enumerate(beats, 1):
        mm, ss = int(t // 60), t % 60
        rows.append("| %d | %02d:%04.1f | %s | %s | %.1fs | %s |" % (
            i, mm, ss, beat["headline"].replace("\n", " / "), beat["say"], beat["est_s"], beat["role"]))
        t += beat["est_s"] + GAP_S
    rows.append("")
    storyboard = run_dir / "分镜表.md"
    storyboard.write_text("\n".join(rows), encoding="utf-8")

    payload = {"beats": beats, "total_chars": total_chars, "estimated_duration_s": round(total_est, 1),
               "chars_per_sec": CHARS_PER_SEC, "warnings": warnings}
    common.save_json(run_dir / "_pipeline" / "script.json", payload)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(script_md), common.repo_rel(storyboard)],
        "metrics": {"beats": len(beats), "chars": total_chars, "estimated_duration_s": round(total_est, 1),
                    "hook_duration_s": hook["est_s"] if hook else None, "warnings": warnings},
        "note": "脚本与分镜已生成，预估 %.1fs" % total_est,
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
