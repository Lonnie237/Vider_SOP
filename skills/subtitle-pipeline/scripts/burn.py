#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""burn.py — 字幕烧录 / 软封装 / 外挂，优先 libass，缺失时走 Pillow + overlay。

本机 ffmpeg 9.0.2 未编译 libass/freetype，subtitles/ass/drawtext 滤镜不可用。
脚本启动先做能力探测：
  - 有 subtitles 滤镜：走 ffmpeg -vf subtitles=...（libass 分支）
  - 没有：用 Pillow 把每条字幕渲染成全画幅透明 PNG，再用 overlay 的
    enable='between(t,start,end)' 按时间区间叠加（fallback 分支）

模式：
  burn      烧录（默认）
  mux       封装软字幕（mov_text，不依赖 libass）
  external  视频流复制 + 同目录输出 .srt 外挂文件

用法示例：
  python3 burn.py --input in.mp4 --srt subs.srt --output out.mp4
  python3 burn.py --input in.mp4 --srt subs.srt --output out.mp4 --engine pillow
  python3 burn.py --input in.mp4 --srt subs.srt --output out.mp4 --mode mux
  python3 burn.py --input in.mp4 --srt subs.srt --output out.mp4 --mode external
  python3 burn.py --input in.mp4 --srt subs.srt --output out.mp4 --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from subtitle import SubError, parse_srt  # noqa: E402
except ImportError as exc:  # pragma: no cover
    raise SystemExit("错误：找不到同目录的 subtitle.py（%s）" % exc)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # 延迟到真正需要 Pillow 时报错，允许 --mode mux/external 在无 Pillow 时工作
    Image = ImageDraw = ImageFont = None

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower"]


class BurnError(Exception):
    """可预期的输入/环境错误。"""


# ---------------------------------------------------------------- 探测

def require_tool(name):
    if not shutil.which(name):
        raise BurnError("找不到 %s，请先安装 FFmpeg（macOS：brew install ffmpeg）。" % name)


def detect_filter(name):
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-h", "filter=%s" % name],
                          capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return "Unknown filter" not in output and proc.returncode == 0


def ffprobe_json(path):
    proc = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                           "-show_format", "-show_streams", str(path)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise BurnError("ffprobe 读取失败：%s\n%s" % (path, (proc.stderr or "").strip()[:400]))
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise BurnError("ffprobe 输出不是合法 JSON：%s" % exc)


def probe_video(path):
    if not Path(path).is_file():
        raise BurnError("输入视频不存在：%s" % path)
    data = ffprobe_json(path)
    info = {"width": None, "height": None, "fps": None, "duration": None, "has_audio": False}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and info["width"] is None:
            info["width"] = int(stream.get("width") or 0) or None
            info["height"] = int(stream.get("height") or 0) or None
            rate = stream.get("r_frame_rate") or stream.get("avg_frame_rate") or "0/1"
            try:
                num, den = rate.split("/")
                info["fps"] = round(float(num) / float(den), 3) if float(den) else None
            except (ValueError, ZeroDivisionError):
                info["fps"] = None
        elif stream.get("codec_type") == "audio":
            info["has_audio"] = True
    try:
        info["duration"] = round(float(data.get("format", {}).get("duration")), 3)
    except (TypeError, ValueError):
        info["duration"] = None
    if not info["width"] or not info["height"]:
        raise BurnError("没有找到视频流：%s" % path)
    return info


# ---------------------------------------------------------------- 字体与 PNG

def find_font(explicit):
    if explicit:
        if not Path(explicit).is_file():
            raise BurnError("--font 指向的字体不存在：%s" % explicit)
        return explicit
    for candidate in FONT_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise BurnError("找不到可用的中文字体：请用 --font 指定 .ttf/.ttc 路径。")


def text_length(font, text):
    if hasattr(font, "getlength"):
        return font.getlength(text)
    return font.getsize(text)[0]


def wrap_by_pixels(text, font, max_px):
    tokens = re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?|\s+|.", text)
    lines, current = [], ""
    for token in tokens:
        candidate = current + token
        if text_length(font, candidate) <= max_px or not current.strip():
            if not current and token.isspace():
                continue
            if text_length(font, candidate) > max_px:
                # 单个超长 token：按字符再切
                for ch in token:
                    if text_length(font, current + ch) > max_px and current:
                        lines.append(current.rstrip())
                        current = ch
                    else:
                        current += ch
                continue
            current = candidate
        else:
            lines.append(current.rstrip())
            current = "" if token.isspace() else token
    if current.strip():
        lines.append(current.rstrip())
    return [line for line in lines if line.strip()]


def render_cue_png(cue, out_path, size, font, font_size, opts):
    width, height = size
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    max_px = int(width * opts.max_width_ratio)
    lines = []
    for logical in cue["text"].split("\n"):
        logical = logical.strip()
        if logical:
            lines.extend(wrap_by_pixels(logical, font, max_px))
    if not lines:
        lines = [""]
    stroke = opts.stroke_width if opts.stroke_width is not None else max(2, font_size // 16)
    line_height = int(font_size * 1.35)
    block_height = line_height * len(lines)
    margin = opts.margin_v if opts.margin_v is not None else max(24, int(height * 0.08))
    if opts.position == "top":
        top = margin
    elif opts.position == "center":
        top = max(0, (height - block_height) // 2)
    else:
        top = max(0, height - margin - block_height)

    if opts.bg == "box":
        pad_x, pad_y = int(font_size * 0.5), int(font_size * 0.25)
        widest = max(text_length(font, line) for line in lines) + stroke * 2
        box = [width / 2 - widest / 2 - pad_x, top - pad_y,
               width / 2 + widest / 2 + pad_x, top + block_height + pad_y]
        draw.rounded_rectangle(box, radius=max(6, font_size // 4),
                               fill=(0, 0, 0, int(255 * opts.bg_opacity)))

    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) / 2 - bbox[0]
        y = top + index * line_height - bbox[1]
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255),
                  stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    image.save(out_path)
    return out_path


def load_font(font_path, font_size):
    try:
        return ImageFont.truetype(font_path, font_size)
    except OSError as exc:
        raise BurnError("加载字体失败：%s（%s）" % (font_path, exc))


# ---------------------------------------------------------------- 命令构建

def fmt_time(value):
    return ("%.3f" % value).rstrip("0").rstrip(".")


def build_pillow_command(input_path, output_path, png_paths, cues, info, opts):
    fps = info["fps"] or 30
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(input_path)]
    for png in png_paths:
        cmd += ["-loop", "1", "-framerate", ("%.3f" % fps).rstrip("0").rstrip("."),
                "-i", str(png)]
    chain = []
    previous = "[0:v]"
    for index, cue in enumerate(cues):
        label = "[vout]" if index == len(cues) - 1 else "[v%d]" % (index + 1)
        chain.append("%s[%d:v]overlay=x=0:y=0:enable='between(t,%s,%s)'%s" % (
            previous, index + 1, fmt_time(cue["start"]), fmt_time(cue["end"]), label))
        previous = label
    cmd += ["-filter_complex", ";".join(chain),
            "-map", "[vout]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", opts.preset, "-crf", str(opts.crf),
            "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart"]
    if info["duration"]:
        cmd += ["-t", fmt_time(info["duration"])]
    cmd.append(str(output_path))
    return cmd


def ass_escape(value):
    text = str(value)
    for old, new in (("\\", "\\\\"), (":", "\\:"), ("'", "\\'"), ("[", "\\["),
                     ("]", "\\]"), (",", "\\,")):
        text = text.replace(old, new)
    return text


def build_libass_command(input_path, output_path, srt_path, info, opts):
    font_size = opts.font_size or max(20, int(info["height"] * 0.045))
    margin_v = opts.margin_v if opts.margin_v is not None else max(24, int(info["height"] * 0.10))
    style = ("FontName=%s,FontSize=%d,PrimaryColour=&H00FFFFFF,"
             "OutlineColour=&H00000000,BorderStyle=1,Outline=%d,Shadow=0,MarginV=%d" % (
                 ass_escape(opts.font_name or "Hiragino Sans GB"), font_size,
                 opts.stroke_width if opts.stroke_width is not None else 3, margin_v))
    vf = "subtitles=filename='%s':force_style='%s'" % (
        ass_escape(Path(srt_path).resolve()), style)
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(input_path), "-vf", vf,
           "-c:v", "libx264", "-preset", opts.preset, "-crf", str(opts.crf),
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
           str(output_path)]
    return cmd


def build_mux_command(input_path, output_path, srt_path):
    return ["ffmpeg", "-hide_banner", "-y", "-i", str(input_path), "-i", str(srt_path),
            "-map", "0:v:0", "-map", "0:a?", "-map", "1:0", "-c", "copy",
            "-c:s", "mov_text", "-metadata:s:s:0", "language=chi",
            "-movflags", "+faststart", str(output_path)]


def build_external_commands(input_path, output_path, srt_path):
    remux = ["ffmpeg", "-hide_banner", "-y", "-i", str(input_path), "-map", "0",
             "-c", "copy", "-movflags", "+faststart", str(output_path)]
    return remux, str(Path(output_path).with_suffix(".srt"))


def print_command(cmd, dry_run):
    prefix = "[dry-run] " if dry_run else "[执行] "
    print(prefix + " ".join(shlex.quote(part) for part in cmd))


def execute(cmd, timeout):
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-10:]
        raise BurnError("ffmpeg 执行失败（exit %s）：\n%s" % (proc.returncode, "\n".join(tail)))
    return proc


# ---------------------------------------------------------------- 主流程

def build_parser():
    parser = argparse.ArgumentParser(
        prog="burn.py",
        description="字幕烧录/软封装/外挂：优先 libass，缺失时用 Pillow + overlay fallback。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  burn.py --input in.mp4 --srt subs.srt --output out.mp4\n"
            "  burn.py --input in.mp4 --srt subs.srt --output out.mp4 --engine pillow\n"
            "  burn.py --input in.mp4 --srt subs.srt --output out.mp4 --mode mux\n"
        ),
    )
    parser.add_argument("--input", "-i", required=True, help="输入视频")
    parser.add_argument("--srt", required=True, help="字幕文件（SRT）")
    parser.add_argument("--output", "-o", required=True, help="输出视频")
    parser.add_argument("--mode", choices=["burn", "mux", "external"], default="burn",
                        help="burn 烧录 / mux 软字幕 / external 外挂，默认 burn")
    parser.add_argument("--engine", choices=["auto", "libass", "pillow"], default="auto",
                        help="烧录引擎：auto 自动选择，默认 auto")
    parser.add_argument("--position", choices=["bottom", "center", "top"], default="bottom",
                        help="字幕位置，默认 bottom")
    parser.add_argument("--font", help="字体文件路径；默认自动探测中文字体")
    parser.add_argument("--font-name", help="libass 分支使用的字体名，默认 Hiragino Sans GB")
    parser.add_argument("--font-size", type=int, help="字号（像素）；默认 画面高 x 0.045")
    parser.add_argument("--max-width-ratio", type=float, default=0.86, help="单行最大宽度占比")
    parser.add_argument("--margin-v", type=int, help="上下安全边距（像素）")
    parser.add_argument("--stroke-width", type=int, help="描边宽度（像素）")
    parser.add_argument("--bg", choices=["none", "box"], default="none", help="是否加半透明底框")
    parser.add_argument("--bg-opacity", type=float, default=0.55, help="底框不透明度 0–1")
    parser.add_argument("--crf", type=int, default=20, help="重编码 CRF，默认 20")
    parser.add_argument("--preset", choices=PRESETS, default="medium", help="x264 速度档")
    parser.add_argument("--keep-png", help="保留渲染的 PNG 到指定目录（便于检查）")
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    parser.add_argument("--timeout", type=float, default=1800, help="单条命令超时秒数")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划与命令，不执行")
    parser.add_argument("--json", action="store_true", help="JSON 输出执行摘要")
    return parser


def validate_args(args):
    if not (0.1 <= args.max_width_ratio <= 1.0):
        raise BurnError("--max-width-ratio 越界：%s（允许 0.1–1.0）" % args.max_width_ratio)
    if not (0 <= args.bg_opacity <= 1):
        raise BurnError("--bg-opacity 越界：%s（允许 0–1）" % args.bg_opacity)
    if not (0 <= args.crf <= 51):
        raise BurnError("--crf 越界：%s（允许 0–51）" % args.crf)
    if args.font_size is not None and not (8 <= args.font_size <= 400):
        raise BurnError("--font-size 越界：%s（允许 8–400）" % args.font_size)
    if not Path(args.input).is_file():
        raise BurnError("输入视频不存在：%s" % args.input)
    if not Path(args.srt).is_file():
        raise BurnError("字幕文件不存在：%s" % args.srt)
    output = Path(args.output)
    if output.exists() and not args.force:
        raise BurnError("输出文件已存在：%s（加 --force 覆盖，或换输出名）" % args.output)
    if output.resolve() == Path(args.input).resolve():
        raise BurnError("--output 不能与 --input 相同。")
    if not output.parent.exists():
        output.parent.mkdir(parents=True, exist_ok=True)


def main(argv=None):
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    validate_args(args)
    require_tool("ffmpeg")
    require_tool("ffprobe")
    try:
        cues = parse_srt(Path(args.srt).read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        raise BurnError("字幕不是 UTF-8：%s" % args.srt)
    except SubError as exc:
        raise BurnError("字幕解析失败：%s" % exc)
    info = probe_video(args.input)
    has_libass = detect_filter("subtitles") and detect_filter("ass")
    if args.engine == "auto":
        engine = "libass" if has_libass else "pillow"
    elif args.engine == "libass":
        if not has_libass:
            raise BurnError(
                "本机 FFmpeg 没有 subtitles/ass 滤镜（未编译 libass），"
                "不能用 --engine libass；去掉该参数走 Pillow fallback，或换带 libass 的 FFmpeg。")
        engine = "libass"
    else:
        engine = "pillow"
    if args.mode != "burn":
        engine = "none"

    summary = {"input": args.input, "srt": args.srt, "output": args.output,
               "mode": args.mode, "engine": engine, "cues": len(cues),
               "video": {"width": info["width"], "height": info["height"],
                         "fps": info["fps"], "duration": info["duration"]},
               "libass_available": has_libass}
    if not args.json:
        print("能力探测：ffmpeg %s | subtitles/ass 滤镜 %s → %s" % (
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            .stdout.splitlines()[0].split()[2],
            "可用" if has_libass else "不可用",
            "libass 分支" if engine == "libass" else
            ("Pillow PNG + overlay fallback" if engine == "pillow" else args.mode)))
        print("字幕 %d 条，视频 %dx%d @ %s fps，时长 %ss" % (
            len(cues), info["width"], info["height"], info["fps"], info["duration"]))

    if args.mode == "external":
        remux, srt_target = build_external_commands(args.input, args.output, args.srt)
        print_command(remux, args.dry_run)
        print("将输出外挂字幕：%s" % srt_target)
        if not args.dry_run:
            execute(remux, args.timeout)
            shutil.copyfile(args.srt, srt_target)
        summary["srt_output"] = srt_target
    elif args.mode == "mux":
        cmd = build_mux_command(args.input, args.output, args.srt)
        print_command(cmd, args.dry_run)
        if not args.dry_run:
            execute(cmd, args.timeout)
    else:
        if engine == "libass":
            cmd = build_libass_command(args.input, args.output, args.srt, info, args)
            print_command(cmd, args.dry_run)
            if not args.dry_run:
                execute(cmd, args.timeout)
        else:
            if Image is None:
                raise BurnError(
                    "本机没有 Pillow，且 FFmpeg 没有 libass，无法烧录。"
                    "安装 Pillow：python3 -m pip install --user pillow（建议独立 venv）。")
            font_path = find_font(args.font)
            font_size = args.font_size or max(20, int(info["height"] * 0.045))
            font = load_font(font_path, font_size)
            if args.keep_png:
                png_dir = Path(args.keep_png).expanduser().resolve()
            else:
                png_dir = Path(tempfile.mkdtemp(prefix="subtitle-png-"))
            png_dir.mkdir(parents=True, exist_ok=True)
            png_paths = []
            for index, cue in enumerate(cues, 1):
                png_path = png_dir / ("cue_%04d.png" % index)
                if not args.dry_run:
                    render_cue_png(cue, png_path, (info["width"], info["height"]),
                                   font, font_size, args)
                png_paths.append(png_path)
            cmd = build_pillow_command(args.input, args.output, png_paths, cues, info, args)
            if args.dry_run:
                printable = [str(png_dir / ("cue_%04d.png" % i)) for i in range(1, len(cues) + 1)]
                print("[dry-run] 将用 Pillow 渲染 %d 张透明 PNG：%s" % (len(printable), png_dir))
                cmd_for_print = build_pillow_command(
                    args.input, args.output,
                    [Path("<png_dir>/cue_%04d.png" % i) for i in range(1, len(cues) + 1)],
                    cues, info, args)
                print_command(cmd_for_print, True)
            else:
                print_command(cmd, False)
                execute(cmd, args.timeout)
                summary["png_dir"] = str(png_dir)
    if not args.dry_run:
        size = Path(args.output).stat().st_size / (1024 * 1024)
        print("  → %s | %.1f MB" % (args.output, size))
        summary["size_mb"] = round(size, 2)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BurnError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        print("错误：ffmpeg 执行超时。", file=sys.stderr)
        sys.exit(2)
