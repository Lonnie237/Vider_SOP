#!/usr/bin/env python3
"""流水线共享工具：路径、JSON、子进程、ffprobe、字体与文本换行。仅标准库 + Pillow。"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "pipeline"
PY = "python3"


class StageError(RuntimeError):
    pass


def now():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def run(cmd, cwd=None, timeout=1800):
    cmd = [str(c) for c in cmd]
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-12:]
        raise StageError("命令失败（exit %d）：%s\n%s" % (proc.returncode, " ".join(cmd), "\n".join(tail)))
    return proc


def run_soft(cmd, cwd=None, timeout=1800):
    cmd = [str(c) for c in cmd]
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, timeout=timeout)


def ffprobe_json(path):
    proc = run(["ffprobe", "-v", "error", "-print_format", "json",
                "-show_format", "-show_streams", str(path)])
    return json.loads(proc.stdout)


def duration_of(path):
    return float(ffprobe_json(path)["format"]["duration"])


def media_summary(path):
    info = ffprobe_json(path)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), {})
    return {
        "path": repo_rel(path),
        "duration_s": round(float(info["format"]["duration"]), 3),
        "size_mb": round(int(info["format"].get("size", 0)) / 1048576, 2),
        "width": v.get("width"),
        "height": v.get("height"),
        "fps": v.get("r_frame_rate"),
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"),
        "sample_rate": a.get("sample_rate"),
        "channels": a.get("channels"),
    }


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path(run_dir):
    return Path(run_dir) / "_pipeline" / "run.json"


def load_state(run_dir):
    p = state_path(run_dir)
    return load_json(p) if p.exists() else {}


def save_state(run_dir, state):
    save_json(state_path(run_dir), state)


def brief(run_dir):
    return load_json(Path(run_dir) / "_pipeline" / "brief.json")


def manifest(run_dir):
    return load_json(Path(run_dir) / "manifest.json")


def repo_rel(path):
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def emit(summary):
    print(json.dumps(summary, ensure_ascii=False))


def find_cjk_font():
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    raise StageError("找不到可用的中文字体（期望 Hiragino / STHeiti / Songti）")


def wrap_text(draw, text, font, max_width):
    lines = []
    cur = ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        trial = cur + ch
        width = draw.textbbox((0, 0), trial, font=font)[2]
        if width > max_width and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines
