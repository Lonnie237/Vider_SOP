---
id: kb/transcode-delivery
title: 转码与交付 · 母版、平台版与 QC 一条线
type: 工作流
domain: [转码, 交付, QC]
status: 可用
confidence: 高
tags: [转码, 交付, H.264, ProRes, faststart, loudnorm, QC]
related: [kb/platform-specs, kb/asset-management, kb/automation-pipeline, kb/sound-design, kb/color-grading, kb/subtitle-density, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 转码与交付 · 母版、平台版与 QC 一条线

> 交付分三层：母版（留档 / 二次编辑）、交付版（高画质可播）、平台版（按平台限制）。三层都用 FFmpeg 从同一工程导出，避免「先在 NLE 里压一遍、再转一遍」的二次损失。

## 一句话定位

把工程输出转成平台可播、画质损失最小、参数可核对的交付文件。用在 S10 导出交付；判断标准是 ffprobe 参数与交付规格一致、faststart 生效、响度命中目标、上传后平台未强制二次压缩。

## 适用场景

- 适用：短视频 / 长视频平台发布、客户交付、归档母版、批量转码。
- 不适用：需要平台端剪辑的二创素材（先给高质量中间文件）；纯音频交付（走音频条目）。

## 流程设计

输入 → 分层输出：

| 层级 | 输入 | 处理 | 输出 | 用途 |
|---|---|---|---|---|
| 母版 | 工程导出 / 高码中间文件 | ProRes 422 HQ 或高码 H.264 | `06_exports/master/` | 归档、二次编辑 |
| 交付版 | 母版 | H.264 crf 18–20 + 响度归一 | `06_exports/platform/` | 客户 / 内部审阅 |
| 平台版 | 交付版 | 按平台码率 / 时长 / 体积再导出 | 平台上传文件 | 抖音 / 视频号 / B站 / YouTube |

处理链：核对规格 → 选层级 → 视频编码 → 音频响度 → 封装 faststart → ffprobe QC → 上传前检查。

## 可操作步骤

1. 核对输入：`ffprobe` 看母版的分辨率、帧率、色彩、音频采样率；与 [交付规格](../../templates/交付规格.md) 对齐。产出：输入参数记录。
2. 选层级与规格：母版走 ProRes，平台版走 H.264（参数见矩阵）。产出：导出参数表。
3. 视频编码：H.264 High / level 4.1 / yuv420p / crf 18–20；竖屏先做安全裁切。产出：无声视频或整片。
4. 音频：两遍 loudnorm（短视频 -14 LUFS / 长视频 -16 LUFS，TP ≤ -1.5 dBTP）；再编 AAC 192–256k。产出：达标音轨。
5. 封装：`-movflags +faststart`，MP4 容器；确认 moov 在 mdat 前。产出：可秒开的 MP4。
6. QC：ffprobe 全参数 + 抽帧 + 响度复核；填 [QC 清单](../../templates/QC清单.md)。产出：QC 报告。
7. 上传前检查：平台体积 / 时长限制、封面、标题、字幕文件；上传后用手机看一遍。产出：发布就绪。

H.264 横屏交付（[实测] 2026-11-03：1080p30 编码成功；faststart 后 moov@36 位于 mdat@1543 之前）：

```bash
ffmpeg -y -hide_banner -i master.mov -c:v libx264 -preset slow -crf 19 -profile:v high -level 4.1 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -shortest out_1080p.mp4
```

竖屏适配（16:9 → 9:16 中心裁切；[实测] 2026-11-03 输出 1080×1920）：

```bash
ffmpeg -y -hide_banner -i master.mov -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -crf 19 -profile:v high -level 4.1 -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -shortest out_9x16.mp4
```

ProRes 母版（[实测] 2026-11-03：ProRes 422 HQ 2s 1080p 约 19MB；Proxy 约 5MB）：

```bash
ffmpeg -y -hide_banner -i master.mov -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s24le -ar 48000 out_master.mov
```

两遍响度归一（短视频 `I=-14`；长视频改成 `-16`；详细混音见 [声音设计](../方法论/sound-design.md)）：

```bash
ffmpeg -hide_banner -i out_1080p.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json -f null - 2> loud.json
MEASURED=$(python3 parse_loud.py loud.json)
ffmpeg -y -hide_banner -i out_1080p.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=7:$MEASURED:linear=true:print_format=summary" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 out_final.mp4
```

faststart 校验（[实测] 2026-11-03：带 faststart 的 moov 在文件头，不带则接近文件尾）：

```bash
python3 -c "d=open('out_final.mp4','rb').read(); print('moov', d.find(b'moov'), 'mdat', d.find(b'mdat'))"
```

QC 命令（ffprobe 一次读全规格）：

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,profile,width,height,r_frame_rate,pix_fmt,color_space,color_primaries,color_transfer,color_range,sample_rate,channels -of json out_final.mp4
```

## 交付规格矩阵

| 场景 | 编码 | 分辨率 | 帧率 | 关键参数 | 音频 |
|---|---|---|---|---|---|
| 母版归档 | ProRes 422 HQ | 同工程 | 同工程 | `-profile:v 3 -pix_fmt yuv422p10le` | PCM 24bit/48k |
| 横屏平台版 | H.264 High | 1920×1080 | 25/30/60 | crf 19–20，level 4.1，GOP 2s | AAC 192k 48k 立体声 |
| 竖屏平台版 | H.264 High | 1080×1920 | 30/60 | crf 19–20，中心裁切 | AAC 192k 48k 立体声 |
| 4K 平台版 | H.264 High | 3840×2160 | 30/60 | crf 18–20，level 5.1 | AAC 256k 48k |
| 客户审阅 | H.264 | 1920×1080 | 30 | crf 22–23，文件名带日期 | AAC 128k |
| 批量混剪 | H.264 | 按平台 | 按平台 | 见 [平台规格](platform-specs.md) | AAC 192k |

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| H.264 质量 | 母版级 crf 18–19；平台版 crf 20–23 | [推断] 画质 / 体积平衡 | 有平台码率上限时用 `-maxrate` |
| preset | slow（交付）/ medium（批量） | [推断] | 本机 1080p 10s slow 约 1.4s（medium） |
| Profile / Level | High / 4.1（1080p30）；5.1（4K） | H.264 规范 | 兼容性优先 |
| 像素格式 | yuv420p | 平台兼容 | 10-bit 只留母版 |
| GOP | 2s（30fps → 60 帧，60fps → 120 帧） | [推断] | 平台随机访问友好 |
| 音频 | AAC-LC 192–256k，48kHz，立体声 | [推断] | 统一 48k |
| 响度 | 短视频 -14 LUFS；长视频 -16 LUFS；TP ≤ -1.5 dBTP | 本仓规范 | 见 [声音设计](../方法论/sound-design.md) |
| 封装 | MP4 + `+faststart` | [实测] moov 前置 | 边下边播 |
| 色彩标签 | bt709 / tv / yuv420p | Rec.709 交付 | 见 [调色基础](../方法论/color-grading.md) |
| 文件命名 | `项目_画幅_平台_v1_日期.mp4` | 本仓规范 | 不用 `final` |
| 码率参考（1080p30） | 8–16 Mbps | [推断] | 平台版别低于 6 Mbps |
| 上传前体积 | ≤ 平台限制的 80% | [推断] | 留二次处理余量 |

## 失败处理

| 失败 | 症状 | 处理 |
|---|---|---|
| 平台二次压缩明显 | 上传后细节变糊、出现块 | 提高码率 / 分辨率；避免低码率 + 高运动 |
| 音画不同步 | 口型差半拍 | 统一帧率（VFR→CFR）、检查 `-shortest`、音频起始偏移 |
| 旋转元数据丢失 | 手机竖拍变横屏 | 编码前用 `-vf` 应用旋转，不依赖 display matrix |
| 文件过大 | 超过平台体积上限 | 降码率 / 降分辨率 / 缩短时长；先看平台矩阵 |
| 色彩标签缺失 | 播放器偏色 / 发灰 | 加 `-x264-params` 写全色彩标签并用 ffprobe 复核 |
| 响度不达标 | 平台后忽大忽小 | 两遍 loudnorm + ebur128 复核，不要只拉总音量 |
| faststart 未生效 | 网页播放要等整段下载 | 加 `-movflags +faststart` 重新封装 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 从 NLE 直接导出低码率再上传 | 二次编码损失叠加 | 从母版一次导出平台版 |
| crf 28 当交付 | 暗部与运动糊 | 交付用 crf 18–20 |
| 音频 44.1kHz / 单声道 | 平台转码异常、声场变窄 | 统一 48kHz 立体声 |
| 不加 faststart | 网页首帧慢 | MP4 加 `+faststart` |
| 竖屏直接拉伸 16:9 | 人脸变形 | 中心裁切 + 安全区检查 |
| 多次转码 | 每转一次掉一次画质 | 母版只转一次，平台版从母版出 |
| 只测本地播放 | 上传后才发现规格不符 | 按平台矩阵 + 上传后真机复核 |

## 验证方式

- 规格：`ffprobe` JSON 与交付规格逐项比对；分辨率 / 帧率 / 编码 / 音频采样率 / 声道 / 时长。
- faststart：`python3 -c "d=open('out.mp4','rb').read(); print(d.find(b'moov') < d.find(b'mdat'))"` 输出 `True`（[实测]：带 faststart 为 moov@36 < mdat@1543；不带为 mdat@44 < moov@1904108）。
- 响度：`ffmpeg -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -20`，I 命中 -14 / -16 ±1，TP ≤ -1.5 dBTP。
- 画面：抽首帧、中段、尾帧各 1 张；看黑帧、花屏、字幕安全区。
- 上传后：用另一台手机播放，确认 1080p 可播、无强制压缩痕迹。
- 失败信号：平台显示「转码中」很久 / 播放糊；文件头 moov 在尾部；响度差 > 2 LU。

## 关联条目

- 工作流：[平台规格与发布](platform-specs.md)、[素材管理与代理剪辑](asset-management.md)、[自动化流水线](automation-pipeline.md)
- 方法论：[声音设计](../方法论/sound-design.md)、[调色基础](../方法论/color-grading.md)、[字幕与信息密度](../方法论/subtitle-density.md)
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-oral-knowledge`、`sop/long-tutorial`、`sop/long-promo`

## 来源

1. [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）：libx264、prores_ks、AAC、movflags。
2. [FFmpeg loudnorm 文档](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)（访问 2026-11-03）：两遍归一化参数。
3. 本机实测（2026-11-03，ffmpeg 9.0.2）：faststart moov/mdat 位置对比；ProRes 422 HQ 2s 1080p 19MB；16:9 中心裁切输出 1080×1920；两遍 loudnorm 输出 -14.0 LUFS；加 `-x264-params` 后 ffprobe 读到完整色彩标签。
4. 本仓模板：[交付规格](../../templates/交付规格.md)、[QC 清单](../../templates/QC清单.md)（2026-11-03）。
5. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）。
