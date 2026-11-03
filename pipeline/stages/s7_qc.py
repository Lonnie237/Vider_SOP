#!/usr/bin/env python3
"""S7 质检：调用 qc-deliver 技能核验成片，生成 QC 报告与成片说明。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="S7 自动质检")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def find_final(run_dir):
    finals = sorted((run_dir / "05-交付" / "final").glob("*.mp4"))
    if not finals:
        raise common.StageError("05-交付/final 下没有成片")
    return finals[-1]


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    final = find_final(run_dir)
    qc_script = common.REPO / "skills" / "qc-deliver" / "scripts" / "qc.py"
    proc = common.run_soft([sys.executable, str(qc_script),
                            "--project", str(run_dir), "--input", str(final),
                            "--duration-tolerance", "2", "--bitrate-tolerance", "0.35", "--json"])
    if proc.returncode not in (0, 1):
        raise common.StageError("qc.py 执行失败（exit %d）：%s" % (
            proc.returncode, (proc.stderr or "").strip().splitlines()[-8:]))
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise common.StageError("qc.py 输出不是合法 JSON：%s" % exc)
    checks = report.get("checks", [])
    status = report.get("status", "FAIL")

    qc_md = run_dir / "05-交付" / "QC报告.md"
    lines = []
    lines.append("# QC 报告 · %s" % run_dir.name)
    lines.append("")
    lines.append("- 成片：%s" % common.repo_rel(final))
    lines.append("- 结果：**%s**" % status)
    lines.append("- 统计：%s" % json.dumps(report.get("summary", {}), ensure_ascii=False))
    lines.append("- 生成时间：%s" % common.now())
    lines.append("")
    lines.append("| 检查项 | 期望 | 实测 | 结果 | 备注 |")
    lines.append("|---|---|---|---|---|")
    for check in checks:
        lines.append("| %s | %s | %s | %s | %s |" % (
            str(check.get("name", "")).replace("|", "/"),
            str(check.get("expected", "")).replace("|", "/"),
            str(check.get("actual", "")).replace("|", "/"),
            check.get("status", ""),
            str(check.get("note", "")).replace("|", "/")))
    lines.append("")
    if status != "PASS":
        lines.append("## 必须修复")
        lines.append("")
        for check in checks:
            if check.get("status") == "FAIL":
                lines.append("- %s：期望 %s，实测 %s" % (check.get("name"), check.get("expected"), check.get("actual")))
        lines.append("")
    qc_md.write_text("\n".join(lines), encoding="utf-8")

    manifest = common.manifest(run_dir)
    spec = manifest["delivery_spec"]
    info = common.media_summary(final)
    delivery_md = run_dir / "05-交付" / "成片说明.md"
    rows = []
    rows.append("# 成片说明 · %s" % manifest["project"]["name"])
    rows.append("")
    rows.append("- 成片文件：%s" % common.repo_rel(final))
    rows.append("- 画幅 / 帧率：%sx%s / %s" % (info["width"], info["height"], info["fps"]))
    rows.append("- 编码：%s + %s / %s Hz / %s 声道" % (
        info["video_codec"], info["audio_codec"], info["sample_rate"], info["channels"]))
    rows.append("- 时长：%s 秒" % info["duration_s"])
    rows.append("- 大小：%.2f MB" % info["size_mb"])
    rows.append("- 响度目标：%s LUFS" % spec.get("loudness_lufs"))
    rows.append("- 质检：**%s**（详见 QC报告.md）" % status)
    rows.append("- 封面：05-交付/封面.png")
    rows.append("- 字幕：04-字幕/srt/voice.srt（已烧录）")
    rows.append("")
    rows.append("## 工程文件")
    rows.append("")
    rows.append("- 口播稿 / 分镜：02-工程/脚本.md、分镜表.md")
    rows.append("- 配音：01-素材/音频/voice.wav（原始）、voice_norm.wav（归一后）")
    rows.append("- 底片与烧录版：03-导出/preview/base.mp4、base_av.mp4、subbed.mp4")
    rows.append("- 运行状态与报告：_pipeline/run.json、_pipeline/run-report.md")
    rows.append("")
    rows.append("## 发布前人工复核")
    rows.append("")
    rows.append("- [ ] 前 3 秒钩子是否成立（手机竖屏看一遍）")
    rows.append("- [ ] 字幕是否有错别字、是否被平台 UI 遮挡")
    rows.append("- [ ] 配音语气是否符合账号风格（可换音色重跑 S2）")
    rows.append("- [ ] 封面与标题是否与内容一致")
    delivery_md.write_text("\n".join(rows), encoding="utf-8")

    common.save_json(run_dir / "_pipeline" / "qc.json", report)
    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(qc_md), common.repo_rel(delivery_md)],
        "metrics": report.get("summary", {}),
        "qc": {"status": status, "summary": report.get("summary", {}), "input": str(final)},
        "note": "QC %s" % status,
    })
    if status != "PASS":
        print("QC 未通过，请查看 %s" % common.repo_rel(qc_md), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)