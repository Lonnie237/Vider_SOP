---
id: sop/long-ppt-to-video
title: "PPT/文档转视频 · 逐页解说 SOP"
type: sop
video_type: "PPT转视频"
duration: "3–15min"
aspect: "16:9"
platforms: [B站, YouTube, 视频号, 客户交付]
difficulty: 低
tools: [PowerPoint / Keynote, LibreOffice, python-pptx, pymupdf, ffmpeg, TTS]
status: 可用
updated: 2026-11-04
owner: lead
---

# PPT/文档转视频 · 逐页解说 SOP

> 读者：需要把课件/汇报/产品介绍快速视频化的普通用户或执行 Agent。目标：一次制作即可交付，页面不错位、音画不同步、字幕不返工。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 已有 PPT/PDF/文档，想加旁白与字幕 | 需要保留 PPT 原生动画：直接录屏（[产品说明 SOP](long-product-explainer.md)） |
| 课程、培训、汇报、产品介绍 | 需要真人出镜：[口播 SOP](short-oral-knowledge.md) |
| 3–15 分钟、16:9 为主 | 纯数据动画：[数据动画 SOP](long-data-animation.md) |
| 希望批量、可复现 | 扫描件无文字层：先 OCR 或重做 PPT |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 | 1920×1080（16:9） | 竖屏 1080×1920（PPT 居中 + 上下留白） |
| 帧率 | 30 fps | 60 fps（录屏素材） |
| 视频 | H.264 High，VBR 1–2 Mbps（静态幻灯片） | 文字多/图表密可到 4 Mbps |
| 音频 | AAC 48 kHz 立体声 192 kbps，-16 LUFS | 短视频变体 -14 LUFS |
| 字幕 | 烧录（ASS/SRT）或外挂 | 平台自动字幕可用时外挂 |
| 封装/命名 | .mp4，`<项目>-ppt-v1-<date>.mp4` | 客户交付附 PDF + 讲稿 |
| 时长 | 3–15 min；页均 20–60s | 30–60s 摘要版 |

## 前置准备

- 源文件：PPT/PPTX/PDF/DOCX；有讲者备注就先导出备注，这是最好的旁白素材。
- 工具：LibreOffice（`soffice`，PPT→PDF）、pymupdf（PDF→PNG）、ffmpeg、TTS（edge-tts 或本机 say）。
- 环境：中文字体（Hiragino / Noto / 思源），磁盘 ≥ 2GB；Python 3.10+（若用 slide-stream）。
- 文案：逐页旁白，中文约 250 字/分钟；先按目标时长估算总字数（时长×4.2 字/秒）。
- 立项：填 [项目 Brief](../templates/项目Brief.md)，交付规格用 [交付规格模板](../templates/交付规格.md)。

## 流程总览（10 分钟成片，单人）

| 阶段 | 产出 | 时间预算 |
|---|---|---|
| S0 目标与时长 | Brief、页数/时长目标 | 0.3h |
| S1 逐页旁白 | 每页一段文本 | 1.5h |
| S2 归一 PDF | pdf/source.pdf | 0.2h |
| S3 PDF→页图 | pages/NN.png + 页尺寸 | 0.1h |
| S4 逐页 TTS | mp3/NN.mp3 + 句子边界 | 0.3h |
| S5 时长表 | durations.json（ffprobe 实测） | 0.1h |
| S6 分段渲染 | seg/NN.mp4（无字幕，并行） | 0.3h |
| S7 拼接 + 字幕 | master.mp4 → final.mp4 | 0.5h |
| S8 QC | QC 记录 + 抽帧 | 0.3h |
| 合计 | — | 约 3.6h |

## 分阶段操作

### S0 目标与时长

- 确定目标时长、平台、是否需要字幕/片头。
- 页数 × 页均 20–60s 校验总时长；超时就删页而不是加速旁白。

### S1 逐页旁白

- 每页一段，口语化；不要念 bullet（bullet 是给看的，旁白是给听的）。
- 中文 250 字/分钟；封面/过渡 45–70 字，重点页 75–100 字；数字用阿拉伯数字。
- 没有讲者备注时，按「这页想让观众记住什么」写，不要堆信息。

### S2 归一 PDF

```bash
soffice --headless --convert-to pdf --outdir pdf/ deck.pptx
```

- 已有 PDF 跳过；不要用 python-pptx 直接从形状出图（字体/换行会漂移）。
- 校验 PDF 页数 == 幻灯片页数。

### S3 PDF→页图

```bash
python3 - <<'PY'
import pymupdf
doc = pymupdf.open("pdf/source.pdf")
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=144).save("pages/%02d.png" % i)
print("pages", len(doc))
PY
```

- 144dpi 约 1920×1080；检查每页宽高比一致，不一致时统一 pad。

### S4 逐页 TTS + 句子边界

- 用 edge-tts 或本机 say 逐页合成；一遍同时导出句子边界（ASS/SRT 时间轴）。
- 后处理：响度归一（-16 LUFS）、去首尾静音、统一 48kHz 单声道。

### S5 时长表

- 用 ffprobe 读每页 mp3 真实时长，写入 durations.json；不要用句边界之和。

### S6 分段渲染

- 每页：静图 + 音频 → 无声 mp4；统一 1920×1080/30fps/yuv420p/libx264。
- 并行 `-j 4`；失败页单独重跑，不要整片重来。

### S7 拼接 + 字幕 + 导出

```bash
# 1) 无字幕拼接，零重编码
ffmpeg -y -f concat -safe 0 -i segments.txt -c copy master.mp4
# 2) 全片一次烧字幕（ASS 带样式）
ffmpeg -y -i master.mp4 -vf "ass=subs/final.ass" -c:v libx264 -crf 20 -preset medium \
  -c:a copy -movflags +faststart final.mp4
```

- 字幕时间轴必须对成片（页长来自 mp3 实测）；不要用源稿时间。
- 可加 3s 标题卡、末页定格 3s（concat 前后追加，copy 拼接）。

### S8 QC

- 页数、每页时长、全片帧数、音画同步、字幕、黑帧、响度、命名。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 页图 | dpi / 尺寸 | 144dpi 约 1920×1080 |
| 旁白 | 语速 | 250 字/分钟 |
| 页均时长 | 封面/重点 | 45–70 字 / 75–100 字 |
| 分段编码 | H.264 | crf 20–23，preset medium/veryfast |
| 拼接 | concat | `-c copy` |
| 字幕烧录 | ASS | 一次全片 |
| 响度 | 长视频 | -16 LUFS（±1） |
| 幻灯片码率 | VBR | 1–2 Mbps |

## 质量门禁（QC）

- [ ] 页数 = PPT 页数；无缺页/重页
- [ ] 每页时长 = 对应音频实测时长；全片无音画漂移
- [ ] 字幕在成片时间轴上，无重叠/超长行/错别字
- [ ] 抽帧：标题卡、中间页、末页、无黑帧
- [ ] 响度 -16 LUFS；无爆音
- [ ] 规格/命名/封装正确
- [ ] 敏感信息（客户名、内部数据）已脱敏

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 页面错位/文字压图 | 用 python-pptx 直接抽图 | 先 LibreOffice 转 PDF 再栅格化 |
| Python 装了包却 import 失败 | pymupdf 与 TTS 不在同一解释器 | 用 `which python` 统一，或 `python -m pip` |
| 音画不同步 | 页长用句边界之和 | 用 mp3 ffprobe 实测时长 |
| 字幕整体偏移 | 字幕对源稿时间 | 重算成片时间轴 |
| 成片很大/慢 | 逐页烧字幕 + xfade | 分段无字幕 + copy + 一次烧 |
| 中文变方框 | 字体缺失 | 安装 CJK 字体并在 ASS 指定字体名 |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| PPT→PDF→PNG | 命令行 | LibreOffice + pymupdf |
| 逐页 TTS/字幕 | Python | edge-tts / say |
| 分段渲染/拼接 | ffmpeg + 并发 | ffmpeg |
| 预检/时长校验 | 脚本 | ffprobe + Python |
| 质检 | 脚本 | 本仓 qc-deliver |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| 只有 PDF | 跳过 S2，直接 S3 |
| 只有图片 | 跳过 S2/S3，图片按页排序后直接 S4 |
| 加背景音乐 | BGM -18～-24dB，旁白处 ducking |
| 竖屏 9:16 | PPT 居中 + 上下品牌留白；字幕安全区上移 |
| 客户交付 | 附 PDF、讲稿、字幕文件、母版 |

## 复盘与改进

- 本机可行性（2026-11-04）：`soffice` 已装、python-pptx 可用；pymupdf 与 edge-tts 未装，需 `pip install pymupdf edge-tts` 后补实测（[待确认]）。
- 来源仓库 50 页实测：旧 128s/119.5MB → 新 90.6s/47.9MB；本机未复现。
- 回填：真实项目完成后记录页数、总时长、渲染耗时与返工点。

## 关联条目

- 方法：[PPT/文档转视频](../knowledge/工作流/ppt-to-video.md)
- 字幕：[字幕与信息密度](../knowledge/方法论/subtitle-density.md)
- 交付：[转码与交付](../knowledge/工作流/transcode-delivery.md)
- 工具：[ffmpeg](../knowledge/开源库/ffmpeg.md)、[whisperx](../knowledge/开源库/whisperx.md)

## 来源

1. [cernetman/agent-skills · ppt-to-explainer-video-ffmpeg](https://github.com/cernetman/agent-skills/tree/main/skills/ppt-to-explainer-video-ffmpeg)（MIT）
2. [michael-borck/slide-stream](https://github.com/michael-borck/slide-stream)（MIT）
3. 本仓：[来源台账](../research/来源台账.md)
