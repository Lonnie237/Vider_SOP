#!/usr/bin/env python3
"""生成/校验 INDEX.md。

用法：
  python3 scripts/build_index.py          # 重建 INDEX.md
  python3 scripts/build_index.py --check  # 仅检查是否最新（不一致退出码 1）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb  # noqa: E402

TYPE_ORDER = {"库": 0, "工具": 1, "方法论": 2, "工作流": 3, "环境": 4}
STATUS_ORDER = {"已验证": 0, "可用": 1, "草稿": 2, "归档": 3}


def cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def load_knowledge():
    rows = []
    for p in kb.iter_markdown(kb.ROOT / "knowledge"):
        meta, _, _ = kb.parse_frontmatter(p)
        rows.append((meta, p))
    rows.sort(key=lambda x: (TYPE_ORDER.get(str(x[0].get("type")), 9), str(x[0].get("id"))))
    return rows


def load_sops():
    rows = []
    for p in kb.iter_markdown(kb.ROOT / "sop"):
        meta, _, _ = kb.parse_frontmatter(p)
        rows.append((meta, p))
    rows.sort(key=lambda x: str(x[0].get("id")))
    return rows


def load_skills():
    rows = []
    skills_dir = kb.ROOT / "skills"
    if skills_dir.exists():
        for p in sorted(skills_dir.glob("*/SKILL.md")):
            meta, _, _ = kb.parse_frontmatter(p)
            rows.append((meta, p))
    return rows


def count_status(rows):
    c = {"草稿": 0, "可用": 0, "已验证": 0, "归档": 0}
    for meta, _ in rows:
        s = str(meta.get("status", "草稿"))
        c[s] = c.get(s, 0) + 1
    return c


def render() -> str:
    k = load_knowledge()
    s = load_sops()
    sk = load_skills()
    kc = count_status(k)
    sc = count_status(s)
    templates = sorted((kb.ROOT / "templates").glob("*.md")) if (kb.ROOT / "templates").exists() else []
    docs = sorted((kb.ROOT / "docs").glob("*.md")) if (kb.ROOT / "docs").exists() else []
    scripts = sorted((kb.ROOT / "scripts").glob("*.py")) if (kb.ROOT / "scripts").exists() else []

    lines = []
    lines.append("# INDEX · 全库索引")
    lines.append("")
    lines.append("> 本文件由 `scripts/build_index.py` 自动生成，**不要手改**；新增/修改条目后运行脚本重建。")
    lines.append("")
    lines.append("## 统计")
    lines.append("")
    lines.append("| 类别 | 总数 | 草稿 | 可用 | 已验证 | 归档 |")
    lines.append("|---|---|---|---|---|---|")
    lines.append("| 知识条目 | %d | %d | %d | %d | %d |" % (
        len(k), kc.get("草稿", 0), kc.get("可用", 0), kc.get("已验证", 0), kc.get("归档", 0)))
    lines.append("| SOP | %d | %d | %d | %d | %d |" % (
        len(s), sc.get("草稿", 0), sc.get("可用", 0), sc.get("已验证", 0), sc.get("归档", 0)))
    lines.append("| 技能 | %d | - | - | - | - |" % len(sk))
    lines.append("| 模板 | %d | - | - | - | - |" % len(templates))
    ready = kc.get("可用", 0) + kc.get("已验证", 0) + sc.get("可用", 0) + sc.get("已验证", 0)
    total = len(k) + len(s)
    ratio = (ready * 100 // total) if total else 0
    lines.append("")
    lines.append("可用以上占比：**%d%%**（%d/%d）" % (ratio, ready, total))
    lines.append("")

    lines.append("## 知识库")
    lines.append("")
    if k:
        lines.append("| 标题 | ID | 类型 | 状态 | 更新 | 文件 |")
        lines.append("|---|---|---|---|---|---|")
        for meta, p in k:
            lines.append("| %s | `%s` | %s | %s | %s | [%s](%s) |" % (
                cell(meta.get("title", p.stem)), cell(meta.get("id", "")), cell(meta.get("type", "")),
                cell(meta.get("status", "")), cell(meta.get("updated", "")), p.stem, kb.rel(p)))
    else:
        lines.append("_暂无条目。_")
    lines.append("")

    lines.append("## SOP")
    lines.append("")
    if s:
        lines.append("| 标题 | ID | 形态 | 时长 | 画幅 | 状态 | 更新 | 文件 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for meta, p in s:
            lines.append("| %s | `%s` | %s | %s | %s | %s | %s | [%s](%s) |" % (
                cell(meta.get("title", p.stem)), cell(meta.get("id", "")), cell(meta.get("video_type", "")),
                cell(meta.get("duration", "")), cell(meta.get("aspect", "")), cell(meta.get("status", "")),
                cell(meta.get("updated", "")), p.stem, kb.rel(p)))
    else:
        lines.append("_暂无 SOP。_")
    lines.append("")

    lines.append("## 技能")
    lines.append("")
    if sk:
        lines.append("| 技能 | 用途 | 版本 | 路径 |")
        lines.append("|---|---|---|---|")
        for meta, p in sk:
            desc = str(meta.get("description", ""))
            if len(desc) > 60:
                desc = desc[:60] + "…"
            lines.append("| `%s` | %s | %s | [%s](%s) |" % (
                cell(meta.get("name", p.parent.name)), cell(desc), cell(meta.get("version", "")),
                p.parent.name, kb.rel(p.parent)))
    else:
        lines.append("_暂无技能。_")
    lines.append("")

    lines.append("## 规范与模板")
    lines.append("")
    lines.append("### 规范（docs/）")
    lines.append("")
    for p in docs:
        lines.append("- [%s](%s)" % (p.stem, kb.rel(p)))
    lines.append("")
    lines.append("### 模板（templates/）")
    lines.append("")
    for p in templates:
        lines.append("- [%s](%s)" % (p.stem, kb.rel(p)))
    lines.append("")
    lines.append("### 脚本（scripts/）")
    lines.append("")
    for p in scripts:
        lines.append("- [%s](%s)" % (p.name, kb.rel(p)))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("相关：[README](README.md) · [AGENTS](AGENTS.md) · [知识分类体系](docs/知识分类体系.md) · "
                 "[写作与标注规范](docs/写作与标注规范.md) · [质量门禁](docs/质量门禁.md)")
    lines.append("")
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    content = render()
    idx = kb.ROOT / "INDEX.md"
    current = idx.read_text(encoding="utf-8") if idx.exists() else ""
    if check:
        if current != content:
            print("INDEX.md 已过期，请运行：python3 scripts/build_index.py")
            sys.exit(1)
        print("INDEX.md 是最新的。")
        return
    idx.write_text(content, encoding="utf-8")
    k = load_knowledge()
    s = load_sops()
    sk = load_skills()
    print("已生成 INDEX.md：知识条目 %d，SOP %d，技能 %d" % (len(k), len(s), len(sk)))


if __name__ == "__main__":
    main()
