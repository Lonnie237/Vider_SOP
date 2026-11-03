#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""init_project.py — 初始化视频项目：目录 + 立项文档 + 机器可读 manifest。

读取仓库 templates/ 下的模板（项目Brief/分镜表/交付规格/QC清单），按
项目名、视频形态、平台渲染为项目内文档；同时写出 manifest.json，
供 ffmpeg-render / qc-deliver 读取交付规格（分辨率/帧率/码率/响度）。

用法示例：
  python3 skills/video-project-init/scripts/init_project.py \
      --name "三分钟讲清楚代理剪辑" --form 口播知识 --platform 抖音 \
      --root /tmp/demo --dry-run

默认只写 --root 下的新目录，不覆盖已有内容；已存在同名非空目录时加 --force。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform as _platform
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常量

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent

DIRS = ["01-素材", "02-工程", "03-导出", "04-字幕", "05-交付"]
SUBDIRS = {
    "01-素材": ["视频", "音频", "图片"],
    "02-工程": ["工程文件", "proxy"],
    "03-导出": ["preview", "master"],
    "04-字幕": ["srt", "png"],
    "05-交付": ["final"],
}

# 平台默认档：画幅/分辨率/帧率/响度是通用交付常识；码率是本仓默认档，
# 不是平台官方推荐值，生成文档中会标注 [待确认]，发布前必须核对平台说明。
PLATFORMS = {
    "抖音":     {"aspect": "9:16", "width": 1080, "height": 1920, "fps": 30, "loudness": -14, "bitrate": 6000},
    "视频号":   {"aspect": "9:16", "width": 1080, "height": 1920, "fps": 30, "loudness": -14, "bitrate": 6000},
    "小红书":   {"aspect": "9:16", "width": 1080, "height": 1920, "fps": 30, "loudness": -14, "bitrate": 6000},
    "B站":      {"aspect": "16:9", "width": 1920, "height": 1080, "fps": 30, "loudness": -16, "bitrate": 8000},
    "YouTube":  {"aspect": "16:9", "width": 1920, "height": 1080, "fps": 30, "loudness": -14, "bitrate": 10000},
    "客户交付": {"aspect": "16:9", "width": 1920, "height": 1080, "fps": 30, "loudness": -16, "bitrate": 12000},
}

FORM_ALIASES = {"教程": "教程长视频", "口播": "口播知识", "vlog": "Vlog"}

# 形态 → SOP 路由（仅写文字引用，生成文档不写仓内相对链接，避免项目外死链）
FORM_PROFILES = {
    "口播知识":   {"sop": "sop/short-oral-knowledge", "duration": 60,  "ratio": "竖屏 9:16"},
    "混剪卡点":   {"sop": "sop/short-montage",        "duration": 30,  "ratio": "竖屏 9:16"},
    "教程长视频": {"sop": "sop/long-tutorial",        "duration": 300, "ratio": "横屏 16:9"},
    "Vlog":       {"sop": "sop/long-vlog",            "duration": 180, "ratio": "横屏 16:9"},
    "访谈":       {"sop": "sop/long-interview",       "duration": 300, "ratio": "横屏 16:9"},
    "宣传片":     {"sop": "sop/short-promo",          "duration": 60,  "ratio": "横屏 16:9"},
    "数据动画":   {"sop": "sop/short-data-viz",       "duration": 60,  "ratio": "竖屏 9:16"},
}

TEMPLATE_FILES = {
    "brief": "项目Brief.md",
    "storyboard": "分镜表.md",
    "delivery_spec": "交付规格.md",
    "qc_checklist": "QC清单.md",
}

BT = chr(96)  # Markdown 代码围栏用，避免源码里直接出现三个反引号


class InitError(Exception):
    """可预期的输入/环境错误：打印人类可读信息并以非 0 退出。"""


# ---------------------------------------------------------------- 工具函数

def run_version(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    text = out.stdout or out.stderr
    return text.splitlines()[0].strip() if text else None


def find_templates(explicit):
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser().resolve())
    candidates += [REPO_ROOT / "templates", Path.cwd() / "templates"]
    for cand in candidates:
        if all((cand / f).is_file() for f in TEMPLATE_FILES.values()):
            return cand
    raise InitError(
        "找不到模板目录。已尝试：%s\n请用 --templates 指向仓库 templates/ 目录（需含：%s）。"
        % ("、".join(str(c) for c in candidates), "、".join(TEMPLATE_FILES.values()))
    )


def read_template(tpl_dir, key):
    path = tpl_dir / TEMPLATE_FILES[key]
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InitError("读取模板失败：%s（%s）" % (path, exc))


def set_cell(text, label, value, cell=1):
    """把 Markdown 表格中第一列为 label 的行的第 cell 个单元格替换为 value。"""
    value = str(value).replace("|", "/").replace("\n", " ")
    lines = text.splitlines()
    hit = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0] == label:
            while len(cells) <= cell:
                cells.append("")
            cells[cell] = value
            lines[idx] = "| " + " | ".join(cells) + " |"
            hit = True
            break
    if not hit:
        raise InitError("模板结构变化：找不到表格行「%s」，请检查 templates/ 模板。" % label)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def replace_heading(text, prefix, title):
    return re.sub(r"^" + re.escape(prefix) + r".*$", prefix + title, text, count=1, flags=re.M)


def replace_all(text, mapping):
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


def safe_dirname(name):
    text = name.strip()
    text = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", text)
    text = re.sub(r"\s+", "-", text).strip("-. ")
    return text or "video-project"


def make_slug(name, date_str):
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "project-" + date_str.replace("-", "")


def parse_date(raw):
    if raw is None:
        return _dt.date.today().isoformat()
    try:
        return _dt.datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise InitError("--date 需要 YYYY-MM-DD 格式，收到：%s" % raw)


def validate_int(name, value, low, high):
    if not isinstance(value, int):
        raise InitError("%s 需要整数，收到：%s" % (name, value))
    if value < low or value > high:
        raise InitError("%s 越界：%s（允许 %d–%d）" % (name, value, low, high))
    return value


# ---------------------------------------------------------------- 模板渲染

def render_brief(tpl, ctx):
    text = replace_heading(tpl, "# 项目 Brief · ", ctx["name"])
    text = replace_all(text, {"<口播知识 / 混剪卡点 / 教程 / Vlog / 访谈 / 宣传片 / 数据动画>": ctx["form"]})
    text = set_cell(text, "项目名", ctx["name"])
    text = set_cell(text, "视频形态", ctx["form"])
    text = set_cell(text, "目标平台", ctx["platform"])
    text = set_cell(text, "目标时长", ctx["duration_label"])
    text = set_cell(text, "画幅 / 分辨率", "%s / %d×%d" % (ctx["aspect"], ctx["width"], ctx["height"]))
    text = set_cell(text, "交付日期", ctx["delivery_date"] or "（待定，立项后 3 天内补）")
    text = set_cell(text, "负责人", ctx["owner"])
    text = text.replace(
        "| 对应 SOP | [sop/...](../sop/) |",
        "| 对应 SOP | %s（路由以仓库 sop/README.md 为准；文件未校验存在性） |" % ctx["sop"],
    )
    text = set_cell(text, "钩子（0–3s）", "3s")
    text = text.replace("<链接>", "（填写链接）")
    text += (
        "\n> 本文件由「skills/video-project-init/scripts/init_project.py」于 %s 按"
        "「templates/项目Brief.md」渲染生成；带「（填写链接）」处需人工补齐。\n" % ctx["date"]
    )
    return text


def render_storyboard(tpl, ctx):
    text = replace_heading(tpl, "# 分镜表 · ", ctx["name"])
    text += (
        "\n> 本文件由 init_project.py 于 %s 按「templates/分镜表.md」渲染生成。"
        "分镜数量按成片时长 %s 规划，逐行补齐即可。\n" % (ctx["date"], ctx["duration_label"])
    )
    return text


def render_delivery_spec(tpl, ctx):
    text = replace_heading(tpl, "# 交付规格 · ", "%s / %s" % (ctx["name"], ctx["platform"]))
    text = set_cell(text, "分辨率", "%d×%d（%s，%s 默认档）" % (ctx["width"], ctx["height"], ctx["aspect"], ctx["platform"]))
    text = set_cell(text, "帧率", "%d fps（与素材一致优先）" % ctx["fps"])
    text = set_cell(text, "视频编码", "H.264 High（libx264）")
    text = set_cell(
        text, "码率 / 质量",
        "VBR %d kbps（本仓默认档，非平台官方值 [待确认]）；备选 CRF %d" % (ctx["bitrate"], ctx["crf"]),
    )
    text = set_cell(text, "色彩", "Rec.709 / sRGB（交付前确认无偏色）")
    text = set_cell(
        text, "音频",
        "AAC 48 kHz 立体声；响度 %d LUFS（±1 LU）" % ctx["loudness"],
    )
    text = set_cell(
        text, "字幕",
        "外挂 SRT 优先；需烧录时用 subtitle-pipeline（本机无 libass，走 Pillow overlay）",
    )
    text = set_cell(text, "封装", ".mp4（H.264 + AAC）")
    text = set_cell(text, "文件命名", "%s-<版本>-<日期>.mp4" % ctx["slug"])
    # 平台变体表：填目标平台行的码率建议（第 4 个单元格）
    lines = text.splitlines()
    variant_label = {"B站": "B 站", "客户交付": "微信 / 客户交付"}.get(ctx["platform"], ctx["platform"])
    for idx, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
        if cells and cells[0] == variant_label and len(cells) >= 4:
            cells[3] = "%d kbps（本仓默认档）" % ctx["bitrate"]
            lines[idx] = "| " + " | ".join(cells) + " |"
            break
    text = "\n".join(lines) + ("\n" if tpl.endswith("\n") else "")
    fence = BT * 3
    out_name = "../03-导出/%s-v1-%s.mp4" % (ctx["slug"], ctx["date"])
    in_name = "../01-素材/input.mp4"
    scale_chain = (
        "scale=%d:%d:force_original_aspect_ratio=decrease,"
        "pad=%d:%d:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=%d"
        % (ctx["width"], ctx["height"], ctx["width"], ctx["height"], ctx["fps"])
    )
    cmd = (
        fence + "bash\n"
        "ffmpeg -hide_banner -y -i %s \\\n"
        "  -vf \"%s\" \\\n"
        "  -c:v libx264 -preset slow -b:v %dk -maxrate %dk -bufsize %dk -profile:v high -pix_fmt yuv420p \\\n"
        "  -c:a aac -b:a 192k -ar 48000 -ac 2 -af loudnorm=I=%d:TP=-1.5:LRA=11 \\\n"
        "  -movflags +faststart %s\n"
        "%s\n"
        % (in_name, scale_chain, ctx["bitrate"], int(ctx["bitrate"] * 1.25),
           ctx["bitrate"] * 2, ctx["loudness"], out_name, fence)
    )
    pattern = fence + r"bash\n# 横屏 1080p30 H\.264 \+ AAC.*?" + fence + r"\n"
    text = re.sub(pattern, cmd, text, count=1, flags=re.S)
    text = text.replace("<项目>-<日期>-master", "%s-%s-master" % (ctx["slug"], ctx["date"]))
    text += (
        "\n> 本文件由 init_project.py 于 %s 按「templates/交付规格.md」渲染生成。"
        "分辨率/帧率/响度可用于自动渲染与质检；码率是本仓默认档，发布前按平台官方说明核对。\n" % ctx["date"]
    )
    return text


def render_qc_checklist(tpl, ctx):
    text = replace_heading(tpl, "# QC 清单 · ", ctx["name"])
    text = text.replace("../templates/交付规格.md", "../05-交付/交付规格.md")
    out_name = "../03-导出/%s-v1-%s.mp4" % (ctx["slug"], ctx["date"])
    text = text.replace("output.mp4", out_name)
    text += (
        "\n> 本文件由 init_project.py 于 %s 按「templates/QC清单.md」渲染生成；"
        "自动核对可用仓库技能 qc-deliver（脚本 scripts/qc.py）。\n" % ctx["date"]
    )
    return text


# ---------------------------------------------------------------- 主流程

def build_context(args, form, platform_profile):
    date = parse_date(args.date)
    slug = args.slug or make_slug(args.name, date)
    duration = args.duration if args.duration is not None else platform_profile.get("duration")
    if duration is None:
        duration = FORM_PROFILES[form]["duration"]
    if duration <= 0 or duration > 7200:
        raise InitError("--duration 越界：%s 秒（允许 1–7200）" % duration)
    width = validate_int("--width", args.width or platform_profile["width"], 64, 7680)
    height = validate_int("--height", args.height or platform_profile["height"], 64, 4320)
    fps = validate_int("--fps", args.fps or platform_profile["fps"], 1, 240)
    bitrate = validate_int("--video-bitrate", args.video_bitrate or platform_profile["bitrate"], 100, 200000)
    loudness = args.loudness if args.loudness is not None else platform_profile["loudness"]
    if loudness > 0 or loudness < -70:
        raise InitError("--loudness 越界：%s LUFS（允许 -70–0）" % loudness)
    return {
        "name": args.name,
        "slug": slug,
        "form": form,
        "platform": args.platform,
        "aspect": platform_profile["aspect"],
        "width": width,
        "height": height,
        "fps": fps,
        "bitrate": bitrate,
        "crf": args.crf,
        "loudness": loudness,
        "duration": duration,
        "duration_label": "%d 秒" % duration,
        "owner": args.owner,
        "date": date,
        "delivery_date": args.delivery_date,
        "sop": FORM_PROFILES[form]["sop"],
        "dir_name": args.dir_name or safe_dirname(args.name),
    }


def ensure_target(target, force):
    if target.exists():
        if not target.is_dir():
            raise InitError("目标路径已存在且不是目录：%s" % target)
        if any(target.iterdir()) and not force:
            raise InitError(
                "目标目录已存在且非空：%s\n如需写入请加 --force（只覆盖同名文件，不删除其他内容）。" % target
            )
    return target


def make_manifest(ctx, templates_dir, files, dirs):
    open_questions = []
    if not ctx["delivery_date"]:
        open_questions.append("交付日期（Brief / manifest 中为空）")
    if not ctx["owner"] or ctx["owner"] == "未指派":
        open_questions.append("负责人（当前为未指派）")
    open_questions += [
        "目标时长（当前按形态默认值 %d 秒，需确认）" % ctx["duration"],
        "参考视频链接",
        "码率/平台参数核对（当前为本仓默认档）",
    ]
    return {
        "schema_version": 1,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "generator": "skills/video-project-init/scripts/init_project.py",
        "project": {
            "name": ctx["name"],
            "slug": ctx["slug"],
            "form": ctx["form"],
            "platform": ctx["platform"],
            "aspect": ctx["aspect"],
            "owner": ctx["owner"],
            "delivery_date": ctx["delivery_date"],
        },
        "directories": dirs,
        "files": files,
        "delivery_spec": {
            "width": ctx["width"],
            "height": ctx["height"],
            "fps": ctx["fps"],
            "aspect": ctx["aspect"],
            "video_codec": "h264",
            "video_bitrate_kbps": ctx["bitrate"],
            "crf": ctx["crf"],
            "audio_codec": "aac",
            "audio_sample_rate": 48000,
            "audio_channels": 2,
            "audio_bitrate_kbps": 192,
            "loudness_lufs": ctx["loudness"],
            "container": "mp4",
            "duration_target_s": ctx["duration"],
            "max_size_mb": None,
            "naming": "%s-<version>-<date>.mp4" % ctx["slug"],
        },
        "platform_defaults_note": (
            "分辨率/帧率/响度为通用交付默认档；码率为本仓默认档，非平台官方推荐值。"
            "平台参数属易变事实，发布前按平台官方说明核对。"
        ),
        "open_questions": open_questions,
        "templates_used": {k: str(templates_dir / v) for k, v in TEMPLATE_FILES.items()},
        "tool_versions": {
            "python": _platform.python_version(),
            "ffmpeg": run_version(["ffmpeg", "-version"]),
            "pillow": _pillow_version(),
        },
    }


def _pillow_version():
    try:
        import PIL
        return getattr(PIL, "__version__", None)
    except ImportError:
        return None


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="init_project.py",
        description="初始化视频项目目录、项目Brief、分镜表、交付规格、QC清单与 manifest.json。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python3 init_project.py --name \"三分钟讲清楚代理剪辑\" --form 口播知识 \\\n"
            "      --platform 抖音 --root /tmp/demo --dry-run\n"
            "  python3 init_project.py --name demo --form 混剪卡点 --platform B站 --root /tmp/demo\n"
        ),
    )
    parser.add_argument("--name", required=True, help="项目名（会用于标题与默认目录名）")
    parser.add_argument("--form", required=True, help="视频形态：%s" % " / ".join(FORM_PROFILES))
    parser.add_argument("--platform", required=True, help="目标平台：%s" % " / ".join(PLATFORMS))
    parser.add_argument("--root", default=".", help="输出父目录，默认当前目录")
    parser.add_argument("--dir-name", help="项目目录名，默认由项目名清洗得到")
    parser.add_argument("--slug", help="英文短名（用于文件命名/manifest），默认由项目名推导")
    parser.add_argument("--duration", type=float, help="目标成片时长（秒），默认按形态")
    parser.add_argument("--width", type=int, help="覆盖平台默认宽度")
    parser.add_argument("--height", type=int, help="覆盖平台默认高度")
    parser.add_argument("--fps", type=int, help="覆盖平台默认帧率")
    parser.add_argument("--video-bitrate", type=int, help="覆盖视频码率（kbps）")
    parser.add_argument("--crf", type=int, default=23, help="备选质量档 CRF，默认 23")
    parser.add_argument("--loudness", type=float, help="覆盖响度目标（LUFS）")
    parser.add_argument("--owner", default=os.environ.get("USER") or "未指派", help="负责人，默认当前系统用户")
    parser.add_argument("--delivery-date", help="交付日期 YYYY-MM-DD（可选）")
    parser.add_argument("--date", help="生成日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--templates", help="模板目录，默认自动定位仓库 templates/")
    parser.add_argument("--force", action="store_true", help="允许写入已有非空目录（仅覆盖同名文件）")
    parser.add_argument("--dry-run", action="store_true", help="只打印将创建的内容，不写文件")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出 manifest（配合 --dry-run 也可）")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    raw_form = args.form.strip()
    form = FORM_ALIASES.get(raw_form, raw_form)
    if form not in FORM_PROFILES:
        raise InitError("不支持的形态：%s\n可选：%s" % (args.form, " / ".join(FORM_PROFILES)))
    if args.platform not in PLATFORMS:
        raise InitError("不支持的平台：%s\n可选：%s" % (args.platform, " / ".join(PLATFORMS)))
    if args.crf < 0 or args.crf > 51:
        raise InitError("--crf 越界：%s（允许 0–51）" % args.crf)
    if args.duration is not None and (args.duration <= 0 or args.duration > 7200):
        raise InitError("--duration 越界：%s（允许 1–7200 秒）" % args.duration)

    profile = dict(PLATFORMS[args.platform])
    profile["duration"] = FORM_PROFILES[form]["duration"]
    ctx = build_context(args, form, profile)
    templates_dir = find_templates(args.templates)
    target = Path(args.root).expanduser().resolve() / ctx["dir_name"]
    if not args.dry_run:
        ensure_target(target, args.force)

    dirs = DIRS + [d + "/" + s for d in DIRS for s in SUBDIRS[d]]
    files = {
        "brief": "项目Brief.md",
        "storyboard": "分镜表.md",
        "delivery_spec": "05-交付/交付规格.md",
        "qc_checklist": "05-交付/QC清单.md",
        "manifest": "manifest.json",
    }
    payload = {
        "项目Brief.md": render_brief(read_template(templates_dir, "brief"), ctx),
        "分镜表.md": render_storyboard(read_template(templates_dir, "storyboard"), ctx),
        "05-交付/交付规格.md": render_delivery_spec(read_template(templates_dir, "delivery_spec"), ctx),
        "05-交付/QC清单.md": render_qc_checklist(read_template(templates_dir, "qc_checklist"), ctx),
    }
    manifest = make_manifest(ctx, templates_dir, files, dirs)
    payload["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    if args.dry_run:
        if args.json:
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
        print("[dry-run] 将创建项目目录：%s" % target)
        print("目录（%d 个，含子目录）：" % len(dirs))
        for d in dirs:
            print("  %s/" % d)
        print("文件：")
        for rel_path in payload:
            print("  %s" % rel_path)
        print("提示：去掉 --dry-run 才会真正写入。")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    for d in dirs:
        (target / d).mkdir(parents=True, exist_ok=True)
    # 不放占位文件；用空 .gitkeep 让空目录可被版本库保留
    for d in dirs:
        keep = target / d / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    written = []
    for rel_path, text in payload.items():
        dest = target / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append(rel_path)

    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print("项目已初始化：%s" % target)
        print("目录：%s" % "、".join(DIRS))
        print("文件：")
        for rel_path in written:
            print("  %s" % rel_path)
        if manifest["open_questions"]:
            print("待确认：%s" % "；".join(manifest["open_questions"]))
        print("下一步：填 项目Brief.md → 补 分镜表.md → 用 ffmpeg-render 导出 → qc-deliver 质检。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except InitError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        sys.exit(2)
