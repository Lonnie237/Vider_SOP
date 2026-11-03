#!/usr/bin/env python3
"""共享工具：frontmatter 解析、仓库扫描、常量。无第三方依赖。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

STATUS = {"草稿", "可用", "已验证", "归档"}
CONFIDENCE = {"高", "中", "低"}
DIFFICULTY = {"低", "中", "高"}
KNOWLEDGE_TYPES = {"库", "工具", "方法论", "工作流", "环境"}

REQUIRED_KNOWLEDGE = ["id", "title", "type", "domain", "status", "confidence",
                      "tags", "related", "updated", "owner"]
REQUIRED_LIB = ["license", "repo", "docs", "language", "platform"]
REQUIRED_SOP = ["id", "title", "type", "video_type", "duration", "aspect",
                "platforms", "difficulty", "tools", "status", "updated", "owner"]
REQUIRED_SKILL = ["name", "description", "version"]

ID_RE = r"^kb/[a-z0-9][a-z0-9-]*$"
SOP_ID_RE = r"^sop/[a-z0-9][a-z0-9-]*$"
DATE_RE = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "tmp", "cache", "exports", "media", "runs"}


def parse_inline_list(raw: str) -> List[str]:
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return []
    inner = raw[1:-1].strip()
    if not inner:
        return []
    items, buf, quote = [], [], None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf).strip())
    return [clean_scalar(x) for x in items if x]


def clean_scalar(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def parse_frontmatter(path: Path) -> Tuple[Dict[str, object], str, List[str]]:
    """返回 (frontmatter dict, body, errors)。"""
    errors: List[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {}, "", ["文件不是 UTF-8 编码"]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["缺少 frontmatter（文件应以 --- 开头）"]
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text, ["frontmatter 未闭合（缺少结尾 ---）"]
    meta: Dict[str, object] = {}
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t" and line.strip().startswith("- "):
            i += 1
            continue
        if ":" not in line:
            errors.append("frontmatter 第 %d 行无法解析：%s" % (i + 1, line[:40]))
            i += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "":
            items: List[str] = []
            j = i + 1
            while j < end and (not lines[j].strip() or lines[j].strip().startswith("- ")):
                if lines[j].strip().startswith("- "):
                    items.append(clean_scalar(lines[j].strip()[2:]))
                j += 1
            meta[key] = items
            i = j
            continue
        if raw.startswith("["):
            meta[key] = parse_inline_list(raw)
        else:
            meta[key] = clean_scalar(raw)
        i += 1
    body = "\n".join(lines[end + 1:])
    return meta, body, errors


def iter_markdown(base: Path, skip_readme: bool = True) -> List[Path]:
    out: List[Path] = []
    if not base.exists():
        return out
    for p in sorted(base.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if skip_readme and p.name.lower() == "readme.md":
            continue
        if "_templates" in p.parts:
            continue
        out.append(p)
    return out


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)