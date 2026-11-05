#!/usr/bin/env python3
"""仓库体检：门禁、索引、计数一致性、流水线可运行性、Git 状态。

用法：
  python3 scripts/healthcheck.py              # 严格：脏工作区也算失败
  python3 scripts/healthcheck.py --allow-dirty

退出码：0 全部通过；1 有 FAIL。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(cmd):
    return subprocess.run([PY] + cmd, cwd=str(ROOT), capture_output=True, text=True)


def sh(cmd):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(description="仓库体检")
    ap.add_argument("--allow-dirty", action="store_true", help="允许未提交改动")
    args = ap.parse_args()

    fails, warns, notes = [], [], []

    # 1) 门禁
    v = run(["scripts/validate.py", "--strict"])
    if v.returncode != 0:
        fails.append("validate.py --strict 未通过")
        notes.extend((v.stdout or v.stderr).strip().splitlines()[:10])
    else:
        warns.extend(() for _ in ())

    # 2) 索引最新
    idx = run(["scripts/build_index.py", "--check"])
    if idx.returncode != 0:
        fails.append("INDEX.md 不是最新（运行 python3 scripts/build_index.py）")
        notes.append((idx.stdout or idx.stderr).strip()[:300])

    # 3) 计数一致性：INDEX 统计 vs README / team
    index_text = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    m = re.search(r"\| 知识条目 \| (\d+) \|", index_text)
    m2 = re.search(r"\| SOP \| (\d+) \|", index_text)
    m3 = re.search(r"\| 技能 \| (\d+) \|", index_text)
    counts = {
        "knowledge": int(m.group(1)) if m else None,
        "sop": int(m2.group(1)) if m2 else None,
        "skills": int(m3.group(1)) if m3 else None,
    }
    for path, label in (("README.md", "README"), ("team/README.md", "team/README")):
        text = (ROOT / path).read_text(encoding="utf-8")
        k = re.search(r"知识 (\d+) 条", text)
        s = re.search(r"SOP (\d+) 条", text)
        if counts["knowledge"] and k and int(k.group(1)) != counts["knowledge"]:
            fails.append("%s 知识条数 %s 与 INDEX %s 不一致" % (label, k.group(1), counts["knowledge"]))
        if counts["sop"] and s and int(s.group(1)) != counts["sop"]:
            fails.append("%s SOP 条数 %s 与 INDEX %s 不一致" % (label, s.group(1), counts["sop"]))

    # 4) 流水线定义与阶段脚本
    for p in sorted((ROOT / "pipeline" / "definitions").glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fails.append("流水线定义 JSON 无法解析：%s（%s）" % (p.name, exc))
            continue
        for st in data.get("stages", []):
            script = ROOT / "pipeline" / "stages" / st.get("script", "")
            if not script.exists():
                fails.append("%s 缺少阶段脚本 %s" % (p.name, st.get("script")))
        brief = data.get("run", {}).get("brief")
        if brief and not (ROOT / brief).exists():
            fails.append("%s 缺少 demo brief：%s" % (p.name, brief))
        notes.append("流水线 %s：%d 阶段" % (data.get("name"), len(data.get("stages", []))))

    # 5) 脚本可编译（缓存写 tmp，避免沙箱限制）
    pycache = Path("/tmp/vider-pycache")
    env = {"PYTHONPYCACHEPREFIX": str(pycache), "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"}
    files = [str(p) for p in (ROOT / "pipeline").rglob("*.py")] +             [str(p) for p in (ROOT / "scripts").glob("*.py")] +             [str(p) for p in (ROOT / "skills").rglob("*.py")]
    c = subprocess.run([PY, "-m", "py_compile"] + files, cwd=str(ROOT),
                       capture_output=True, text=True, env=env)
    if c.returncode != 0:
        fails.append("Python 脚本编译失败")
        notes.append((c.stderr or "").strip().splitlines()[-5:])

    # 6) Git 状态
    git = sh(["git", "status", "--short"]) if (ROOT / ".git").exists() else None
    if git and git.stdout.strip():
        msg = "工作区有未提交改动 %d 项" % len(git.stdout.strip().splitlines())
        (warns if args.allow_dirty else fails).append(msg)

    # 7) 关键文件
    for rel in ("README.md", "AGENTS.md", "INDEX.md", "docs/质量门禁.md", "pipeline/README.md"):
        if not (ROOT / rel).exists():
            fails.append("缺少关键文件：%s" % rel)

    print("仓库体检 · %s" % ROOT)
    print("  INDEX：知识 %s / SOP %s / 技能 %s" % (
        counts["knowledge"], counts["sop"], counts["skills"]))
    for n in notes:
        print("  · " + str(n))
    for wmsg in warns:
        print("  WARN  " + wmsg)
    for f in fails:
        print("  FAIL  " + f)
    if fails:
        print("结果：FAIL（%d 项）" % len(fails))
        return 1
    print("结果：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())