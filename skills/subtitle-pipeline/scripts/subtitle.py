#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""subtitle.py — 字幕文本处理：断句、校时、CPS 校验、SRT/ASS 生成与能力探测。

输入：
  - 纯文本（每行一句，可选行首时间区间，如 [00:00:01.000-00:00:02.500] 台词）
  - 已存在的 SRT（自动识别 -->）
输出：
  - SRT（utf-8）或 ASS（UTF-8，供有 libass 的 FFmpeg / 播放器使用）
  - 终端摘要：条数、总时长、最大 CPS、告警

本脚本只做文本与时间，不调用 FFmpeg 滤镜；烧录请用 burn.py。
本机 ffmpeg 9.0.2 未编译 libass，subtitle 相关滤镜不可用，burn.py 会自动走 Pillow overlay。

用法示例：
  python3 subtitle.py probe
  python3 subtitle.py build --input script.txt --duration 30 --out subs.srt
  python3 subtitle.py build --input script.txt --duration 30 --out subs.ass
  python3 subtitle.py validate --input subs.srt
  python3 subtitle.py retime --input subs.srt --out fixed.srt --offset 0.4
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

SRT_TIME_RE = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})")
SRT_ARROW_RE = re.compile(
    r"(\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{3})"
)
INLINE_TIME_RE = re.compile(
    r"^\s*[\[【]?\s*(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})"
    r"\s*(?:-{1,2}|–|—|~|至)\s*"
    r"(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s*[\]】]?\s*(.*)$"
)
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])")
PUNCT_BREAK = set("，、；：,.;:!?！？。 ")


class SubError(Exception):
    """可预期的输入/格式错误。"""


# ---------------------------------------------------------------- 时间与宽度

def parse_time(raw):
    """解析 00:00:01,000 / 00:01.000 / 01:02.500 为秒。"""
    text = str(raw).strip().replace(",", ".")
    parts = text.split(":")
    try:
        if len(parts) == 2:
            hours, minutes, seconds = 0, int(parts[0]), float(parts[1])
        elif len(parts) == 3:
            hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
        else:
            raise ValueError
    except ValueError:
        raise SubError("时间格式无法解析：%s（示例 00:00:01,000）" % raw)
    return round(hours * 3600 + minutes * 60 + seconds, 3)


def seconds_to_srt(seconds):
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    hours, rem = divmod(ms, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, millis = divmod(rem, 1000)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, secs, millis)


def seconds_to_ass(seconds):
    if seconds < 0:
        seconds = 0.0
    cs = int(round(seconds * 100))
    hours, rem = divmod(cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, centis = divmod(rem, 100)
    return "%d:%02d:%02d.%02d" % (hours, minutes, secs, centis)


def display_width(text):
    width = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            width += 2
        else:
            width += 1
    return width


# ---------------------------------------------------------------- SRT 读写

def parse_srt(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues = []
    for block in blocks:
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0].strip()):
            lines = lines[1:]
        if not lines:
            continue
        match = SRT_ARROW_RE.search(lines[0])
        if not match:
            raise SubError("SRT 时间行无法解析：%s" % lines[0].strip()[:60])
        start = parse_time(match.group(1))
        end = parse_time(match.group(2))
        if end <= start:
            raise SubError("SRT 第 %d 条 end <= start" % (len(cues) + 1))
        body = "\n".join(lines[1:]).strip()
        cues.append({"index": len(cues) + 1, "start": start, "end": end, "text": body})
    if not cues:
        raise SubError("没有解析到任何字幕条，请检查 SRT 格式。")
    return cues


def cues_to_srt(cues):
    chunks = []
    for i, cue in enumerate(cues, 1):
        chunks.append("%d\n%s --> %s\n%s\n" % (
            i, seconds_to_srt(cue["start"]), seconds_to_srt(cue["end"]), cue["text"]))
    return "\n".join(chunks)


def cues_to_ass(cues, width=1080, height=1920, font_name="Hiragino Sans GB",
                font_size=None, margin_v=None):
    font_size = font_size or max(24, int(height * 0.045))
    margin_v = margin_v if margin_v is not None else max(24, int(height * 0.10))
    header = "\n".join([
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: %d" % width,
        "PlayResY: %d" % height,
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,%s,%d,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
        "0,0,0,0,100,100,0,0,1,3,0,2,80,80,%d,1" % (font_name, font_size, margin_v),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ])
    events = []
    for cue in cues:
        body = cue["text"].replace("\n", "\\N")
        events.append("Dialogue: 0,%s,%s,Default,,0,0,0,,%s" % (
            seconds_to_ass(cue["start"]), seconds_to_ass(cue["end"]), body))
    return header + "\n" + "\n".join(events) + "\n"


# ---------------------------------------------------------------- 断句与时间

def split_sentences(text):
    sentences = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        for part in SENT_SPLIT_RE.split(line):
            part = part.strip()
            if part:
                sentences.append(part)
    return sentences


def wrap_sentence(sentence, max_width):
    """按显示宽度折行；优先在标点/空格处断开，避免把英文单词拆散。"""
    lines = []
    current = []
    current_width = 0
    for ch in sentence:
        ch_width = display_width(ch)
        if current_width + ch_width <= max_width:
            current.append(ch)
            current_width += ch_width
            continue
        # 尝试回退到最近标点或空格
        cut = len(current)
        for back in range(len(current) - 1, max(0, len(current) - 8) - 1, -1):
            if current[back] in PUNCT_BREAK:
                cut = back + 1
                break
        if cut <= 0:
            cut = len(current)
        lines.append("".join(current[:cut]).strip())
        rest = current[cut:]
        current = rest + [ch]
        current_width = sum(display_width(c) for c in current)
    if current:
        lines.append("".join(current).strip())
    return [line for line in lines if line]


def build_cues(text, max_width, max_lines):
    sentences = split_sentences(text)
    if not sentences:
        raise SubError("输入文本为空。")
    cues = []
    for sentence in sentences:
        lines = wrap_sentence(sentence, max_width)
        pending = []
        for line in lines:
            pending.append(line)
            if len(pending) == max_lines:
                cues.append({"text": "\n".join(pending)})
                pending = []
        if pending:
            cues.append({"text": "\n".join(pending)})
    return cues


def cue_char_count(cue):
    return len(re.sub(r"\s", "", cue["text"]))


def cue_cps(cue):
    duration = cue["end"] - cue["start"]
    if duration <= 0:
        return float("inf")
    return cue_char_count(cue) / duration


def allocate_timing(cues, total_duration, start, chars_per_sec, min_dur,
                    max_dur, gap, warnings):
    count = len(cues)
    chars = [max(1, cue_char_count(cue)) for cue in cues]
    durations = []
    if total_duration is None:
        durations = [min(max_dur, max(min_dur, ch / chars_per_sec)) for ch in chars]
    else:
        available = total_duration - gap * (count - 1)
        if available <= 0:
            raise SubError("总时长太短：%.2fs 无法容纳 %d 条字幕" % (total_duration, count))
        if available < min_dur * count:
            warnings.append("总时长不足：按 %.2fs/条 均分，低于最小单条时长 %.2fs" %
                            (available / count, min_dur))
            durations = [available / count] * count
        else:
            total_chars = float(sum(chars))
            durations = [max(min_dur, available * ch / total_chars) for ch in chars]
            # 压缩超长条，把余量还给其他条
            for _ in range(8):
                overflow = sum(durations) - available
                if overflow <= 0.001:
                    break
                adjustable = [i for i, d in enumerate(durations) if d > min_dur + 0.01]
                if not adjustable:
                    break
                pool = sum(durations[i] - min_dur for i in adjustable)
                for i in adjustable:
                    durations[i] -= overflow * (durations[i] - min_dur) / pool
            durations = [max(min_dur, min(max_dur, d)) for d in durations]
    cursor = float(start)
    for cue, duration in zip(cues, durations):
        duration = max(0.1, min(max_dur, duration))
        cue["start"] = round(cursor, 3)
        cue["end"] = round(cursor + duration, 3)
        cursor = cue["end"] + gap
    return cues


def parse_plain_text(text):
    """纯文本：每行可选 [开始-结束] 时间区间，缺省由 allocate_timing 自动分配。"""
    cues = []
    manual = 0
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue
        match = INLINE_TIME_RE.match(line)
        if match:
            cues.append({
                "text": match.group(3).strip(),
                "start": parse_time(match.group(1)),
                "end": parse_time(match.group(2)),
            })
            manual += 1
        else:
            cues.append({"text": line, "start": None, "end": None})
    if not cues:
        raise SubError("输入文本为空。")
    return cues, manual


# ---------------------------------------------------------------- 校验

def validate_cues(cues, cps_limit, min_dur, max_dur, max_width, max_lines):
    errors, warnings = [], []
    previous_end = -1.0
    for i, cue in enumerate(cues, 1):
        tag = "第 %d 条「%s」" % (i, cue["text"].replace("\n", "/")[:20])
        duration = cue["end"] - cue["start"]
        if cue["start"] < previous_end - 0.001:
            errors.append("%s 与前一条重叠（start=%.3f < prev_end=%.3f）" %
                          (tag, cue["start"], previous_end))
        if duration <= 0:
            errors.append("%s 时长 <= 0" % tag)
        elif duration < min_dur - 0.001:
            warnings.append("%s 时长 %.2fs < 最小 %.2fs" % (tag, duration, min_dur))
        elif duration > max_dur + 0.001:
            warnings.append("%s 时长 %.2fs > 最大 %.2fs" % (tag, duration, max_dur))
        cps = cue_cps(cue)
        if cps > cps_limit + 0.001:
            warnings.append("%s CPS %.1f > 上限 %.1f（建议加时长或删字）" %
                            (tag, cps, cps_limit))
        lines = cue["text"].split("\n")
        if len(lines) > max_lines:
            warnings.append("%s 行数 %d > %d" % (tag, len(lines), max_lines))
        for line in lines:
            if display_width(line) > max_width:
                warnings.append("%s 行宽 %d > %d：%s" %
                                (tag, display_width(line), max_width, line))
        previous_end = max(previous_end, cue["end"])
    return errors, warnings


# ---------------------------------------------------------------- 能力探测

def detect_filter(name):
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-h", "filter=%s" % name],
                          capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return "Unknown filter" not in output and proc.returncode == 0


def probe():
    result = {"ffmpeg": None, "ffprobe": None, "filters": {}, "pillow": None,
              "recommended_burn_engine": None}
    try:
        proc = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout:
            first = proc.stdout.splitlines()[0]
            match = re.search(r"version\s+(\S+)", first)
            result["ffmpeg"] = match.group(1) if match else first
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout:
            match = re.search(r"version\s+(\S+)", proc.stdout.splitlines()[0])
            result["ffprobe"] = match.group(1) if match else "unknown"
    except (OSError, subprocess.SubprocessError):
        pass
    for name in ("subtitles", "ass", "drawtext", "overlay"):
        result["filters"][name] = detect_filter(name)
    try:
        import PIL
        result["pillow"] = getattr(PIL, "__version__", "unknown")
    except ImportError:
        result["pillow"] = None
    if result["filters"].get("subtitles"):
        result["recommended_burn_engine"] = "libass"
    elif result["pillow"]:
        result["recommended_burn_engine"] = "pillow"
    else:
        result["recommended_burn_engine"] = None
    return result


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SubError("读取输入失败：%s（%s）" % (path, exc))
    except UnicodeDecodeError:
        raise SubError("输入不是 UTF-8：%s（请先转码为 UTF-8）" % path)


def write_text(path, text):
    target = Path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise SubError("写入失败：%s（%s）" % (path, exc))


def infer_format(path, explicit):
    if explicit:
        return explicit
    if path and path.lower().endswith(".ass"):
        return "ass"
    return "srt"


def command_build(args):
    raw = read_text(args.input)
    lookahead = raw[:4000]
    if SRT_ARROW_RE.search(lookahead):
        cues = parse_srt(raw)
        manual = len(cues)
        detected = "srt"
    else:
        cues, manual = parse_plain_text(raw)
        detected = "text"
        if manual and manual != len(cues):
            raise SubError("时间标注混用：请每行都写 [开始-结束]，或全部不写。")
        if manual == 0:
            cues = build_cues(raw, args.max_width, args.max_lines)
        else:
            for cue in cues:
                cue["text"] = "\n".join(wrap_sentence(cue["text"], args.max_width))
    warnings = []
    if manual < len(cues):
        cues = allocate_timing(cues, args.duration, args.start, args.chars_per_sec,
                               args.min_dur, args.max_dur, args.gap, warnings)
    else:
        # 全部带时间区间：仍做基本排序与非法时间检查
        cues.sort(key=lambda cue: cue["start"])
    errors, warns = validate_cues(cues, args.cps_limit, args.min_dur, args.max_dur,
                                  args.max_width, args.max_lines)
    warnings.extend(warns)
    fmt = infer_format(args.out, args.format)
    if fmt == "ass":
        payload = cues_to_ass(cues, args.ass_width, args.ass_height, args.font_name,
                              args.font_size, args.ass_margin_v)
    else:
        payload = cues_to_srt(cues)
    if args.out:
        write_text(args.out, payload)
    elif not args.json:
        sys.stdout.write(payload)
    summary = {
        "input": args.input,
        "detected": detected,
        "format": fmt,
        "out": args.out,
        "cues": len(cues),
        "chars": sum(cue_char_count(cue) for cue in cues),
        "span_s": round(cues[-1]["end"] - cues[0]["start"], 3) if cues else 0,
        "max_cps": round(max(cue_cps(cue) for cue in cues), 2) if cues else None,
        "warnings": warnings,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("生成 %s：%d 条，%.2fs，最大 CPS %.1f → %s" % (
            fmt.upper(), len(cues),
            summary["span_s"], summary["max_cps"], args.out or "stdout"))
        if warnings:
            print("警告 %d 条：" % len(warnings))
            for item in warnings[:10]:
                print("  - %s" % item)
    return 1 if errors else 0


def command_validate(args):
    cues = parse_srt(read_text(args.input))
    errors, warnings = validate_cues(cues, args.cps_limit, args.min_dur, args.max_dur,
                                     args.max_width, args.max_lines)
    report = {
        "input": args.input,
        "cues": len(cues),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "max_cps": round(max(cue_cps(cue) for cue in cues), 2),
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("校验 %s：%d 条 | error %d | warning %d | 最大 CPS %.1f" % (
            args.input, len(cues), len(errors), len(warnings), report["max_cps"]))
        for item in errors:
            print("  ERROR   %s" % item)
        for item in warnings:
            print("  WARN    %s" % item)
    return 1 if errors else 0


def command_retime(args):
    cues = parse_srt(read_text(args.input))
    for cue in cues:
        cue["start"] = round(max(0.0, cue["start"] * args.scale + args.offset), 3)
        cue["end"] = round(max(0.0, cue["end"] * args.scale + args.offset), 3)
        if cue["end"] - cue["start"] < args.min_dur:
            cue["end"] = round(cue["start"] + args.min_dur, 3)
        if cue["end"] - cue["start"] > args.max_dur:
            cue["end"] = round(cue["start"] + args.max_dur, 3)
    cues.sort(key=lambda cue: cue["start"])
    payload = cues_to_srt(cues)
    if args.out:
        write_text(args.out, payload)
    else:
        sys.stdout.write(payload)
    if not args.out:
        print("已重校时 %d 条（offset=%.2fs scale=%.3f）" % (
            len(cues), args.offset, args.scale), file=sys.stderr)
    return 0


def command_probe(args):
    result = probe()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("ffmpeg %s / ffprobe %s / Pillow %s" % (
            result["ffmpeg"], result["ffprobe"], result["pillow"]))
        for name, available in result["filters"].items():
            print("  filter %-10s %s" % (name, "可用" if available else "不可用"))
        print("推荐烧录方式：%s" % (result["recommended_burn_engine"] or "无可用方案"))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="subtitle.py",
        description="字幕文本处理：断句、校时、CPS 校验、SRT/ASS 生成与 FFmpeg 能力探测。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  subtitle.py probe\n"
            "  subtitle.py build --input script.txt --duration 30 --out subs.srt\n"
            "  subtitle.py build --input subs.srt --out subs.ass\n"
            "  subtitle.py validate --input subs.srt\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="探测 ffmpeg 滤镜与 Pillow 能力")
    p_probe.add_argument("--json", action="store_true", help="JSON 输出")
    p_probe.set_defaults(func=command_probe)

    p_build = sub.add_parser("build", help="纯文本/SRT → SRT/ASS（断句 + 校时）")
    p_build.add_argument("--input", "-i", required=True, help="输入文件，- 表示 stdin")
    p_build.add_argument("--out", "-o", help="输出文件；省略则打印到 stdout")
    p_build.add_argument("--format", choices=["srt", "ass"], help="输出格式，默认按 --out 后缀")
    p_build.add_argument("--duration", type=float, help="总时长（秒）；纯文本自动分配时必填")
    p_build.add_argument("--start", type=float, default=0.0, help="首条开始时间（秒）")
    p_build.add_argument("--chars-per-sec", type=float, default=4.5, help="估算语速，默认 4.5 字/秒")
    p_build.add_argument("--max-width", type=int, default=30, help="单行最大显示宽度（中文=2），默认 30")
    p_build.add_argument("--max-lines", type=int, default=2, help="每条最多行数，默认 2")
    p_build.add_argument("--min-dur", type=float, default=0.8, help="单条最短时长（秒）")
    p_build.add_argument("--max-dur", type=float, default=6.0, help="单条最长时长（秒）")
    p_build.add_argument("--gap", type=float, default=0.04, help="条间间隔（秒）")
    p_build.add_argument("--cps-limit", type=float, default=9.0, help="CPS 告警上限，默认 9 字/秒")
    p_build.add_argument("--ass-width", type=int, default=1080, help="ASS 画布宽，默认 1080")
    p_build.add_argument("--ass-height", type=int, default=1920, help="ASS 画布高，默认 1920")
    p_build.add_argument("--ass-margin-v", type=int, help="ASS 底部安全边距（像素）")
    p_build.add_argument("--font-name", default="Hiragino Sans GB", help="ASS 字体名")
    p_build.add_argument("--font-size", type=int, help="ASS 字号；默认 画布高 x 0.045")
    p_build.add_argument("--json", action="store_true", help="JSON 输出摘要")
    p_build.set_defaults(func=command_build)

    p_validate = sub.add_parser("validate", help="校验已有 SRT（重叠/CPS/行宽/时长）")
    p_validate.add_argument("--input", "-i", required=True, help="SRT 文件")
    p_validate.add_argument("--cps-limit", type=float, default=9.0)
    p_validate.add_argument("--min-dur", type=float, default=0.8)
    p_validate.add_argument("--max-dur", type=float, default=6.0)
    p_validate.add_argument("--max-width", type=int, default=30)
    p_validate.add_argument("--max-lines", type=int, default=2)
    p_validate.add_argument("--json", action="store_true")
    p_validate.set_defaults(func=command_validate)

    p_retime = sub.add_parser("retime", help="整体平移/缩放时间轴")
    p_retime.add_argument("--input", "-i", required=True)
    p_retime.add_argument("--out", "-o")
    p_retime.add_argument("--offset", type=float, default=0.0, help="整体偏移（秒），正数延后")
    p_retime.add_argument("--scale", type=float, default=1.0, help="时间轴缩放系数")
    p_retime.add_argument("--min-dur", type=float, default=0.8)
    p_retime.add_argument("--max-dur", type=float, default=6.0)
    p_retime.set_defaults(func=command_retime)
    return parser


def main(argv=None):
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "build" and args.duration is None and args.input == "-" and not sys.stdin.isatty():
        pass
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SubError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        sys.exit(2)
    except BrokenPipeError:
        sys.exit(0)
