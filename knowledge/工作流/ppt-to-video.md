---
id: kb/ppt-to-video
title: PPT/文档转视频 · 逐页解说、一次烧字幕
type: 工作流
domain: [脚本, 剪辑, 字幕, 交付]
status: 可用
confidence: 高
tags: [PPT转视频, 幻灯片, 旁白, TTS, 字幕, ffmpeg, LibreOffice]
related: [kb/whisperx, kb/subtitle-density, kb/transcode-delivery, kb/code-video-pipeline]
updated: 2026-11-04
owner: lead
---

# PPT/文档转视频 · 逐页解说、一次烧字幕

## 一句话定位

把 PPT/PDF/文档变成「逐页画面 + 旁白 + 字幕」的讲解视频：先归一成 PDF 再出图，每页旁白按真实音频时长定页长，分段并行渲染、`concat -c copy` 拼接、全片只烧一次字幕。

## 适用场景

- 课程课件、公司培训、产品介绍、汇报材料的视频化。
- 已有 PPT/PDF，想要低成本、可批量、可复现的讲解视频。
- 不适用：需保留 PPT 原生动画、扫描件无文字层、必须完全离线（edge-tts 需网络）的场景。

## 可操作步骤（8 步）

1. 预检：确认 ffmpeg/ffprobe、中文字体、Python 解释器（pymupdf 与 TTS 必须同一解释器）、磁盘空间。
2. 归一成 PDF：`soffice --headless --convert-to pdf`（PPT/Word/Excel→PDF）；已有 PDF 直接跳过。不要用 python-pptx 直接从形状对象出图——字体替换/换行/行高会漂移。
3. PDF→页图：pymupdf（新 API `import pymupdf`，旧版 `import fitz`）按 144dpi 出图约 1920×1080；检查每页宽高比是否一致。ffmpeg 通常不带 PDF 解码器，不要用它转。
4. 写逐页旁白：口语化、TTS 友好，阿拉伯数字保留；中文约 250 字/分钟（约 4.2 字/秒）；封面/过渡页 45–70 字，重点页 75–100 字。可用讲者备注、LLM 起草或自写稿。
5. 逐页 TTS + 句边界：一遍生成 mp3 同时收集句子边界，字幕与音频天然同步；不要二次转写。
6. 时长表：用 ffprobe 读每页 mp3 的真实时长（不是句边界之和，尾部静音也算）；写入 durations。
7. 并行渲染分段：每页「静图 + 音频」渲染成无声 mp4（不烧字幕），`-j 4` 并行；参数统一（分辨率/帧率/像素格式/编码），便于 copy 拼接。
8. 拼接 + 一次烧字幕 + 校验：`concat -c copy` 得 master；用一份全片 ASS/SRT 单次烧录（唯一一次全片重编码）；可加 3s 标题卡与末页定格；最后校验页数、帧数、音画时长、字幕时间轴、黑帧。

## 参数与阈值

| 参数 | 推荐值 | 依据 |
|---|---|---|
| 旁白速度 | 250 字/分钟（约 4.2 字/秒） | cernetman skill 口径 |
| 逐页字数 | 封面/过渡 45–70；重点 75–100 | 同上 |
| 页图分辨率 | 144dpi 约 1920×1080 | 同上 |
| 分段并行 | `-j 4` | 50 页实测 58.8s→41.7s（−29%） |
| 拼接 | `-f concat -c copy` | 零重编码 |
| 字幕 | 全片一次烧录 | 避免逐段重编码代际损失 |
| 幻灯片码率 | 700–1200kbps（静态文字/图表） | 50 页实测 778kbps 文字仍清晰 |
| 响度 | 长视频 -16 LUFS / 短视频 -14 | 本仓交付规范 |
| 标题卡/末页 | 3s 标题卡；末页定格 3s | 来源实践 |

## 50 页实测基准（来源仓库 Windows 环境）

| 指标 | 旧方案（逐段烧字幕 + N 级 xfade） | 新方案（分段无字幕 + copy + 一次烧录） |
|---|---|---|
| 总耗时 | 128s | 90.6s（medium）/ 77.9s（veryfast） |
| 成片大小 | 119.5MB | 47.9MB |
| 码率 | 2059kbps | 778kbps |
| 质量 | 多代重编码 | 仅一次全片重编码 |

> 基准来自 [cernetman/agent-skills](https://github.com/cernetman/agent-skills)（MIT），未在本机复现；引用时保留测试条件。

## 工具选型

| 工具 | 定位 | 许可 | 备注 |
|---|---|---|---|
| [cernetman/agent-skills · ppt-to-explainer-video-ffmpeg](https://github.com/cernetman/agent-skills/tree/main/skills/ppt-to-explainer-video-ffmpeg) | 本地 ffmpeg 全链路 | MIT | LibreOffice + pymupdf + edge-tts |
| [slide-stream](https://github.com/michael-borck/slide-stream) | 端到端（Markdown/PPT→视频/pptx） | MIT | Python 3.10+；离线音色；doctor 预检 |
| [py-ppt2movie](https://github.com/icaoberg/py-ppt2movie) | PPT→MP4 + 每页旁白 | 见仓库 | 轻量参考 |
| [presentation-generator](https://github.com/ncukondo/presentation-generator) | PptxGenJS + TTS + ffmpeg | 见仓库 | 生成+合成模板 |
| Slidev / motion.md | Markdown 演示→视频 | MIT/见仓库 | 轻量路线 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 用 python-pptx 直接抽图 | 字体/换行/行高漂移，页面错位 | 先转 PDF 再栅格化 |
| 用 ffmpeg 解 PDF | ffmpeg 通常无 PDF 解码器 | pymupdf 或 poppler |
| 逐页烧字幕再 xfade | 多代重编码，慢且糊 | 分段无字幕 → copy → 一次烧 |
| 用句边界之和当页长 | 尾部静音没算，音画错位 | 用 mp3 实测时长 |
| 字幕时间轴用源稿时间 | 成片时间轴已变 | 字幕必须对成片时间轴 |
| 逐页重启进程/重复加载模型 | 慢 | 批量并行、复用进程 |

## 验证方式

- 页数 = 幻灯片页数；每段时长 = 对应 mp3 实测时长。
- 全片帧数 = `round(duration×30)`；无音画漂移。
- 字幕在成片时间轴上，无重叠/超长行/错别字。
- 抽帧检查：标题卡、中间页、末页定格、无黑帧。

## 关联条目

- 字幕：[字幕与信息密度](../方法论/subtitle-density.md)
- 转写：[WhisperX](../开源库/whisperx.md)
- 交付：[转码与交付](transcode-delivery.md)
- SOP：[PPT/文档转视频 SOP](../../sop/long-ppt-to-video.md)

## 来源

1. [cernetman/agent-skills · ppt-to-explainer-video-ffmpeg](https://github.com/cernetman/agent-skills/tree/main/skills/ppt-to-explainer-video-ffmpeg)（MIT，访问 2026-11-04）：PDF 归一、8 步管线、50 页基准。
2. [michael-borck/slide-stream](https://github.com/michael-borck/slide-stream)（MIT，访问 2026-11-04）：逐页旁白、离线音色、doctor 预检。
3. [py-ppt2movie](https://github.com/icaoberg/py-ppt2movie)、[presentation-generator](https://github.com/ncukondo/presentation-generator)（访问 2026-11-04）。
4. 本仓来源台账：[research/来源台账.md](../../research/来源台账.md)。
