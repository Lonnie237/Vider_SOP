#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qc.py — 交付前自动质检：规格 / 响度 / 黑帧 / 文件大小 / 命名。

检查项：
  文件存在 | 封装 | 视频流 | 分辨率 | 帧率 | 视频编码 | 时长 | 视频码率
  音频流 | 音频编码 | 采样率 | 声道 | 音频码率
  响度（loudnorm 实测） | 真峰值 | 黑帧（blackdetect） | 文件大小 | 命名规范

输出 PASS/FAIL/WARN/SKIP 表（--json 输出机器可读报告）；有任何 FAIL 退出码为 1。
只依赖 Python 标准库，规格来自 manifest.json 或 05-交付/交付规格.md。

用法示例：
  python3 qc.py --input out.mp4 --project /tmp/demo
  python3 qc.py --input out.mp4 --spec manifest.json --json
  python3 qc.py --input out.mp4 --spec 05-交付/交付规格.md --naming-regex '^[a-z0-9-]+\.mp4$'
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

SPEC_KEYS = ("width", "height", "fps", "video_codec", "video_bitrate_kbps",
             "audio_codec", "audio_sample_rate", "audio_channels",
             "audio_bitrate_kbps", "duration_target_s", "loudness_lufs",
             "max_size_mb", "naming")
STATUS_ORDER = {"FAIL": 0, "WARN": 1, "PASS": 2, "SKIP": 3}


class QcError(Exception):
    """可预期的输入/环境错误。"""


# ---------------------------------------------------------------- 工具

def require_tool(name):
    if not shutil.which(name):
        raise QcError("找不到 %s，请先安装 FFmpeg（macOS：brew install ffmpeg）。" % name)


def display_width(text):
    width = 0
    for ch in str(text):
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def pad(text, width):
    text = str(text)
    return text + " " * max(0, width - display_width(text))


def run(cmd, timeout=300):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        raise QcError("执行命令失败：%s（%s）" % (cmd[0], exc))


def normalize_codec(value):
    text = str(value or "").strip().lower().replace(".", "").replace("/", "")
    aliases = {"h264": "h264", "avc": "h264", "hevc": "hevc", "h265": "hevc",
               "aac": "aac", "mp3": "mp3", "opus": "opus"}
    return aliases.get(text, text)


# ---------------------------------------------------------------- 规格

def parse_spec_markdown(text):
    spec = {}

    def cell(label):
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and cells[0] == label:
                return cells[1] if len(cells) > 1 else ""
        return ""

    raw = cell("分辨率")
    match = re.search(r"(\d{2,5})\s*[×xX*]\s*(\d{2,5})", raw)
    if match:
        spec["width"], spec["height"] = int(match.group(1)), int(match.group(2))
    raw = cell("帧率")
    match = re.search(r"(\d{1,3}(?:\.\d+)?)", raw)
    if match:
        spec["fps"] = float(match.group(1))
    raw = cell("视频编码").lower()
    if "264" in raw or "avc" in raw:
        spec["video_codec"] = "h264"
    elif "265" in raw or "hevc" in raw:
        spec["video_codec"] = "hevc"
    raw = cell("码率 / 质量") or cell("码率")
    match = re.search(r"(\d{3,7})\s*kbps", raw, re.I)
    if match:
        spec["video_bitrate_kbps"] = int(match.group(1))
    raw = cell("音频")
    if "aac" in raw.lower():
        spec["audio_codec"] = "aac"
    match = re.search(r"(-?\d{1,2}(?:\.\d+)?)\s*LUFS", raw, re.I)
    if match:
        spec["loudness_lufs"] = float(match.group(1))
    match = re.search(r"(\d{2,3}(?:\.\d+)?)\s*kHz", raw, re.I)
    if match:
        spec["audio_sample_rate"] = int(float(match.group(1)) * 1000)
    if "单声道" in raw:
        spec["audio_channels"] = 1
    elif "立体声" in raw:
        spec["audio_channels"] = 2
    raw = cell("文件命名")
    if raw:
        spec["naming"] = raw
    return spec


def normalize_spec(data):
    if isinstance(data, dict) and isinstance(data.get("delivery_spec"), dict):
        data = data["delivery_spec"]
    if not isinstance(data, dict):
        return {}
    return {key: data[key] for key in SPEC_KEYS if data.get(key) not in (None, "", [])}


def load_spec(args):
    spec, source = {}, None
    candidates = []
    if args.spec:
        candidates.append(Path(args.spec).expanduser().resolve())
    if args.project:
        project = Path(args.project).expanduser().resolve()
        candidates += [project / "manifest.json", project / "05-交付" / "交付规格.md"]
    for path in candidates:
        if not path.is_file():
            continue
        if path.suffix.lower() == ".json":
            try:
                spec.update(normalize_spec(json.loads(path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, OSError) as exc:
                raise QcError("规格 JSON 读取失败：%s（%s）" % (path, exc))
        else:
            try:
                spec.update(parse_spec_markdown(path.read_text(encoding="utf-8")))
            except OSError as exc:
                raise QcError("规格 Markdown 读取失败：%s（%s）" % (path, exc))
        source = str(path)
        break
    if args.spec and not source:
        raise QcError("--spec 指向的文件不存在：%s" % args.spec)
    if args.project and not source:
        raise QcError("--project 下没找到 manifest.json 或 05-交付/交付规格.md：%s" % args.project)
    # 命令行覆盖
    overrides = {
        "width": args.width, "height": args.height, "fps": args.fps,
        "video_codec": args.video_codec, "video_bitrate_kbps": args.video_bitrate,
        "audio_codec": args.audio_codec, "audio_sample_rate": args.sample_rate,
        "audio_channels": args.channels, "audio_bitrate_kbps": args.audio_bitrate,
        "duration_target_s": args.duration, "loudness_lufs": args.loudness,
        "max_size_mb": args.max_size_mb,
    }
    for key, value in overrides.items():
        if value is not None:
            spec[key] = value
    if args.naming_regex:
        spec["naming_regex"] = args.naming_regex
    return spec, source


def naming_to_regex(naming):
    if not naming:
        return None
    pattern = re.escape(str(naming))
    mapping = {
        "<version>": r"v\d+", "<版本>": r"v\d+",
        "<date>": r"\d{4}-\d{2}-\d{2}", "<日期>": r"\d{4}-\d{2}-\d{2}",
        "<project>": r"[A-Za-z0-9-]+", "<项目>": r"[A-Za-z0-9-]+",
    }
    for token, regex in mapping.items():
        pattern = pattern.replace(re.escape(token), regex)
        pattern = pattern.replace(token, regex)
    return "^" + pattern + "$"


# ---------------------------------------------------------------- 探测

def probe(path):
    proc = run(["ffprobe", "-v", "error", "-print_format", "json",
                "-show_format", "-show_streams", str(path)])
    if proc.returncode != 0:
        raise QcError("ffprobe 读取失败：%s\n%s" % (path, (proc.stderr or "").strip()[:500]))
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise QcError("ffprobe 输出不是合法 JSON：%s" % exc)


def stream_value(stream, key):
    value = stream.get(key)
    try:
        return float(value) if value not in (None, "N/A") else None
    except (TypeError, ValueError):
        return None


def measure_loudness(path, target):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
           "-af", "loudnorm=I=%s:TP=-1.5:LRA=11:print_format=json" % target,
           "-f", "null", "-"]
    proc = run(cmd)
    text = (proc.stderr or "") + (proc.stdout or "")
    blocks = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", text, re.S)
    if not blocks:
        raise QcError("loudnorm 没有返回 JSON（文件可能没有音轨）：%s" % path)
    try:
        data = json.loads(blocks[-1])
    except json.JSONDecodeError as exc:
        raise QcError("loudnorm 输出解析失败：%s" % exc)
    return {
        "input_i": float(data["input_i"]),
        "input_tp": float(data["input_tp"]),
        "input_lra": float(data.get("input_lra", 0)),
    }


def detect_black(path, duration_threshold):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
           "-vf", "blackdetect=d=%s:pix_th=0.10" % duration_threshold,
           "-an", "-f", "null", "-"]
    proc = run(cmd)
    text = (proc.stderr or "") + (proc.stdout or "")
    intervals = []
    for match in re.finditer(
            r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)", text):
        intervals.append((float(match.group(1)), float(match.group(2)),
                          float(match.group(3))))
    return intervals


# ---------------------------------------------------------------- 检查

def add(checks, name, expected, actual, status, note=""):
    checks.append({"name": name, "expected": str(expected), "actual": str(actual),
                   "status": status, "note": note})


def fmt_num(value, digits=2):
    if value is None:
        return "N/A"
    return ("%%.%df" % digits % value).rstrip("0").rstrip(".")


def run_checks(path, spec, args):
    checks = []
    add(checks, "文件存在", "可读文件", path.name, "PASS")
    size_mb = path.stat().st_size / (1024 * 1024)
    data = probe(path)
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    container = str(fmt.get("format_name", ""))

    add(checks, "封装", spec.get("container", "mp4"), container,
        "PASS" if "mp4" in container or spec.get("container") is None else "FAIL")
    add(checks, "视频流", "存在", "存在" if video else "缺失",
        "PASS" if video else "FAIL")
    if not video:
        return checks, size_mb

    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    add(checks, "分辨率", "%dx%d" % (spec["width"], spec["height"]) if spec.get("width") else "未指定",
        "%dx%d" % (width, height),
        "PASS" if not spec.get("width") else
        ("PASS" if (width, height) == (int(spec["width"]), int(spec["height"])) else "FAIL"))

    fps = stream_value(video, "r_frame_rate")
    if fps is None and video.get("r_frame_rate"):
        try:
            num, den = str(video["r_frame_rate"]).split("/")
            fps = float(num) / float(den) if float(den) else None
        except (ValueError, ZeroDivisionError):
            fps = None
    if spec.get("fps"):
        ok = fps is not None and abs(fps - float(spec["fps"])) <= args.fps_tolerance
        add(checks, "帧率", "%sfps" % fmt_num(spec["fps"]), "%sfps" % fmt_num(fps),
            "PASS" if ok else "FAIL",
            "" if ok else "容差 ±%s" % args.fps_tolerance)
    else:
        add(checks, "帧率", "未指定", "%sfps" % fmt_num(fps), "SKIP")

    codec = normalize_codec(video.get("codec_name"))
    add(checks, "视频编码", spec.get("video_codec", "未指定"), codec,
        "PASS" if not spec.get("video_codec") else
        ("PASS" if codec == normalize_codec(spec["video_codec"]) else "FAIL"))

    duration = None
    try:
        duration = float(fmt.get("duration"))
    except (TypeError, ValueError):
        pass
    if spec.get("duration_target_s") and duration is not None:
        target = float(spec["duration_target_s"])
        ok = abs(duration - target) <= args.duration_tolerance
        add(checks, "时长", "%ss" % fmt_num(target), "%ss" % fmt_num(duration),
            "PASS" if ok else "FAIL", "" if ok else "容差 ±%ss" % args.duration_tolerance)
    else:
        add(checks, "时长", "未指定", "%ss" % fmt_num(duration), "SKIP")

    video_kbps = None
    if video.get("bit_rate"):
        video_kbps = float(video["bit_rate"]) / 1000
    if spec.get("video_bitrate_kbps") and video_kbps is not None:
        target = float(spec["video_bitrate_kbps"])
        ratio = abs(video_kbps - target) / target
        add(checks, "视频码率", "%skbps" % fmt_num(target), "%skbps" % fmt_num(video_kbps, 0),
            "PASS" if ratio <= args.bitrate_tolerance else "FAIL",
            "" if ratio <= args.bitrate_tolerance else "偏差 %.0f%%，容差 %.0f%%" % (
                ratio * 100, args.bitrate_tolerance * 100))
    else:
        add(checks, "视频码率", "未指定" if not spec.get("video_bitrate_kbps") else "%skbps" % spec["video_bitrate_kbps"],
            "%skbps" % fmt_num(video_kbps, 0) if video_kbps else "N/A", "SKIP")

    add(checks, "音频流", "存在", "存在" if audio else "缺失",
        "PASS" if audio else "FAIL")
    if audio:
        audio_codec = normalize_codec(audio.get("codec_name"))
        add(checks, "音频编码", spec.get("audio_codec", "未指定"), audio_codec,
            "PASS" if not spec.get("audio_codec") else
            ("PASS" if audio_codec == normalize_codec(spec["audio_codec"]) else "FAIL"))
        sample_rate = audio.get("sample_rate")
        add(checks, "采样率", "%sHz" % (spec.get("audio_sample_rate") or "未指定"),
            "%sHz" % (sample_rate or "N/A"),
            "PASS" if not spec.get("audio_sample_rate") else
            ("PASS" if str(sample_rate) == str(spec["audio_sample_rate"]) else "FAIL"))
        channels = audio.get("channels")
        add(checks, "声道数", str(spec.get("audio_channels") or "未指定"),
            str(channels or "N/A"),
            "PASS" if not spec.get("audio_channels") else
            ("PASS" if str(channels) == str(spec["audio_channels"]) else "FAIL"))
        audio_kbps = None
        if audio.get("bit_rate"):
            audio_kbps = float(audio["bit_rate"]) / 1000
        if spec.get("audio_bitrate_kbps") and audio_kbps is not None:
            target = float(spec["audio_bitrate_kbps"])
            ratio = abs(audio_kbps - target) / target
            add(checks, "音频码率", "%skbps" % fmt_num(target, 0),
                "%skbps" % fmt_num(audio_kbps, 0),
                "PASS" if ratio <= args.bitrate_tolerance else "FAIL")
        else:
            add(checks, "音频码率", "未指定" if not spec.get("audio_bitrate_kbps") else "%skbps" % spec["audio_bitrate_kbps"],
                "%skbps" % fmt_num(audio_kbps, 0) if audio_kbps else "N/A", "SKIP")
    else:
        for name in ("音频编码", "采样率", "声道数", "音频码率"):
            add(checks, name, "有音轨", "无音轨", "FAIL" if spec.get("audio_codec") else "SKIP")

    if not args.skip_loudness and audio:
        target = float(spec.get("loudness_lufs") or -14)
        try:
            measured = measure_loudness(path, target)
            delta = measured["input_i"] - target
            ok = abs(delta) <= args.loudness_tolerance
            add(checks, "响度 I", "%s LUFS" % fmt_num(target, 1),
                "%s LUFS" % fmt_num(measured["input_i"], 1),
                "PASS" if ok else "FAIL",
                "" if ok else "偏差 %+.1f LU" % delta)
            tp_ok = measured["input_tp"] <= -1.0
            add(checks, "真峰值 TP", "<= -1.0 dBTP",
                "%s dBTP" % fmt_num(measured["input_tp"], 1),
                "PASS" if tp_ok else "FAIL")
            add(checks, "响度范围 LRA", "参考", "%s LU" % fmt_num(measured["input_lra"], 1), "PASS")
        except QcError as exc:
            add(checks, "响度 I", "可测", "测量失败", "FAIL", str(exc)[:80])
    else:
        add(checks, "响度 I", "参考", "未测量", "SKIP")

    if not args.skip_blackdetect:
        intervals = detect_black(path, args.black_duration)
        significant = []
        for start, end, duration in intervals:
            if args.allow_black_edges > 0 and (
                    (start < args.allow_black_edges) or
                    (duration and end >= (duration - args.allow_black_edges))):
                continue
            significant.append((start, end, duration))
        if significant:
            sample = "；".join("%.2fs-%.2fs" % (s, e) for s, e, _ in significant[:3])
            add(checks, "黑帧", "0 段（>=%.1fs）" % args.black_duration,
                "%d 段：%s" % (len(significant), sample), "FAIL",
                "黑帧可能由片头片尾造成，确认后可放宽 --allow-black-edges")
        else:
            add(checks, "黑帧", "0 段（>=%.1fs）" % args.black_duration,
                "%d 段" % len(intervals), "PASS")
    else:
        add(checks, "黑帧", "参考", "未检测", "SKIP")

    if spec.get("max_size_mb") is not None:
        limit = float(spec["max_size_mb"])
        add(checks, "文件大小", "<= %s MB" % fmt_num(limit, 1),
            "%.2f MB" % size_mb, "PASS" if size_mb <= limit else "FAIL")
    else:
        add(checks, "文件大小", "未指定上限", "%.2f MB" % size_mb, "SKIP")

    pattern = spec.get("naming_regex") or naming_to_regex(spec.get("naming"))
    if pattern:
        matched = re.fullmatch(pattern, path.name) is not None
        add(checks, "命名规范", pattern, path.name, "PASS" if matched else "FAIL",
            "" if matched else "用 --naming-regex 或修改文件名")
    else:
        add(checks, "命名规范", "未指定", path.name, "SKIP")
    return checks, size_mb


# ---------------------------------------------------------------- 输出

def print_table(path, checks, size_mb):
    headers = ["检查项", "期望", "实测", "结果", "备注"]
    rows = [[check["name"], check["expected"], check["actual"],
             check["status"], check["note"]] for check in checks]
    widths = [max(display_width(row[i]) for row in ([headers] + rows)) + 2
              for i in range(len(headers))]
    widths[-1] = min(widths[-1], 40)
    print("交付质检：%s（%.2f MB）" % (path, size_mb))
    print("".join(pad(headers[i], widths[i]) for i in range(len(headers))).rstrip())
    print("-" * (sum(widths) + 8))
    for row in rows:
        print("".join(pad(row[i], widths[i]) for i in range(len(headers))).rstrip())
    counts = {status: 0 for status in ("PASS", "FAIL", "WARN", "SKIP")}
    for check in checks:
        counts[check["status"]] += 1
    overall = "FAIL" if counts["FAIL"] else "PASS"
    print("")
    print("结果：%s（%d PASS / %d FAIL / %d WARN / %d SKIP）" % (
        overall, counts["PASS"], counts["FAIL"], counts["WARN"], counts["SKIP"]))
    return overall


def build_parser():
    parser = argparse.ArgumentParser(
        prog="qc.py",
        description="交付质检：ffprobe 规格核验 + 响度 + 黑帧 + 文件大小 + 命名规范。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  qc.py --input out.mp4 --project /tmp/demo\n"
            "  qc.py --input out.mp4 --spec 05-交付/交付规格.md --json\n"
            "  qc.py --input out.mp4 --spec spec.json --naming-regex '^[a-z0-9-]+\\.mp4$'\n"
        ),
    )
    parser.add_argument("--input", "-i", required=True, help="待检视频")
    parser.add_argument("--spec", help="交付规格：manifest.json 或 交付规格.md")
    parser.add_argument("--project", help="项目目录：自动读 manifest.json / 05-交付/交付规格.md")
    parser.add_argument("--width", type=int, help="期望宽度")
    parser.add_argument("--height", type=int, help="期望高度")
    parser.add_argument("--fps", type=float, help="期望帧率")
    parser.add_argument("--video-codec", help="期望视频编码，如 h264")
    parser.add_argument("--video-bitrate", type=int, help="期望视频码率 kbps")
    parser.add_argument("--audio-codec", help="期望音频编码，如 aac")
    parser.add_argument("--sample-rate", type=int, help="期望采样率 Hz")
    parser.add_argument("--channels", type=int, help="期望声道数")
    parser.add_argument("--audio-bitrate", type=int, help="期望音频码率 kbps")
    parser.add_argument("--duration", type=float, help="期望时长（秒）")
    parser.add_argument("--loudness", type=float, help="期望响度 LUFS")
    parser.add_argument("--max-size-mb", type=float, help="文件大小上限 MB")
    parser.add_argument("--naming-regex", help="文件名正则（默认由规格 naming 推导）")
    parser.add_argument("--fps-tolerance", type=float, default=0.1, help="帧率容差，默认 0.1")
    parser.add_argument("--duration-tolerance", type=float, default=0.5, help="时长容差秒，默认 0.5")
    parser.add_argument("--bitrate-tolerance", type=float, default=0.35, help="码率相对容差，默认 0.35")
    parser.add_argument("--loudness-tolerance", type=float, default=1.0, help="响度容差 LU，默认 1.0")
    parser.add_argument("--black-duration", type=float, default=0.5, help="黑帧判定时长秒，默认 0.5")
    parser.add_argument("--allow-black-edges", type=float, default=0.0,
                        help="允许片头/片尾黑帧的秒数，默认 0")
    parser.add_argument("--skip-loudness", action="store_true", help="跳过响度分析")
    parser.add_argument("--skip-blackdetect", action="store_true", help="跳过黑帧检测")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    return parser


def main(argv=None):
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    if not (0.5 <= args.duration_tolerance <= 10):
        raise QcError("--duration-tolerance 越界：%s（允许 0.5–10）" % args.duration_tolerance)
    if not (0 <= args.bitrate_tolerance <= 1):
        raise QcError("--bitrate-tolerance 越界：%s（允许 0–1）" % args.bitrate_tolerance)
    if args.black_duration <= 0:
        raise QcError("--black-duration 必须 > 0")
    require_tool("ffprobe")
    require_tool("ffmpeg")
    path = Path(args.input).expanduser().resolve()
    if not path.is_file():
        raise QcError("输入文件不存在：%s" % args.input)
    spec, source = load_spec(args)
    if not spec:
        raise QcError(
            "没有交付规格：请用 --spec / --project 提供，或用 --width/--fps/--duration 等参数指定。\n"
            "项目没初始化时先跑 video-project-init 技能。")
    checks, size_mb = run_checks(path, spec, args)
    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    if args.json:
        report = {
            "input": str(path),
            "spec_source": source,
            "status": overall,
            "size_mb": round(size_mb, 2),
            "summary": {status: sum(1 for c in checks if c["status"] == status)
                        for status in ("PASS", "FAIL", "WARN", "SKIP")},
            "checks": checks,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_table(path, checks, size_mb)
    return 1 if overall == "FAIL" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except QcError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        sys.exit(2)
