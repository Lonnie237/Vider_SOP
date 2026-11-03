---
id: kb/automation-pipeline
title: 自动化流水线 · ffmpeg-first 的幂等编排
type: 工作流
domain: [自动化, 转码, 字幕, 交付]
status: 可用
confidence: 高
tags: [自动化, 流水线, ffmpeg, 幂等, 重试, 编排, 日志]
related: [kb/asset-management, kb/transcode-delivery, kb/platform-specs, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 自动化流水线 · ffmpeg-first 的幂等编排

> 原则：能用 FFmpeg 滤镜与 Python 标准库解决的，不上框架；只有程序化动效 / 数学动画才引入 Remotion / Manim。流水线必须「可重跑、失败可续、产物可追溯」。

## 一句话定位

把「素材 → 粗剪 → 字幕 → 包装 → 导出 → QC」串成以 manifest 驱动的批处理，单条失败不拖垮整批、重跑只补未完成项。用在 S9–S11 批量产出；判断标准是第二次运行全部 SKIP、失败项有日志、产物命名与目录可预测。

## 适用场景

- 适用：批量口播 / 切片 / 混剪、同一模板的多平台导出、每日更新栏目、历史素材重制。
- 不适用：一次性精剪、需要逐帧手工调整的创意片（人工 NLE 更快）；需要复杂 3D / 粒子（走 Blender）。

## 流程设计

阶段 × 输入 × 输出（每个阶段产物落盘并打 `.ok` 标记）：

| 阶段 | 输入 | 工具 | 输出 | 幂等标记 |
|---|---|---|---|---|
| 0 探针 | manifest | ffmpeg / python / df | `04_logs/preflight.json` | — |
| 1 粗剪 | 原素材或代理 | ffmpeg concat / trim | `02_work/01_cut.mp4` | `.cut.ok` |
| 2 字幕 | SRT + Pillow | `overlay` | `02_work/02_subbed.mp4` | `.sub.ok` |
| 3 包装 | 字幕版 | overlay logo / xfade | `02_work/03_packaged.mp4` | `.pack.ok` |
| 4 导出 | packaged | libx264 + loudnorm | `03_output/<id>.mp4` | `.ok` |
| 5 QC | 输出 | ffprobe / ebur128 | `04_logs/qc.json` | — |

目录与 manifest：项目根放 `manifest.json`（唯一事实来源）与 `run.py`（只用标准库）；`01_input/` 原素材、`02_work/` 中间产物、`03_output/` 最终产物、`04_logs/` 日志。

```json
{
  "version": 1,
  "jobs": [
    {"id": "ep01", "input": "01_input/ep01.mp4", "output": "03_output/ep01.mp4"},
    {"id": "ep02", "input": "01_input/ep02.mp4", "output": "03_output/ep02.mp4"}
  ]
}
```

## 可操作步骤

1. 写 manifest：任务 id、输入、输出、可选参数（平台、响度目标）；id 与输出名一一对应。产出：`manifest.json`。
2. 预检：检查 ffmpeg / 滤镜 / Python 包 / 磁盘；任何一项失败直接退出（退出码 2），避免半批产物。产出：`preflight.json`。
3. 跑阶段：每个阶段一条命令、一个产物、一个 `.ok`；命令失败重试 2 次，仍失败记入日志并继续下一条。产出：中间产物。
4. 原子落盘：先写 `*.part.mp4`，成功后 `mv` 为正式名，再写 `.ok`；崩溃不会留下「看似完成」的文件。产出：可安全重跑。
5. 日志：每次运行追加 `04_logs/run.jsonl`（时间、job、阶段、状态、耗时、退出码）。产出：可追溯记录。
6. QC 与汇总：对 `03_output` 跑 ffprobe / ebur128，生成 `qc.json`；脚本以失败数作为退出码。产出：QC 报告。
7. 断点续跑：删掉某个 `.ok` 再运行，只补该条；全量重跑前先归档 `03_output`。产出：增量更新。

编排脚本（[实测] 2026-11-03：2 条任务运行两遍，第一遍 DONE×2，第二遍 SKIP×2、failed: 0）：

```python
import json, os, subprocess, sys

root = sys.argv[1]
manifest = json.load(open(os.path.join(root, "manifest.json"), encoding="utf-8"))
os.makedirs(os.path.join(root, "03_output"), exist_ok=True)
failed = 0

for job in manifest["jobs"]:
    dst = os.path.join(root, job["output"])
    if os.path.exists(dst) and os.path.exists(dst + ".ok"):
        print("SKIP", job["id"]); continue
    tmp = dst + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", os.path.join(root, job["input"]),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "192k", tmp]
    for attempt in range(1, 3):
        if subprocess.run(cmd).returncode == 0:
            break
        print("RETRY", job["id"], "attempt", attempt)
    else:
        print("FAIL", job["id"]); failed += 1; continue
    os.replace(tmp, dst)
    open(dst + ".ok", "w").write("ok")
    print("DONE", job["id"])

print("failed:", failed)
sys.exit(1 if failed else 0)
```

预检命令（本机无 libass，必须探测后再决定字幕路径）：

```bash
ffmpeg -version | head -1
ffmpeg -hide_banner -filters 2>/dev/null | grep -qw subtitles && echo libass=yes || echo libass=no
python3 -c "import PIL; print('Pillow', PIL.__version__)"
df -h . | tail -1
```

Node 26 也可编排（`node:child_process` 的 `spawnSync` 同样逻辑）；本仓默认 Python 标准库，减少依赖。

### 何时该上 Remotion / Manim

| 需求 | 选择 | 理由 |
|---|---|---|
| 裁剪 / 拼接 / 转场 / 字幕 / 水印 / 响度 / 批量导出 | FFmpeg + Python | 无渲染框架开销，命令可审计 |
| React 组件化动效、数据驱动模板、精确排版 | Remotion | 组件复用、时间轴即代码 |
| 数学 / 几何动画、公式推导 | Manim | 现成数学对象与动画 API |
| 3D / 复杂粒子 | Blender（VSE 或脚本） | FFmpeg 滤镜无法胜任 |

判断标准：如果一条命令能表达清楚，就不上框架；需要「程序化生成每一帧的画面结构」才考虑 Remotion / Manim [推断]。

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| 并发数 | 2–4（`min(4, 物理核/2)`） | [推断] 内存与编码器排队 | 24GB 机器建议 ≤ 4 |
| 单任务超时 | 短视频 600s；长视频 1800s | [推断] | 超时按失败处理并终止子进程 |
| 重试次数 | 2 次（共 3 次机会） | [推断] | 瞬时错误有效，逻辑错误不重试 |
| 幂等标记 | 输出文件 + `.ok` | [实测] 二次运行全 SKIP | 标记与产物同目录 |
| 原子落盘 | `*.part` → rename | [推断] | 避免半成品被当成完成 |
| 日志 | JSONL，追加写 | [推断] | 便于 grep / 汇总 |
| 磁盘阈值 | 可用 < 10% 停止 | [推断] | 预检阶段判断 |
| 中间产物 | 可删可重建 | [推断] | `02_work` 不备份 |
| 失败策略 | 单条失败继续，末尾 exit 1 | [推断] | 批量不中断 |
| 输出命名 | `<id>_<平台>_v1_<日期>.mp4` | 本仓规范 | 见 [转码与交付](transcode-delivery.md) |

## 失败处理

| 失败 | 症状 | 处理 |
|---|---|---|
| ffmpeg 缺失 | 命令 127 / preflight 失败 | 预检退出码 2，不启动批处理 |
| 单条编码失败 | 某 job FAIL，其余继续 | 重试 2 次；仍失败写日志，人工看该条 |
| 半成品文件 | 输出存在但播放失败 | 用 `.part` + rename；重跑覆盖 |
| 磁盘写满 | 编码中断、ENOSPC | 清理 `02_work` 或换盘；保留 manifest 与日志 |
| 字体缺失 | Pillow 报 `OSError` | 预检探测字体，回退到 STHeiti 并告警 |
| 字幕滤镜不存在 | `Unknown filter 'subtitles'` | 本机走 Pillow overlay（见 [字幕与信息密度](../方法论/subtitle-density.md)） |
| 输入缺失 | 找不到文件 | 标记 `SKIP_MISSING`，不中断整批 |
| 并发过高 | 内存压力、编码变慢 | 降到 2；长视频串行 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 每次全量重跑 | 浪费数小时，覆盖已人工修过的产物 | manifest + `.ok` 幂等 |
| 文件列表写死在脚本里 | 加一条要改代码 | 用 manifest 驱动 |
| 不检查子进程退出码 | 失败被当成成功，交付空文件 | 检查 returncode，失败记日志 |
| 无日志 / 只 print | 出问题无法定位是哪条、哪步 | JSONL 日志 + 退出码 |
| 并发开到核数 | 内存爆、编码器互相抢 | 2–4 并发，长任务串行 |
| 中间文件与成品同目录 | 误交付 `.part` / 中间版 | `02_work` 与 `03_output` 分离 |
| 用超长 shell 管道拼逻辑 | 难维护、难重试 | Python 编排，单阶段单命令 |

## 验证方式

- 幂等（[实测] 2026-11-03，Python 3.9.6 + ffmpeg 9.0.2）：连续运行两次，第二次输出 `SKIP job1 / SKIP job2 / failed: 0`。
- 断点续跑：删一个 `.ok` 再运行，应只重做该条；其余 SKIP。
- 产物：`ffprobe -v error -show_entries format=duration,size -of json 03_output/*.mp4` 条数与 manifest 一致。
- 日志：`grep -c '"status": "failed"' 04_logs/run.jsonl` 为 0；耗时分布可排序。
- 失败信号：退出码 0 但输出缺失；第二次运行不 SKIP；`02_work` 残留 `.part` 文件。

## 关联条目

- 工作流：[素材管理与代理剪辑](asset-management.md)、[转码与交付](transcode-delivery.md)、[平台规格与发布](platform-specs.md)
- 方法论：[字幕与信息密度](../方法论/subtitle-density.md)、[声音设计](../方法论/sound-design.md)
- 环境：[本机环境](../环境/environment-local.md)
- 技能：`ffmpeg-render`、`subtitle-pipeline`、`qc-deliver`
- 落地 SOP：`sop/short-live-clip`、`sop/long-data-animation`

## 来源

1. [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）：命令行与滤镜参考。
2. [Python 标准库 subprocess 文档](https://docs.python.org/3/library/subprocess.html)（访问 2026-11-03）：子进程与退出码。
3. [Remotion 官网](https://www.remotion.dev/)（访问 2026-11-03）：React 程序化视频。
4. [Manim Community 文档](https://www.manim.community/)（访问 2026-11-03）：数学动画。
5. 本机实测（2026-11-03，Python 3.9.6，Node 26.12.0，ffmpeg 9.0.2）：`run.py` 在 2 条任务上连跑两遍，第二遍全 SKIP、failed: 0；预检命令可执行。
6. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）。
