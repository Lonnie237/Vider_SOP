#!/usr/bin/env python3
"""D3 数据与故事板：校验数据集，计算排名/增长与逐年关键帧，生成 storyboard.json。"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="D3 数据校验与故事板")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def load_dataset(path):
    data = common.load_json(path)
    years = data.get("years") or []
    series = data.get("series") or []
    if len(years) < 2:
        raise common.StageError("数据集至少需要 2 个年份")
    if len(series) < 2:
        raise common.StageError("数据集至少需要 2 条序列")
    for i, s in enumerate(series):
        if not s.get("name"):
            raise common.StageError("series[%d] 缺少 name" % i)
        values = s.get("values") or []
        if len(values) != len(years):
            raise common.StageError("series %s 的值数量 %d 与年份数量 %d 不一致" % (
                s.get("name"), len(values), len(years)))
        for v in values:
            if not isinstance(v, (int, float)):
                raise common.StageError("series %s 含非数值：%s" % (s.get("name"), v))
    if not data.get("unit"):
        data["unit"] = ""
    return data


def ranking_at(dataset, index):
    rows = [(s["name"], s["values"][index]) for s in dataset["series"]]
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    brief = common.brief(run_dir)
    voice = common.load_json(run_dir / "_pipeline" / "voice.json")
    cfg = brief.get("dataviz") or {}
    kind = cfg.get("chart", "bar-race")
    if not cfg.get("dataset"):
        raise common.StageError("brief.dataviz.dataset 未配置")
    dataset_path = common.REPO / cfg["dataset"]
    if not dataset_path.exists():
        raise common.StageError("数据集不存在：%s" % cfg["dataset"])
    dataset = load_dataset(dataset_path)

    beats = {b["id"]: b for b in voice["beats"]}
    brief_beats = {b["id"]: b for b in brief.get("beats", [])}
    total = float(voice["total_duration_s"])
    if total <= 0:
        raise common.StageError("配音总时长非法：%s" % total)

    # 逐年排名与增长
    years = dataset["years"]
    rankings = {str(y): ranking_at(dataset, i) for i, y in enumerate(years)}
    growth = {}
    for s in dataset["series"]:
        first = float(s["values"][0]) or 1.0
        last = float(s["values"][-1])
        growth[s["name"]] = round(last / first, 2)

    # 场景：标题 → 图表主体（含洞察卡）→ CTA
    b01 = beats["b01"]
    insight_beat = next((b for b in voice["beats"] if b.get("role") == "method"), None)
    if insight_beat is None:
        insight_beat = list(beats.values())[-2]
    title_end = float(b01["end"])
    race_start = title_end
    race_end = float(insight_beat["end"])
    cta_start = race_end

    keyframes = []
    for beat in voice["beats"]:
        src_beat = brief_beats.get(beat.get("id"), {})
        year = src_beat.get("year")
        if year is None:
            continue
        t = float(beat["start"]) + float(beat["duration"]) * 0.45
        keyframes.append({"t": round(t, 3), "year": int(year)})
    keyframes.sort(key=lambda x: x["t"])
    if kind != "donut" and not keyframes:
        raise common.StageError("没有任何 beat 配置 year 字段，无法驱动年份动画")

    scenes = [
        {"id": "title", "kind": "title", "start": 0.0, "end": round(title_end, 3),
         "headline": b01.get("headline"), "text": b01.get("say")},
        {"id": "race", "kind": "race", "start": round(race_start, 3), "end": round(race_end, 3),
         "insight_start": round(float(insight_beat["start"]), 3)},
        {"id": "cta", "kind": "cta", "start": round(cta_start, 3), "end": round(total, 3),
         "headline": (beats.get("b10") or insight_beat).get("headline"),
         "text": (beats.get("b10") or insight_beat).get("say")},
    ]

    knowledge = next((s for s in dataset["series"] if s["name"] in ("知识科普", "知识")), dataset["series"][0])
    final_total = sum(float(s["values"][-1]) for s in dataset["series"]) or 1.0
    shares = []
    for s in dataset["series"]:
        value = float(s["values"][-1])
        shares.append({"name": s["name"], "value": value, "color": s.get("color", "#FFFFFF"),
                       "share": round(value / final_total * 100, 1)})
    shares.sort(key=lambda x: x["value"], reverse=True)
    summary = {
        "years": years,
        "series_count": len(dataset["series"]),
        "final_total": round(final_total, 2),
        "shares": shares,
        "growth": growth,
        "growth_highlight": growth.get(knowledge["name"]),
        "highlight_name": knowledge["name"],
        "top1_by_year": {str(y): rankings[str(y)][0][0] for y in years},
        "knowledge_rank_by_year": {
            str(y): [name for name, _ in rankings[str(y)]].index(knowledge["name"]) + 1 for y in years
        },
    }

    storyboard = {
        "duration_s": round(total, 3),
        "fps": int(brief.get("spec", {}).get("fps", 30)),
        "width": int(brief.get("spec", {}).get("width", 1920)),
        "height": int(brief.get("spec", {}).get("height", 1080)),
        "scenes": scenes,
        "year_keyframes": keyframes,
        "summary": summary,
        "chart": {
            "kind": kind,
            "title": cfg.get("title", "播放量竞速"),
            "subtitle": cfg.get("subtitle", ""),
            "footnote": cfg.get("footnote", "示例数据 · 仅作演示"),
            "badge": cfg.get("badge", "示例数据"),
            "unit": dataset.get("unit", ""),
            "insight": cfg.get("insight", {}),
            "palette": cfg.get("palette", {}),
        },
    }
    common.save_json(run_dir / "_pipeline" / "storyboard.json", storyboard)

    # 数据说明（人类可读）
    series = dataset["series"]
    lines = []
    lines.append("# 数据说明 · %s" % brief["content"].get("title", ""))
    lines.append("")
    lines.append("> 数据集：`%s`。%s" % (cfg["dataset"], dataset.get("note", "")))
    lines.append("")
    lines.append("## 数据表（单位：%s）" % dataset.get("unit", ""))
    lines.append("")
    header = "| 序列 | " + " | ".join(str(y) for y in years) + " |"
    lines.append(header)
    lines.append("|---|" + "---|" * len(years))
    for s in series:
        lines.append("| %s | %s |" % (s["name"], " | ".join(str(v) for v in s["values"])))
    lines.append("")
    lines.append("## 逐年第一")
    lines.append("")
    for y in years:
        lines.append("- %s：%s（%.1f %s）" % (y, rankings[str(y)][0][0], rankings[str(y)][0][1], dataset.get("unit", "")))
    lines.append("")
    lines.append("## 七年增长倍数")
    lines.append("")
    for name, g in sorted(growth.items(), key=lambda x: x[1], reverse=True):
        lines.append("- %s：%.2f×" % (name, g))
    lines.append("")
    lines.append("## 统计口径")
    lines.append("")
    lines.append("- 数据为虚构示例，仅用于演示流水线；不代表任何真实平台或账号。")
    lines.append("- 增长倍数 = 末年值 / 首年值；排名按当年值降序。")
    lines.append("- 年份关键帧来自旁白 beat 的 year 字段，渲染器按时间插值。")
    lines.append("")
    data_md = run_dir / "02-工程" / "数据说明.md"
    data_md.parent.mkdir(parents=True, exist_ok=True)
    data_md.write_text("\n".join(lines), encoding="utf-8")
    common.save_json(run_dir / "_pipeline" / "data.json",
                     {"dataset": dataset, "summary": summary, "keyframes": keyframes})

    common.emit({
        "status": "ok",
        "artifacts": [common.repo_rel(data_md), common.repo_rel(run_dir / "_pipeline" / "storyboard.json")],
        "metrics": {"series": len(series), "years": len(years), "scenes": len(scenes),
                    "keyframes": len(keyframes), "highlight": knowledge["name"],
                    "growth": summary["growth_highlight"], "chart": kind,
                    "final_total": summary["final_total"]},
        "note": "数据校验通过：%d 条序列 × %d 年（%s），%d 个关键帧" % (
            len(series), len(years), kind, len(keyframes)),
    })


if __name__ == "__main__":
    try:
        main()
    except common.StageError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)