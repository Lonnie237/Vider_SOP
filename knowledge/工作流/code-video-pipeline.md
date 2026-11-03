---
id: kb/code-video-pipeline
title: 纯代码视频管线 · 帧=f(t)、剪辑表驱动、分段闭环
type: 工作流
domain: [动效, 剪辑, 自动化, 交付]
status: 可用
confidence: 高
tags: [纯代码视频, 逐帧渲染, 确定性, 剪辑表, 数据动画, ffmpeg, Playwright]
related: [kb/remotion, kb/manim, kb/automation-pipeline, kb/transcode-delivery]
updated: 2026-11-03
owner: lead
---

# 纯代码视频管线 · 帧=f(t)、剪辑表驱动、分段闭环

## 一句话定位

把视频画面当成「时间的纯函数」来写：所有段的时间参数集中在一份剪辑表，渲染器按 `t` 逐帧出图、管道给 FFmpeg，配乐/字幕/质检共用同一套时间常数——适合数据动画、动效包装、风格展示片等**可参数化**的视频。

## 适用场景

- 数据可视化动画、图表竞速、信息图动效、排行榜、年度回顾。
- 需要可复现、可 diff、可批量重跑的视频（同一输入必出同一帧）。
- 没有实拍素材、但需要电影感包装的内容。
- 不适用：真人出镜、写实叙事、需要生成式模型的画面。

## 可操作步骤

1. **锁定 brief**：题材、画幅/平台、时长、风格/主题、结尾 CTA。
2. **写剪辑表**：每个段 `[start, end, type, params]` 落成一份 JSON；所有渲染、音频、字幕都读它。
3. **定义渲染契约**：渲染器接收 `t`（或 `u=t/duration`），只依赖时间与常量；禁止随机数、系统时间、CSS 动画。
4. **逐段闭环**：设计 → 实现 → 抽 4–6 张静帧 → 接触表检查 → 整段渲染 → ffprobe 帧数校验（`== round(duration×30)`）。
5. **画面管道化**：帧直接写入 `ffmpeg -f rawvideo` 或 `image2pipe`，不落盘；分段编码参数保持一致，便于 `-c copy` 拼接。
6. **声音分轨**：旁白（TTS/真人）与 BGM/音效分轨，统一响度；若做卡点，音频与画面共用 BPM/时间常数。
7. **合成与质检**：concat → 混音 → 2-pass 或 CRF 编码 → 规格/响度/黑帧/帧数/命名 QC → 人工看片。

## 参数与阈值

| 参数 | 推荐值 | 依据 |
|---|---|---|
| 帧率 | 30fps（与交付一致） | 平台通用；数据动画 30 足够 |
| 每段时长 | 1–6s；随旁白句子切段 | 便于单段重渲与排错 |
| 静帧抽检点 | 段内 0.2 / 0.8 / 1.4 / 2.0 / 2.6s | 覆盖入场、主画面、收尾 |
| 帧数误差 | 0 帧（`round(duration×30)`） | 防止音画漂移 |
| 编码 | H.264 High + AAC 48k；2-pass 或 CRF 18–23 | 兼容性与体积平衡 |
| 响度 | 短视频 -14 LUFS / 长视频 -16 LUFS | 与平台一致 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 画面依赖 `Math.random` / `Date.now` | 每次渲染都不一样，无法复现与对比 | 用固定 seed/hash(t) 生成随机感 |
| 先写完全部段再渲染 | 一个全局错误导致全片重来 | 先跑通 1 段，再复制 |
| 段之间编码参数不一致 | concat `-c copy` 失败或时间漂移 | 统一分辨率/帧率/像素格式/编码 preset |
| 只做整片 QC，不查帧数 | 音画错位到结尾才暴露 | 每段 `ffprobe -count_frames` |
| 用屏幕录制代替逐帧渲染 | 分辨率/帧率不稳，不可复现 | 代码渲染 + 固定时间轴 |
| 忽略字体与缺字 | 中文变方框/回退字体，风格崩 | 字体本地化 + 渲染前 `document.fonts.ready` |

## 验证方式

- 确定性：同一 `t` 连续渲染两次，帧哈希一致（或像素 diff = 0）。
- 完整性：每段帧数 = `round(duration×30)`；全片时长与剪辑表一致。
- 音画同步：抽 3 个卡点帧，核对画面切换与音频瞬态在同一帧。
- 交付：QC 报告 PASS；接触表/静帧人工复核无溢出、无缺字。

## 来源

1. [Moessif/code-video-showcase](https://github.com/Moessif/code-video-showcase)（MIT，访问 2026-11-03）：10 阶段工作流、帧=f(t) 渲染契约、分段闭环、2-pass 与 QA 方法。
2. 仓库 `references/render-pipeline.md`、`references/style-recipes.md`、`templates/common.js`（访问 2026-11-03）。
3. 本仓调研笔记：[2026-11-03-code-video-showcase](../../research/2026-11-03-code-video-showcase.md)。
4. 本仓落地实现：[pipeline/definitions/data-viz-animation.json](../../pipeline/definitions/data-viz-animation.json)、[pipeline/stages/d4_render.py](../../pipeline/stages/d4_render.py)。