#!/usr/bin/env python3
"""仓库质量门禁：frontmatter / id / 取值 / 死链 / 索引一致性。

用法：
  python3 scripts/validate.py            # 普通校验（缺链为 warning）
  python3 scripts/validate.py --strict   # 验收模式（warning 也算失败）
  python3 scripts/validate.py --check-index  # 同时校验 INDEX.md 是否为最新
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb  # noqa: E402
import build_index  # noqa: E402

errors = []
warnings = []

SECTION_RULES = {
    ("knowledge", "库"): ["一句话定位", "能解决什么", "核心能力", "安装", "最小可用示例",
                       "优缺点", "适用", "关系", "实测记录", "来源"],
    ("knowledge", "工具"): ["一句话定位", "能解决什么", "核心能力", "安装", "最小可用示例",
                         "优缺点", "适用", "关系", "实测记录", "来源"],
    ("knowledge", "方法论"): ["一句话定位", "适用场景", "可操作步骤", "参数与阈值", "常见反例",
                          "验证方式", "来源"],
    ("knowledge", "工作流"): ["一句话定位", "适用场景", "可操作步骤", "参数与阈值", "常见反例",
                          "验证方式", "来源"],
    ("knowledge", "环境"): ["一句话定位", "适用场景", "验证方式", "来源"],
    ("sop", "sop"): ["适用", "交付规格", "前置准备", "流程总览", "分阶段操作", "参数速查",
                     "质量门禁", "常见问题", "可自动化环节", "变体", "复盘与改进", "关联条目"],
    ("skill", "skill"): ["何时使用", "不适用", "输入", "步骤", "输出格式", "失败处理", "自检", "参考"],
}


def normalize(text: str) -> str:
    return "".join(str(text).split()).replace("·", "").replace("/", "")


def check_sections(path, meta, body, kind):
    key = (kind, str(meta.get("type", "")))
    required = SECTION_RULES.get(key)
    if not required:
        return
    heads = re.findall(r"^#{2,3}\s+(.+)$", body, re.M)
    heads_norm = [normalize(h) for h in heads]
    for sec in required:
        if normalize(sec) not in "".join(heads_norm):
            warn("%s: 缺少必备节（%s）" % (kb.rel(path), sec))


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def check_doc(path: Path, kind: str, required, extra=None):
    meta, body, fmerrs = kb.parse_frontmatter(path)
    for e in fmerrs:
        err("%s: %s" % (kb.rel(path), e))
        return meta, body
    for key in required:
        if key not in meta:
            err("%s: 缺少字段 %s" % (kb.rel(path), key))
    if kind == "knowledge":
        if meta.get("type") not in kb.KNOWLEDGE_TYPES and meta.get("type") is not None:
            err("%s: type 取值非法：%s" % (kb.rel(path), meta.get("type")))
        if meta.get("type") in ("库", "工具"):
            for key in kb.REQUIRED_LIB:
                if key not in meta:
                    err("%s: 库条目缺少字段 %s" % (kb.rel(path), key))
    if kind == "sop" and meta.get("type") != "sop":
        err("%s: SOP 的 type 必须为 sop" % kb.rel(path))
    status = meta.get("status")
    if status is not None and status not in kb.STATUS:
        err("%s: status 非法：%s" % (kb.rel(path), status))
    conf = meta.get("confidence")
    if conf is not None and conf not in kb.CONFIDENCE:
        err("%s: confidence 非法：%s" % (kb.rel(path), conf))
    diff = meta.get("difficulty")
    if diff is not None and diff not in kb.DIFFICULTY:
        err("%s: difficulty 非法：%s" % (kb.rel(path), diff))
    upd = meta.get("updated")
    if upd is not None and not re.match(kb.DATE_RE, str(upd)):
        err("%s: updated 必须为 YYYY-MM-DD：%s" % (kb.rel(path), upd))
    if extra:
        extra(meta, path)
    return meta, body


def check_id(meta, path, pattern):
    doc_id = meta.get("id")
    if not doc_id:
        return
    if not re.match(pattern, str(doc_id)):
        err("%s: id 格式非法：%s" % (kb.rel(path), doc_id))
    elif Path(str(doc_id)).name != path.stem:
        err("%s: id (%s) 与文件名 (%s) 不一致" % (kb.rel(path), doc_id, path.stem))
    return doc_id


def main():
    strict = "--strict" in sys.argv
    check_index = "--check-index" in sys.argv

    seen_ids = {}

    # 知识条目
    for p in kb.iter_markdown(kb.ROOT / "knowledge"):
        meta, body = check_doc(p, "knowledge", kb.REQUIRED_KNOWLEDGE)
        check_sections(p, meta, body, "knowledge")
        doc_id = check_id(meta, p, kb.ID_RE)
        if doc_id:
            if doc_id in seen_ids:
                err("%s: id 重复（另见 %s）" % (kb.rel(p), seen_ids[doc_id]))
            seen_ids[doc_id] = kb.rel(p)

    # SOP
    for p in kb.iter_markdown(kb.ROOT / "sop"):
        meta, body = check_doc(p, "sop", kb.REQUIRED_SOP)
        check_sections(p, meta, body, "sop")
        doc_id = check_id(meta, p, kb.SOP_ID_RE)
        if doc_id:
            if doc_id in seen_ids:
                err("%s: id 重复（另见 %s）" % (kb.rel(p), seen_ids[doc_id]))
            seen_ids[doc_id] = kb.rel(p)

    # 技能
    skills_dir = kb.ROOT / "skills"
    if skills_dir.exists():
        for p in sorted(skills_dir.glob("*/SKILL.md")):
            meta, _, fmerrs = kb.parse_frontmatter(p)
            for e in fmerrs:
                err("%s: %s" % (kb.rel(p), e))
            for key in kb.REQUIRED_SKILL:
                if key not in meta:
                    err("%s: 缺少字段 %s" % (kb.rel(p), key))
            if meta.get("name") != p.parent.name:
                err("%s: name 与目录名不一致（%s）" % (kb.rel(p), meta.get("name")))
            body = kb.parse_frontmatter(p)[1]
            check_sections(p, {"type": "skill"}, body, "skill")

    # 相对链接 + TODO 占位
    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    todo_files = []
    for p in kb.iter_markdown(kb.ROOT, skip_readme=False):
        if any(part in kb.SKIP_DIRS for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warn("%s: 非 UTF-8，跳过文本检查" % kb.rel(p))
            continue
        rel_parts = p.relative_to(kb.ROOT).parts
        in_content_scope = bool(rel_parts) and rel_parts[0] in ("knowledge", "sop", "skills")
        if in_content_scope and ("TODO" in text or "待补充" in text):
            todo_files.append(kb.rel(p))
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = target.split("#", 1)[0].strip()
            if not clean:
                continue
            dest = (p.parent / clean).resolve()
            if not dest.exists():
                msg = "%s: 链接目标不存在：%s" % (kb.rel(p), target)
                if p.parts[len(kb.ROOT.parts)] in ("docs", "templates"):
                    warn(msg)
                else:
                    err(msg)

    for f in todo_files:
        warn("%s: 含 TODO/待补充（确认已说明缺什么、谁补）" % f)

    if check_index:
        expected = build_index.render()
        idx = kb.ROOT / "INDEX.md"
        actual = idx.read_text(encoding="utf-8") if idx.exists() else ""
        if expected != actual:
            err("INDEX.md 不是最新，请运行 python3 scripts/build_index.py")

    print("校验完成：%d error, %d warning" % (len(errors), len(warnings)))
    for e in errors:
        print("  ERROR  " + e)
    for wmsg in warnings:
        print("  WARN   " + wmsg)
    if strict and warnings:
        print("--strict：warning 视为失败")
        sys.exit(1)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()