#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render.py — 生成并执行 FFmpeg 导出 / 转码 / 批量 / 竖屏适配 / 响度标准化命令。

交付规格来源（优先级从高到低）：
  1. 命令行覆盖参数：--width --height --fps --video-bitrate --loudness
  2. --spec：可以是 manifest.json（读 delivery_spec），也可以是 05-交付/交付规格.md
  3. --project：读取 <项目>/manifest.json，或 <项目>/05-交付/交付规格.md
  4. 内置默认值：保留源分辨率/帧率，视频 6000 kbps，响度 -14 LUFS

默认会真正执行 ffmpeg；加 --dry-run 只打印命令。先用 --dry-run 核对再执行是推荐流程。

用法示例：
  python3 skills/ffmpeg-render/scripts/render.py --project /tmp/demo --input in.mp4 \
      --output out.mp4 --dry-run
  python3 skills/ffmpeg-render/scripts/render.py --project /tmp/demo --input in.mp4 \
      --output out.mp4
  python3 skills/ffmpeg-render/scripts/render.py --input in.mp4 --mode vertical \
      --fit blur --output vertical.mp4
  python3 skills/ffmpeg-render/scripts/render.py --project /tmp/demo --input clips/ \
      --mode batch --output-dir out/
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULTS = {
    "width": None,
    "height": None,
    "fps": None,
    "video_bitrate_kbps": 6000,
    "crf": 23,
    "loudness_lufs": -14,
    "audio_bitrate_kbps": 192,
}
VIDEO_EXTS = [".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"]
PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower"]
MODE_CHOICES = ["export", "transcode", "batch", "vertical", "loudnorm"]


class RenderError(Exception):
    """可预期的输入/环境错误。"""


# ---------------------------------------------------------------- 工具函数

def require_tool(name):
    path = shutil.which(name)
    if not path:
        raise RenderError(
            "找不到 %s。请先安装 FFmpeg（macOS：brew install ffmpeg），"
            "或确认 PATH 包含其安装目录。" % name
        )
    return path


def run(cmd, timeout=None, capture=True):
    try:
        return subprocess.run(cmd, capture_output=capture, text=True, timeout=timeout)
    except FileNotFoundError:
        raise RenderError("命令不存在：%s" % cmd[0])
    except subprocess.TimeoutExpired:
        raise RenderError("命令超时（%ss）：%s" % (timeout, " ".join(cmd[:3]) + " ..."))


def probe(path, ffprobe="ffprobe"):
    if not Path(path).is_file():
        raise RenderError("输入文件不存在：%s" % path)
    cmd = [ffprobe, "-v", "error", "-print_format", "json",
           "-show_format", "-show_streams", str(path)]
    proc = run(cmd, timeout=60)
    if proc.returncode != 0:
        raise RenderError("ffprobe 读取失败：%s\n%s" % (path, (proc.stderr or "").strip()[:500]))
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RenderError("ffprobe 输出不是合法 JSON：%s" % exc)
    info = {"path": str(path), "width": None, "height": None, "fps": None,
            "has_audio": False, "duration": None, "codec": None}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and info["codec"] is None:
            info["width"] = int(stream.get("width") or 0) or None
            info["height"] = int(stream.get("height") or 0) or None
            info["fps"] = parse_rate(stream.get("r_frame_rate") or stream.get("avg_frame_rate"))
            info["codec"] = stream.get("codec_name")
        elif stream.get("codec_type") == "audio":
            info["has_audio"] = True
    fmt = data.get("format", {})
    if fmt.get("duration"):
        try:
            info["duration"] = round(float(fmt["duration"]), 3)
        except (TypeError, ValueError):
            pass
    return info


def parse_rate(raw):
    if not raw or raw in ("0/0", "N/A"):
        return None
    if "/" in raw:
        num, den = raw.split("/", 1)
        try:
            return round(float(num) / float(den), 3)
        except (ValueError, ZeroDivisionError):
            return None
    try:
        return round(float(raw), 3)
    except ValueError:
        return None


def fmt_rate(fps):
    if fps is None:
        return "N/A"
    return ("%.3f" % fps).rstrip("0").rstrip(".")


# ---------------------------------------------------------------- 交付规格

def normalize_spec(data):
    """把 manifest / md / 简化 JSON 统一成内部 spec 字典。"""
    spec = {}
    if not isinstance(data, dict):
        return spec
    if isinstance(data.get("delivery_spec"), dict):
        data = data["delivery_spec"]
    mapping = {
        "width": "width", "height": "height", "fps": "fps",
        "video_bitrate_kbps": "video_bitrate_kbps", "crf": "crf",
        "loudness_lufs": "loudness_lufs", "audio_bitrate_kbps": "audio_bitrate_kbps",
        "duration_target_s": "duration_target_s", "max_size_mb": "max_size_mb",
        "video_codec": "video_codec", "container": "container",
    }
    for src, dst in mapping.items():
        if data.get(src) not in (None, "", []):
            spec[dst] = data[src]
    return spec


def parse_spec_markdown(text):
    """从 交付规格.md 的 Markdown 表格里提取分辨率/帧率/码率/响度。"""
    spec = {}

    def cell(label):
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and cells[0] == label and len(cells) >= 2:
                return cells[1]
        return ""

    raw = cell("分辨率")
    m = re.search(r"(\d{2,5})\s*[×xX*]\s*(\d{2,5})", raw)
    if m:
        spec["width"], spec["height"] = int(m.group(1)), int(m.group(2))
    raw = cell("帧率")
    m = re.search(r"(\d{1,3}(?:\.\d+)?)", raw)
    if m:
        spec["fps"] = float(m.group(1))
    raw = cell("码率 / 质量") or cell("码率")
    m = re.search(r"(\d{3,7})\s*kbps", raw, re.I)
    if m:
        spec["video_bitrate_kbps"] = int(m.group(1))
    m = re.search(r"CRF\s*(\d{1,2})", raw, re.I)
    if m:
        spec["crf"] = int(m.group(1))
    raw = cell("音频")
    m = re.search(r"(-?\d{1,2}(?:\.\d+)?)\s*LUFS", raw, re.I)
    if m:
        spec["loudness_lufs"] = float(m.group(1))
    raw = cell("文件命名")
    if raw:
        spec["naming"] = raw
    return spec


def load_spec(args):
    spec = dict(DEFAULTS)
    candidates = []
    if args.spec:
        candidates.append(Path(args.spec).expanduser().resolve())
    if args.project:
        project = Path(args.project).expanduser().resolve()
        candidates += [project / "manifest.json", project / "05-交付" / "交付规格.md"]
    loaded_from = None
    for path in candidates:
        if not path.is_file():
            continue
        if path.suffix.lower() == ".json":
            try:
                spec.update(normalize_spec(json.loads(path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, OSError) as exc:
                raise RenderError("交付规格 JSON 读取失败：%s（%s）" % (path, exc))
        else:
            try:
                spec.update(parse_spec_markdown(path.read_text(encoding="utf-8")))
            except OSError as exc:
                raise RenderError("交付规格 Markdown 读取失败：%s（%s）" % (path, exc))
        loaded_from = str(path)
        break
    if args.spec and not loaded_from:
        raise RenderError("--spec 指向的文件不存在：%s" % args.spec)
    if args.project and not loaded_from:
        raise RenderError(
            "--project 下没找到 manifest.json 或 05-交付/交付规格.md：%s\n"
            "请先用 video-project-init 技能初始化项目。" % args.project
        )
    # 命令行覆盖
    for key in ("width", "height", "fps", "video_bitrate_kbps", "crf", "loudness_lufs", "audio_bitrate_kbps"):
        value = getattr(args, "video_bitrate_kbps" if key == "video_bitrate_kbps" else key, None)
        if key == "video_bitrate_kbps":
            value = args.video_bitrate
        if key == "loudness_lufs":
            value = args.loudness
        if key == "audio_bitrate_kbps":
            value = args.audio_bitrate
        if value is not None:
            spec[key] = value
    return spec, loaded_from


# ---------------------------------------------------------------- FFmpeg 命令

def video_encode_args(spec, codec):
    args = ["-c:v", codec]
    if codec == "libx264":
        args += ["-preset", spec["preset"], "-profile:v", "high", "-pix_fmt", "yuv420p"]
    elif codec == "libx265":
        args += ["-preset", spec["preset"], "-pix_fmt", "yuv420p", "-tag:v", "hvc1"]
    if spec.get("use_crf"):
        args += ["-crf", str(spec["crf"])]
    else:
        bitrate = int(spec["video_bitrate_kbps"])
        args += ["-b:v", "%dk" % bitrate, "-maxrate", "%dk" % int(bitrate * 1.25),
                 "-bufsize", "%dk" % int(bitrate * 2)]
    return args


def audio_encode_args(spec, has_audio):
    if not has_audio:
        return ["-an"]
    args = ["-c:a", "aac", "-b:a", "%dk" % int(spec["audio_bitrate_kbps"]),
            "-ar", "48000", "-ac", "2"]
    if not spec.get("no_audio_normalize"):
        args += ["-af", "loudnorm=I=%s:TP=-1.5:LRA=11" % fmt_rate(spec["loudness_lufs"])]
    return args


def scale_pad_filter(width, height, fps):
    chain = ("scale=%d:%d:force_original_aspect_ratio=decrease,"
             "pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
             % (width, height, width, height))
    if fps:
        chain += ",fps=%s" % fmt_rate(fps)
    return chain


def build_export_cmd(ffmpeg, input_path, output_path, spec, source, mode):
    cmd = [ffmpeg, "-hide_banner", "-y", "-i", str(input_path)]
    width = spec.get("width")
    height = spec.get("height")
    fps = spec.get("fps")
    filters = []
    if mode in ("export", "batch"):
        if width and height:
            filters.append(scale_pad_filter(int(width), int(height), fps))
    elif mode == "transcode":
        if width and height:
            filters.append(scale_pad_filter(int(width), int(height), fps))
        elif fps:
            filters.append("fps=%s" % fmt_rate(fps))
    elif mode == "vertical":
        width = width or 1080
        height = height or 1920
        fit = spec["fit"]
        if fit == "blur":
            graph = (
                "[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=20:2[bg];"
                "[0:v]scale=%d:%d:force_original_aspect_ratio=decrease[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1%s[v]"
                % (width, height, width, height, width, height,
                   ",fps=%s" % fmt_rate(fps) if fps else "")
            )
            cmd += ["-filter_complex", graph, "-map", "[v]", "-map", "0:a?"]
            filters = None
        elif fit == "crop":
            filters.append("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,setsar=1%s"
                           % (width, height, width, height,
                              ",fps=%s" % fmt_rate(fps) if fps else ""))
        elif fit == "pad":
            filters.append(scale_pad_filter(int(width), int(height), fps))
        else:
            raise RenderError("--fit 只能是 blur / crop / pad，收到：%s" % fit)
    if filters:
        cmd += ["-vf", ",".join(filters)]
    cmd += video_encode_args(spec, spec["codec"])
    cmd += audio_encode_args(spec, source["has_audio"])
    if mode != "vertical":
        cmd += ["-map", "0:v:0"]
        if source["has_audio"]:
            cmd += ["-map", "0:a:0"]
    cmd += ["-movflags", "+faststart", str(output_path)]
    return cmd


def build_loudnorm_cmd(ffmpeg, input_path, output_path, spec, source):
    if not source["has_audio"]:
        raise RenderError("输入没有音轨，无法做响度标准化：%s" % input_path)
    cmd = [ffmpeg, "-hide_banner", "-y", "-i", str(input_path),
           "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "%dk" % int(spec["audio_bitrate_kbps"]),
           "-ar", "48000", "-ac", "2",
           "-af", "loudnorm=I=%s:TP=-1.5:LRA=11" % fmt_rate(spec["loudness_lufs"]),
           "-movflags", "+faststart", str(output_path)]
    return cmd


def print_command(cmd, dry_run):
    line = " ".join(shlex.quote(part) for part in cmd)
    print(("[dry-run] " if dry_run else "[执行] ") + line)


def execute(cmd, timeout):
    proc = run(cmd, timeout=timeout)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-8:]
        raise RenderError("ffmpeg 执行失败（exit %s）：\n%s" % (proc.returncode, "\n".join(tail)))
    return proc


def print_summary(path):
    try:
        info = probe(path)
    except RenderError:
        return
    size_mb = Path(path).stat().st_size / (1024 * 1024)
    print("  → %s | %dx%d | %s fps | %ss | %.1f MB"
          % (path, info["width"] or 0, info["height"] or 0,
             fmt_rate(info["fps"]), info["duration"], size_mb))


# ---------------------------------------------------------------- 主流程

def build_parser():
    p = argparse.ArgumentParser(
        prog="render.py",
        description="生成并执行 FFmpeg 导出/转码/批量/竖屏适配/响度标准化命令。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  render.py --project ./demo --input in.mp4 --output out.mp4 --dry-run\n"
            "  render.py --input in.mp4 --mode vertical --fit blur --output v.mp4\n"
            "  render.py --project ./demo --input clips --mode batch --output-dir out\n"
        ),
    )
    p.add_argument("--input", required=True, help="输入文件；batch 模式传目录")
    p.add_argument("--output", help="输出文件；batch 模式可省略")
    p.add_argument("--output-dir", help="batch 输出目录，默认 <input>/rendered")
    p.add_argument("--mode", choices=MODE_CHOICES, default="export", help="任务模式，默认 export")
    p.add_argument("--fit", choices=["blur", "crop", "pad"], default="blur",
                   help="vertical 模式的适配方式，默认 blur（背景模糊）")
    p.add_argument("--spec", help="交付规格文件：manifest.json 或 交付规格.md")
    p.add_argument("--project", help="项目目录：自动读 manifest.json / 05-交付/交付规格.md")
    p.add_argument("--width", type=int, help="目标宽度（像素）")
    p.add_argument("--height", type=int, help="目标高度（像素）")
    p.add_argument("--fps", type=float, help="目标帧率")
    p.add_argument("--video-bitrate", type=int, help="视频码率 kbps")
    p.add_argument("--crf", type=int, help="改用 CRF 质量档（0–51），设置后不再用固定码率")
    p.add_argument("--preset", choices=PRESETS, default="medium", help="x264 速度档，默认 medium")
    p.add_argument("--codec", choices=["libx264", "libx265"], default="libx264", help="视频编码器")
    p.add_argument("--loudness", type=float, help="响度目标 LUFS，如 -14")
    p.add_argument("--audio-bitrate", type=int, help="音频码率 kbps，默认 192")
    p.add_argument("--no-audio-normalize", action="store_true", help="不做 loudnorm 响度标准化")
    p.add_argument("--pattern", default="*", help="batch 文件名通配，默认 *（按常见视频扩展名过滤）")
    p.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    p.add_argument("--timeout", type=float, default=3600, help="单条命令超时秒数，默认 3600")
    p.add_argument("--dry-run", action="store_true", help="只打印命令，不执行")
    p.add_argument("--show-spec", action="store_true", help="打印解析后的交付规格后继续")
    p.add_argument("--json", action="store_true", help="以 JSON 输出执行结果摘要")
    return p


def validate_args(args):
    if args.width is not None and not (64 <= args.width <= 7680):
        raise RenderError("--width 越界：%s（允许 64–7680）" % args.width)
    if args.height is not None and not (64 <= args.height <= 4320):
        raise RenderError("--height 越界：%s（允许 64–4320）" % args.height)
    if args.fps is not None and not (1 <= args.fps <= 240):
        raise RenderError("--fps 越界：%s（允许 1–240）" % args.fps)
    if args.video_bitrate is not None and not (100 <= args.video_bitrate <= 200000):
        raise RenderError("--video-bitrate 越界：%s kbps（允许 100–200000）" % args.video_bitrate)
    if args.crf is not None and not (0 <= args.crf <= 51):
        raise RenderError("--crf 越界：%s（允许 0–51）" % args.crf)
    if args.loudness is not None and not (-70 <= args.loudness <= 0):
        raise RenderError("--loudness 越界：%s LUFS（允许 -70–0）" % args.loudness)
    if args.audio_bitrate is not None and not (32 <= args.audio_bitrate <= 512):
        raise RenderError("--audio-bitrate 越界：%s kbps（允许 32–512）" % args.audio_bitrate)
    if args.mode == "batch":
        if not Path(args.input).is_dir():
            raise RenderError("batch 模式要求 --input 是目录，收到：%s" % args.input)
    else:
        if not Path(args.input).is_file():
            raise RenderError("输入文件不存在：%s" % args.input)
        if not args.output:
            raise RenderError("缺少 --output（非 batch 模式必填）")


def collect_batch_files(input_dir, pattern):
    files = []
    for path in sorted(Path(input_dir).iterdir()):
        if path.is_file() and path.suffix.lower() in VIDEO_EXTS:
            if Path(path).match(pattern):
                files.append(path)
    return files


def main(argv=None):
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    validate_args(args)
    ffmpeg = require_tool("ffmpeg")
    ffprobe = require_tool("ffprobe")
    spec, loaded_from = load_spec(args)
    spec["preset"] = args.preset
    spec["codec"] = args.codec
    spec["use_crf"] = args.crf is not None
    spec["no_audio_normalize"] = args.no_audio_normalize
    spec["fit"] = args.fit
    if args.mode == "transcode":
        # 转码只换编码/码率，默认保持源分辨率与帧率；显式 CLI 参数才缩放。
        spec["width"], spec["height"], spec["fps"] = args.width, args.height, args.fps
    if args.show_spec:
        print("交付规格（来源：%s）：" % (loaded_from or "默认值/命令行"))
        print(json.dumps({k: v for k, v in spec.items()
                          if k not in ("preset", "codec", "use_crf", "no_audio_normalize", "fit")},
                         ensure_ascii=False, indent=2))

    results = []
    if args.mode == "batch":
        files = collect_batch_files(args.input, args.pattern)
        if not files:
            raise RenderError("目录中没有匹配的视频文件：%s（支持 %s）"
                              % (args.input, "、".join(VIDEO_EXTS)))
        out_dir = Path(args.output_dir) if args.output_dir else Path(args.input) / "rendered"
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
        print("batch：%d 个文件 → %s" % (len(files), out_dir))
        for path in files:
            source = probe(path, ffprobe)
            out_path = out_dir / (path.stem + "-render.mp4")
            if out_path.exists() and not args.force:
                print("[跳过] 输出已存在：%s（加 --force 覆盖）" % out_path)
                continue
            cmd = build_export_cmd(ffmpeg, path, out_path, spec, source, "batch")
            print_command(cmd, args.dry_run)
            if not args.dry_run:
                execute(cmd, args.timeout)
                print_summary(out_path)
            results.append({"input": str(path), "output": str(out_path)})
    else:
        source = probe(args.input, ffprobe)
        out_path = Path(args.output)
        if out_path.exists() and not args.force:
            raise RenderError("输出文件已存在：%s\n如需覆盖请加 --force。" % out_path)
        if not args.dry_run:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.mode == "loudnorm":
            cmd = build_loudnorm_cmd(ffmpeg, args.input, out_path, spec, source)
        else:
            cmd = build_export_cmd(ffmpeg, args.input, out_path, spec, source, args.mode)
        print_command(cmd, args.dry_run)
        if not args.dry_run:
            execute(cmd, args.timeout)
            print_summary(out_path)
        results.append({"input": str(args.input), "output": str(out_path)})

    if args.json:
        print(json.dumps({"spec_source": loaded_from, "results": results},
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RenderError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        sys.exit(2)
