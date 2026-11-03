# code-video-showcase 调研笔记（Moessif/code-video-showcase）

- 日期：2026-11-03
- 调研人：lead
- 来源仓库：https://github.com/Moessif/code-video-showcase （MIT）
- 目标：学习其「纯代码做视频」的方法论，判断哪些能迁移到本仓的数据可视化动画流水线。

## 1. 它是什么

一个 **Agent Skill**（不是库、不是模型）：用 HTML/Canvas/SVG/Three.js 逐帧绘制画面，用 Python（numpy/scipy）合成配乐，FFmpeg 合成 30–90s 卡点风格展示片。全程不调用任何视频/图像/音乐生成模型。

核心产物：
- 10 阶段工作流（需求采集 → 剪辑表 → 环境 → 工程骨架 → 逐段实现 → 开场 → 大字卡 → 八连闪/结尾 → 配乐 → 合成质检）
- 剪辑结构公式：`总时长 = O + N·R + 1 + 2 + E`（8 + 11×4 + 1 + 2 + 6 = 61s）
- 11 种风格配方（含「07 数据可视化 · 播放量竞速」）
- 8 套主题配色、大字卡系统、120 BPM 配乐合成
- Playwright 逐帧渲染器 + 段 concat + 2-pass 编码 + QA 清单
- 可运行模板：`segment.html`、`big-card.html`、`common.js`、`render-segment.mjs`、`synth_audio.py`

## 2. 可复用的工程原则（比代码更值钱）

| 原则 | 具体做法 | 对本仓的意义 |
|---|---|---|
| 画面是时间的纯函数 | `window.renderFrame(t)` 只依赖 t 与常量；禁用 CSS animation / rAF / Date.now / Math.random | 同一 t 必出同一帧，可重跑、可 diff、可断点续渲 |
| 剪辑表驱动 | 所有段 `[start,end,type,style,t0,speed]` 落在同一份 JSON，画面与音频共用 | 与我们 `storyboard.json` 的思路一致，避免参数散落 |
| 分段闭环 | 每段：设计 → 写 HTML → 抽 5–6 张静帧 → 接触表 → 整段渲染 → ffprobe 帧数 | 先跑通 1 段再复制，错误成本最低 |
| 帧数校验 | `ffprobe -count_frames` 必须等于 `round(duration×30)` | 我们已把这条加进数据动画渲染阶段 |
| 渲染即管道 | 帧直接写入 ffmpeg stdin，不落盘 | 避免小文件 IO，长片段更稳 |
| 合成音频 | 120 BPM、A 小调，与剪辑表共用时间常数，频谱图复核 | 我们当前用 TTS 旁白；后续可加节拍音效层 |
| 2-pass 编码 | concat 后统一 2-pass，`-shortest -t` 截齐时长 | 我们目前单遍 VBR；数据动画可评估切 2-pass |
| 素材资产化 | 主题、字体、配方全部本地化、可预览 | 数据动画需要固定配色与字体，值得照做 |

## 3. 数据可视化配方（07 数据可视化「播放量竞速」）

- 观感：电影级数据新闻，暗底紫红光雾、发光条、玻璃拟态
- 调色：`bg #0a0710` + 紫红雾（#6a2c70 / #ff5a4a）；bars #7b5cff → #ff5a4a；年份描边大字 rgba(255,255,255,.18)；玻璃卡 rgba(255,255,255,.08)
- 构图：标题左上 → 7 条横向条形（标签左、数值右）→ 右侧巨大描边年份 2019→2026 → 右下玻璃卡结论 → 脚注「示例数据 · 仅作演示」
- 动效：每拍推进一年；年份跳变缩放脉冲；条形长度按年份插值；高亮条珊瑚红发光；结尾玻璃卡淡入上浮
- 音色建议：方波琶音（每拍）+ 年份滴答 + 数据条 whoosh

这套配方几乎可以逐条映射为 Pillow/ffmpeg 实现：渐变光雾、发光条、描边大字、玻璃卡、脚注。

## 4. 它的限制

1. **依赖重**：Node 20+、Playwright/Chromium、本地字体、numpy/scipy；大陆网络下浏览器下载可能很慢。
2. **风格定位**：为「多风格卡点展示片」设计，不是数据新闻/教程类；数据动画只是其中一段 3s 配方。
3. **没有成片 demo**：仓库只有分析资产与模板，需自行拼装验证。
4. **配乐是合成器风格**：适合燃向展示，不适合知识讲解（我们需要 TTS 旁白 + 轻 BGM）。

## 5. 我们的取舍（迁移到本仓）

| 采用 | 不采用（当前阶段） |
|---|---|
| 帧=f(t) 的确定性渲染、剪辑表驱动、分段闭环、帧数/静帧/接触表 QA | Playwright + HTML 渲染（依赖重；先用 Pillow/ffmpeg 验证链路） |
| 数据可视化配方的配色/构图/动效语言 | 11 风格卡点片的整体结构（与数据新闻目标不同） |
| 2-pass 与 concat 的工程习惯 | 合成配乐（当前先 TTS 旁白，后续加 BGM 层） |

落地：
- 新流水线 [pipeline/definitions/data-viz-animation.json](../pipeline/definitions/data-viz-animation.json)（复用 TTS/字幕/混音/导出/QC，替换画面为数据动画渲染器）
- 渲染器 [pipeline/stages/d4_render.py](../pipeline/stages/d4_render.py)：Pillow 逐帧绘制条形竞速 + 大年份 + 玻璃卡，直接管道给 ffmpeg
- 知识沉淀：[code-video-pipeline](../knowledge/工作流/code-video-pipeline.md)

## 6. 待确认 / 后续

- [待确认] 是否引入 Playwright/HTML 渲染器以复用其 11 种风格与 Three.js 场景（需评估 Chromium 下载成本）
- [待确认] 数据动画是否要加合成 BGM（120 BPM 节拍层）
- [待确认] 是否把 2-pass 编码接进 `s6_export`（当前单遍 VBR）

## 来源

1. [Moessif/code-video-showcase](https://github.com/Moessif/code-video-showcase)（访问 2026-11-03）
2. 仓库 `README.md`、`SKILL.md`、`references/render-pipeline.md`、`references/style-recipes.md`（访问 2026-11-03）
3. 本地克隆：`/tmp/code-video-showcase`（2026-11-03）
