---
id: sop/long-data-animation
title: "数据可视化动画 · 数据到成片的参数化 SOP"
type: sop
video_type: "数据可视化动画"
duration: "30–180s"
aspect: "16:9 / 9:16"
platforms: [B站, YouTube, 抖音, 客户]
difficulty: 高
tools: [Python, Manim, Remotion, FFmpeg, Pillow]
status: 可用
updated: 2026-11-03
owner: sop-long
---

# 数据可视化动画 · SOP

> 读者：把数据做成 30–180s 解释型动画的人或执行 Agent。目标：口径可核、图表不误导、代码可复现，渲染后按统一规格转码交付。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 数据解读、财报 / 报告视频、科普解释 | 真人讲解为主：用 `sop/long-tutorial` |
| 30–180s，1 个结论 + 2–5 个图表；需要批量 / 参数化 | 品牌宣传用 `sop/long-promo`；复杂 3D / 角色动画用专业 3D 工具，本 SOP 不覆盖 |

## 交付规格

| 项 | 横屏主规格（16:9） | 竖屏变体（9:16） |
|---|---|---|
| 分辨率 / 帧率 | 1920×1080 / 30fps 恒定 | 1080×1920 / 30fps 恒定 |
| 视频编码 | H.264 High，VBR 平均 9Mbps / 峰值 12Mbps（6–12Mbps） | H.264 High，VBR 平均 12Mbps / 峰值 16Mbps（8–16Mbps） |
| 音频 / 字幕 | AAC 48kHz 192kbps，-16 LUFS（±1）；外挂 SRT，来源烧录进画面 | AAC 192kbps，-14 LUFS（±1）；字号更大、底部留 15% 安全区 |
| 命名 / 时长 / 交付物 | `<主题>-<时长>-<画幅>-v<版本>-<YYYYMMDD>.mp4`；30–180s；附数据表 + 脚本 + 渲染工程 | 竖屏 15–60s 为主 |

## 前置准备

- 数据：CSV / JSON（列 `label,value,unit,period,source`），时间范围、统计口径、单位、缺失值处理写清；工具：Python 3.9.6 + numpy 2.0.2（本机已装）整理数据，Manim（需 Python ≥3.11，本机装不了）或 Remotion 4.0.540（需 Node 26 / pnpm 12.6，本机已装）做动画，FFmpeg 9.0.2 转码，Pillow 11.3.0 做字幕层。
- 环境限制：本机无 matplotlib，不要用 pyplot 出图，图表靠 Manim / Remotion / Pillow [实测]；中文字体先确认字形完整（缺字出方框）。立项填 [项目Brief](../templates/项目Brief.md)，场景表用 [分镜表](../templates/分镜表.md)（数据动画分镜 = 场景表）。

## 流程总览（阶段 × 产出 × 时间预算）

以 **60–90s 成片** 估算；首条按上限估，复用模板后按 ×0.5。

| 阶段 | 产出 | 时间预算 |
|---|---|---|
| S0–S2 数据 / 图表 / 场景 | 干净数据表 + 口径说明 + 图表清单 + 场景表 | 2.5–3.5h |
| S3–S5 脚本 / 渲染 / 转码 | Manim 或 Remotion 可渲染工程 + FFmpeg 交付版 | 4.5–14h |
| S6–S8 字幕 / 竖屏 / QC | SRT 或烧录 + 9:16 重排版 + QC 记录 | 2–3.5h |

## 分阶段操作

### S0 数据整理

- 口径先定：同一图表内单位、百分比基数、时间范围一致；同比 / 环比写清。数据表统一长表（一行一个观测），来源写进表。
- 每屏先写一句结论（「A 品类连续 3 季度增长」），图表只负责证明它。校验脚本（本机 Python 3.9 + 标准库）：

```bash
python3 - <<'PY'
import csv
rows = list(csv.DictReader(open("data.csv", encoding="utf-8")))
total = sum(float(r["value"]) for r in rows)
print("rows:", len(rows), "missing:", [r["label"] for r in rows if not r["value"]])
print("total:", round(total, 1), "top3 share:", round(sum(sorted((float(r["value"]) for r in rows), reverse=True)[:3]) / total, 3))
PY
```

### S1–S2 图表选择与场景表

| 想表达 | 用 | 不用 / 注意 |
|---|---|---|
| 趋势 | 折线图 | 柱状图不适合连续时间 |
| 对比 | 柱状 / 条形图 | 柱状图 y 轴从 0 开始，否则夸大差异 |
| 占比 | 堆叠条 / 环形图 | 类别 >5 改堆叠条，饼图难读 |
| 分布 / 相关 / 流程 | 直方图 / 散点图 / 漏斗图 | 分箱规则、相关系因果、转化每步口径必须标注 |

- 误导检查：截断坐标轴必须标注；不用双 Y 轴混两种单位；动画中不改变数据排序。
- 场景表列：场景号、时间点、数据、图表、入场动画、旁白 / 字幕、时长；入场 0.3–0.8s、结论停留 ≥2s、单场景 5–15s。

### S3 Manim 脚本（Python 路线）

- 适用数学 / 统计解释、公式与精确几何；MIT 许可证 [事实]。manim 0.22.1 要求 Python ≥3.11，本机 3.9.6 需另建 venv [实测]；装法：`python3.11 -m venv .venv && source .venv/bin/activate && pip install manim==0.22.1`。

```python
# scene.py：柱状图 + 标题 + 入场；输出在 media/videos/scene/1080p30/
from manim import *

class DataChart(Scene):
    def construct(self):
        chart = BarChart([12, 34, 23, 48, 31, 55], max_value=60, bar_colors=[BLUE],
                         axis_config={"include_numbers": True})
        self.play(FadeIn(Text("2026 年季度收入（万元）", font_size=48).to_edge(UP)), Create(chart))
        self.wait(1)
```

```bash
manim -r 1920,1080 --fps 30 scene.py DataChart   # -r 覆盖分辨率，--fps 覆盖帧率
```

- 中文文本依赖 Pango 字体；出现方框时装中文字体并在 `Text(..., font="...")` 指定 [待确认：本机未实测]。

### S4 Remotion 脚本（React 路线）

- 适用数据驱动、模板化批量出片、网页排版；个人 / 非营利 / ≤3 人营利组织免费，超过需 Company License [事实]。本机 Node 26 / pnpm 12.6，2026-11-03 实测渲染通过；装法：`pnpm add remotion@4.0.540 @remotion/cli@4.0.540 react@19.0.0 react-dom@19.0.0`。

```tsx
// src/index.ts
import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";
registerRoot(RemotionRoot);
// src/Root.tsx
import { Composition } from "remotion";
import { DataChart } from "./DataChart";
export const RemotionRoot: React.FC = () => (
  <Composition id="DataChart" component={DataChart} durationInFrames={90}
    fps={30} width={1920} height={1080} defaultProps={{ values: [12, 34, 23, 48, 31, 55] }} />
);
// src/DataChart.tsx
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
export const DataChart: React.FC<{ values: number[] }> = ({ values }) => {
  const frame = useCurrentFrame(), { fps, width, height } = useVideoConfig();
  const p = interpolate(frame, [0, fps * 1.5], [0, 1], { extrapolateRight: "clamp" });
  const w = (width * 0.7) / values.length, max = Math.max(...values); // 柱宽与最大值
  return <AbsoluteFill style={{ backgroundColor: "#0f172a", padding: 120 }}>
    <div style={{ color: "#e2e8f0", fontSize: 56 }}>2026 年季度收入（万元）</div>
    {values.map((v, i) => <div key={i} style={{ position: "absolute", left: 120 + i * w,
      bottom: 160, width: w * 0.6, height: (height * 0.55 * v * p) / max,
      backgroundColor: "#38bdf8" }} />)}
  </AbsoluteFill>;
};
```

```bash
# 3s / 90 帧 / 1920×1080 / 30fps / H.264（2026-11-03 本机实测，输出约 38.7kB）
npx remotion render src/index.ts DataChart out/chart.mp4 --props=props.json
```

### S5 渲染与转码

- Manim / Remotion 输出码率不可控，**一律再用 FFmpeg 转成交付规格**（下方横屏命令本机实测跑通）：

```bash
# 横屏：1080p30 H.264 High VBR 9M（峰值 12M）/ AAC 192k / -16 LUFS
ffmpeg -y -i out/chart.mp4 -i bgm.wav -map 0:v -map 1:a \
  -c:v libx264 -preset medium -profile:v high -level 4.1 \
  -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart chart-16x9.mp4
# 竖屏：1080×1920 / VBR 12M（峰值 16M）/ -14 LUFS；画布在脚本里重排，不裁切
ffmpeg -y -i out/chart_9x16.mp4 -i bgm.wav -map 0:v -map 1:a \
  -c:v libx264 -preset medium -profile:v high -level 4.2 \
  -b:v 12M -maxrate 16M -bufsize 24M -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-14:TP=-1.0:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart chart-9x16.mp4
```

### S6–S7 字幕、来源标注与竖屏版

- 数据来源、口径、时间范围**烧录进画面**（脚本里直接画），不要只放简介；字幕外挂 SRT 优先，烧录走 NLE 或按 [教程 SOP](long-tutorial.md) S7 的 Pillow overlay（本机无 libass，不能用 `subtitles` 滤镜）。
- 竖屏：Remotion 新建 `9x16` Composition（`width=1080, height=1920`）重排；Manim 用 `manim -r 1080,1920 --fps 30`；一屏 1 个数字 + 1 个结论，来源小字放底部安全区。

### S8 QC

按 [QC 清单](../templates/QC清单.md) 逐项过；数据动画额外做数据复核：随机抽 3 个数字回查原始表，核对单位与口径。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 横屏 | 分辨率 / 码率 / 响度 | 1920×1080 / VBR 9M（峰值 12M） / -16 LUFS |
| 竖屏 | 分辨率 / 码率 / 响度 | 1080×1920 / VBR 12M（峰值 16M） / -14 LUFS；节奏 0.3–0.8s 入场、结论 ≥2s |

## 质量门禁（QC）

- [ ] 数据可核：每个数字能回查原始表，单位 / 口径 / 时间范围已标注
- [ ] 图表不误导：柱状图 0 起点、无双 Y 轴混单位、截断轴已标注
- [ ] 每屏 1 个结论，屏幕文字 ≤2 行，手机端预览可读
- [ ] 规格达标：分辨率 / 帧率 / 码率 / 音频 / 响度（ffprobe 核对）
- [ ] 动画节奏：入场不拖沓、结论 ≥2s、场景切换无跳变；字幕与旁白同步、专名 / 数字无误
- [ ] 字体授权与字形完整（无方框）；竖屏重排而非裁切、信息不出安全区；工程可复现（数据表 + 脚本 + 命令 + 版本）

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 数字对不上 / 被观众抓错 | 口径混用、单位没统一 | S0 先写口径说明，随机抽样回查原始表 |
| 图表夸大差异 | 柱状图 y 轴不从 0、截断未标注 | 柱状图从 0 起；必须截断时加断轴标记与说明 |
| 本机装不上 Manim | Python 3.9 < 要求的 3.11 | 用独立 venv 装 Python 3.11+ 后再 pip install manim |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 数据校验 / 参数化出片 | csv + numpy 脚本；Remotion props | 本 SOP S0、`kb/remotion` |
| 转码 / 响度 / 字幕层 | FFmpeg + Pillow PNG 序列 | `kb/ffmpeg`、`kb/transcode-delivery` |

## 流水线实现（数据动画样板）

> 本 SOP 已有一条可执行流水线：[pipeline/definitions/data-viz-animation.json](../pipeline/definitions/data-viz-animation.json)。

| 阶段 | 实现 | 产出 |
|---|---|---|
| S0–S2 | 初始化 / 旁白校验 / TTS | 项目目录、脚本、voice.json |
| D3 数据 | [d3_data.py](../pipeline/stages/d3_data.py) | 数据校验、逐年排名、年份关键帧、storyboard.json |
| D4 渲染 | [d4_render.py](../pipeline/stages/d4_render.py) | 逐帧条形竞速 / 折线 / 环图 → base.mp4、封面、静帧、接触表 |
| S5–S8 | 响度合板 / 字幕 / 导出 / QC | 成片、QC 报告 |

运行：

```bash
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json
# 只调画面：--from D4-render --force
```

实测记录（2026-11-03，三种图表共用 D4）：

| 图表 | brief.dataviz.chart | 成片 | 质检 |
|---|---|---|---|
| 条形竞速 | `bar-race` | 37.6s / 2.4MB | PASS |
| 折线/面积 | `line` | 33.6s / 2.3MB | PASS |
| 环图 | `donut` | 23.2s / 1.5MB | PASS |

规格统一 1920×1080 / 30fps / -14.2 LUFS；逐帧渲染 9–14s；帧数均通过 `round(duration×30)` 校验。地图、饼图（非环图）待扩展。

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| B站 | 16:9，30–180s；标题 / 封面写结论，简介补数据来源 |
| YouTube | 16:9；官方建议 1080p 30fps SDR 上传 8Mbps；前 30s 给结论，简介附来源 |
| 抖音 / 视频号 | 9:16，15–60s；1080×1920 / 8–16Mbps / -14 LUFS；一屏一个数字，字幕 64–72px |
| 客户交付 | 16:9 + 9:16 双版，附数据表、脚本、渲染工程、来源清单；ProRes 母版另存 |

## 复盘与改进

- 实测记录（2026-11-03）：Remotion 4.0.540 最小示例在本机（Node 26 / pnpm 12.6）渲染成功：3s / 90 帧 / 1920×1080 / 30fps / H.264，输出约 38.7kB；FFmpeg 转码到 VBR 9M + AAC 192k + -16 LUFS 通过。Manim 未实测（本机 Python 3.9.6 不满足 ≥3.11）；数据校验脚本是骨架，未接真实数据。

## 关联条目

- 方法论：`kb/narrative-structure`、`kb/color-grading`；工作流 / 库：`kb/manim`、`kb/remotion`、`kb/ffmpeg`、`kb/transcode-delivery`、`kb/opentimelineio`
- 方法与实现：`kb/code-video-pipeline`（帧=f(t)、剪辑表驱动）；[数据动画流水线](../pipeline/definitions/data-viz-animation.json)
- 兄弟 SOP：`sop/long-promo`、`sop/long-tutorial`

## 来源

1. 本机实测（2026-11-03）：`node -v` → 26.12.0、`pnpm -v` → 12.6.0、`python3 -V` → 3.9.6、`ffmpeg -version` → 9.0.2；`import matplotlib` → ModuleNotFoundError；remotion render 成功（90 帧 / 1920×1080 / 30fps）。
2. [Manim on PyPI](https://pypi.org/project/manim/)（访问 2026-11-03）：0.22.1，Requires-Python ≥3.11；[ManimCommunity/manim](https://github.com/ManimCommunity/manim)：MIT，42,164 stars，2026-11-02 仍有提交。
4. [Remotion on npm](https://www.npmjs.com/package/remotion)（访问 2026-11-03）：4.0.540；[许可证 FAQ](https://www.remotion.dev/docs/license/faq)：个人 / 非营利 / ≤3 人组织免费；[YouTube 推荐上传编码设置](https://support.google.com/youtube/answer/1722171)：1080p 标准帧率 8Mbps、高帧率 12Mbps（访问 2026-11-03）。
5. [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）。