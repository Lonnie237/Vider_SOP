---
id: kb/manim
title: "Manim · 用 Python 代码生成数学与数据动画"
type: 库
domain: [动效, 剪辑, 自动化]
status: 可用
confidence: 中
license: "MIT"
repo: "https://github.com/ManimCommunity/manim"
docs: "https://docs.manim.community/"
language: Python
platform: [macOS, Linux, Windows]
tags: [动画引擎, 数学动画, 数据可视化, Python, 逐帧渲染, 公式动画]
related: [kb/remotion, kb/code-video-pipeline, kb/ffmpeg, kb/capability-matrix]
updated: 2026-11-03
owner: lead
---

# Manim · 用 Python 代码生成数学与数据动画

## 一句话定位

用 Python 场景代码精确控制图形、公式、坐标轴与数据动画的逐帧生成，适合数学科普、数据解释、公式推导类视频；在流水线中承担 S9 动效包装 / 数据动画渲染。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 精确的数学排版与动画（公式、坐标系、几何变换） | 交互式时间线剪辑与多轨音频 |
| 数据图表的入场/变换/标注动画 | 真人拍摄、实拍素材处理 |
| 可复现的代码化渲染（同一代码同一结果） | 复杂后期调色 / 合成（需交给 NLE 或 FFmpeg） |
| 输出 MP4 / PNG 序列，便于接 FFmpeg 转码与质检 | 低代码/零代码快速出片（要写 Python） |

## 核心能力

- `Scene` + `self.play()` 的动画编排；`Mobject` 场景图。
- 数学排版（`MathTex` 依赖 LaTeX）与文本（`Text` / `MarkupText`，Pango 渲染）。
- 坐标轴、函数图像、条形/折线等图表用 `Axes` / `BarChart` 等构建。
- 多画质档渲染（`-ql` / `-qm` / `-qh`），输出 MP4 或 PNG 序列。
- 可被 Python 脚本编排，适合与数据流水线组合。

## 安装 / 获取

```bash
# 需要 Python 3.11+（PyPI 0.22.1 的 requires-python）
python3.11 -m venv .venv-manim
source .venv-manim/bin/activate
pip install manim
manim --version
```

前提：FFmpeg；系统需 Cairo / Pango（macOS 用 Homebrew 装，Linux 用包管理器；Windows 的 pip wheel 通常自带）。LaTeX 仅在用 `MathTex` 时需要。

## 最小可用示例

```python
# scene.py
from manim import *

class BarDemo(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 4], x_length=8, y_length=5)
        bars = VGroup(*[
            Rectangle(width=0.7, height=v, fill_opacity=0.8, color=BLUE)
            .next_to(axes.c2p(i + 1, 0), UP, buff=0)
            for i, v in enumerate([1.2, 2.0, 1.6, 3.1, 2.6])
        ])
        self.play(Create(axes))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15))
        self.wait(0.5)
```

```bash
manim -qh scene.py BarDemo          # 1920×1080 60fps，输出到 media/videos/
manim -qm --format=png scene.py BarDemo  # PNG 序列，接 FFmpeg
```

预期结果：`media/videos/scene/1080p60/BarDemo.mp4`（或 PNG 序列）。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 数学/数据动画精度高、可复现 | 版本门槛：0.19.2 起最低 Python 3.11，本机 3.9.6 不能直接装 |
| 代码即工程，可进版本管理 | 渲染慢：复杂场景 CPU 渲染可能数分钟到数十分钟 |
| 输出可控，易接 FFmpeg 转码/质检 | 中文字体需显式配置（Pango 字体族），否则回退或方框 |
| 社区活跃（2026-11 约 4.2 万 star） | `MathTex` 依赖 LaTeX，环境不全时报错 |
| MIT 许可，商用友好 | 动画风格偏“教学/几何”，做商业包装需二次设计 |

## 适用 / 不适用

- 适用：数学/物理科普、数据解释、公式推导、需要精确几何变换的动效。
- 不适用：纯剪辑、实拍、批量模板化短视频；替代方案：`kb/remotion`（React 模板化）、`kb/code-video-pipeline`（Pillow/Canvas 轻量渲染）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：[数据可视化动画 SOP](../../sop/long-data-animation.md) 的 S9 渲染备选。
- 关联条目：`kb/remotion`、`kb/code-video-pipeline`、`kb/ffmpeg`。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | 信息核验 | PyPI JSON / GitHub API | 版本 0.22.1，requires-python >=3.11，MIT，仓库 2026-11 活跃 |
| 2026-11-03 | 本机 Python 3.9.6 | `pip install manim` | 未安装：不满足 >=3.11，需另建 3.11+ venv 后补实测 |

## 来源

1. [ManimCommunity/manim](https://github.com/ManimCommunity/manim)（MIT，访问 2026-11-03）
2. [Manim 文档](https://docs.manim.community/)（访问 2026-11-03）
3. [PyPI manim 0.22.1](https://pypi.org/project/manim/)（requires-python >=3.11，访问 2026-11-03）
4. [v0.19.2 changelog](https://docs.manim.community/en/stable/changelog/0.19.2-changelog.html)（最低 Python 提升到 3.11，访问 2026-11-03）