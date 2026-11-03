---
id: kb/sound-design
title: 声音设计与混音 · 对白优先，响度统一
type: 方法论
domain: [声音, 混音, 交付]
status: 可用
confidence: 中
tags: [声音, 混音, 响度, LUFS, loudnorm, 对白, BGM]
related: [kb/transcode-delivery, kb/platform-specs, kb/subtitle-density, kb/pacing-beat, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 声音设计与混音 · 对白优先，响度统一

> 本仓统一响度目标：短视频 **-14 LUFS**、长视频 **-16 LUFS**，真峰值（true peak）**≤ -1.5 dBTP**。测量与归一化都用 ffmpeg 的 `loudnorm` / `ebur128`，本机已实测可用。

## 一句话定位

让观众在手机外放、耳机、车载三种场景都能听清对白，同时不被平台二次压限破坏动态。用在 S6 声音与 S10 交付；判断标准是整片积分响度命中目标 ±1 LU、真峰值不超限、对白不被 BGM 盖住。

## 适用场景

- 适用：口播知识、教程、访谈、Vlog、宣传片；所有需要人声可懂度的成片。
- 不适用：纯音乐 / 环境声作品（以艺术动态为先，不套 -14 LUFS）；现场演出多轨混音（走专业 DAW 流程）。

## 原理与判断标准

- 响度不是一个峰值数字。积分响度（integrated loudness，LUFS）描述整段平均能量，真峰值（true peak，dBTP）防削波，响度范围（LRA，LU）描述忽大忽小的程度。
- 平台会对上传音频做响度归一化，但归一化目标未公开 [推断]；先做统一响度能减少「平台二次处理」带来的动态损失。
- 什么算好：短视频 -14 LUFS ±1，长视频 -16 LUFS ±1；TP ≤ -1.5 dBTP；LRA 短视频 5–7 LU、长视频 7–12 LU；对白清晰、BGM 退后、音效不刺耳。
- 什么算坏：只看峰值不看 LUFS；BGM 盖住人声；整片压到 -8 LUFS 像广告；前段 -20、后段 -10 忽大忽小；`alimiter limit` 填 -1 直接报错。

## 可操作步骤

1. 分轨：对白、音乐、音效至少三条轨；对白单独导出 48kHz / 24bit WAV。产出：`voice.wav`、`music.wav`、`sfx.wav`。
2. 对白清理：`highpass=f=80` 去低频轰鸣；`afftdn=nf=-25` 轻降噪（过强会「水下感」）。产出：干净对白。
3. 对白动态：`acompressor=threshold=-18dB:ratio=3:attack=5:release=150`，再用 `alimiter=limit=0.841`（-1.5 dBFS 的线性值）兜底。产出：稳定对白。
4. 音乐让位：对白出现时把 BGM 压低 6–9 dB，可用 `sidechaincompress` 自动闪避。产出：混音底轨。
5. 两遍响度归一化：第一遍测量 → 第二遍用测量值做线性归一化（保动态）。产出：`normalized.mp4`。
6. 校验：`ebur128` 看最终积分响度、真峰值、LRA；不合格回到第 3 步调动态，不要只拉总音量。

第一遍测量（结果 JSON 写在 stderr，重定向到文件）：

```bash
ffmpeg -hide_banner -i input.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json -f null - 2> loud.json
```

```python
import json, sys
s = open(sys.argv[1]).read()
d = json.loads(s[s.index('{'):s.rindex('}')+1])
print("measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s" % (
    d['input_i'], d['input_tp'], d['input_lra'], d['input_thresh'], d['target_offset']))
```

第二遍归一化（短视频 `I=-14`；长视频改成 `I=-16`）：

```bash
MEASURED=$(python3 parse_loud.py loud.json)
ffmpeg -y -hide_banner -i input.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=7:$MEASURED:linear=true:print_format=summary" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 output.mp4
```

对白链与 BGM 闪避（[实测] 2026-11-03：两条链均可执行，输出 AAC 48kHz）：

```bash
ffmpeg -y -hide_banner -i voice.wav -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=5:release=150,alimiter=limit=0.841" -c:a pcm_s24le voice_clean.wav
ffmpeg -y -hide_banner -i voice_clean.wav -i music.wav -filter_complex "[0:a]highpass=f=80[voice];[1:a][voice]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0[a]" -map "[a]" -c:a pcm_s24le mix.wav
```

校验：

```bash
ffmpeg -hide_banner -i output.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -20
```

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| 短视频积分响度 | -14 LUFS ±1 | 本仓规范 [推断] | 平台归一化目标未公开 |
| 长视频积分响度 | -16 LUFS ±1 | 本仓规范 [推断] | 访谈 / 教程 / 播客 |
| 真峰值 TP | ≤ -1.5 dBTP | [推断] 给二次编码留余量 | 有损编码后峰值会回升 |
| 响度范围 LRA | 短 5–7 LU；长 7–12 LU | [推断] | 过小压平，过大忽大忽小 |
| 对白平均响度 | -18 至 -15 LUFS | [推断] | 音乐比对白低 10–15 dB |
| BGM 底噪 | 对白段比对白低 12–18 dB | [推断] | 闪避 6–9 dB |
| 音效峰值 | ≤ -6 dBFS | [推断] | 转场 / 强调音不刺耳 |
| 高通 | 80 Hz（男声）；100 Hz（女声） | [推断] | 去隆隆声 |
| 采样率 / 位深 | 48 kHz / 24bit 中间；交付 48kHz AAC 192–256k | [推断] | 视频交付统一 48k |
| 声道 | 立体声（对话居中） | [推断] | 平台默认立体声 |
| 淡入淡出 | 0.1–0.3s | [推断] | 防爆音 |
| 限幅器 | `alimiter limit=0.841`（线性） | [实测] 范围 0.0625–1 | 填 -1 会报 "Result too large" |
| loudnorm LRA 目标 | 7 | 本仓规范 | 短视频与长视频一致 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 只看峰值，不测 LUFS | 峰值正常但整片偏小或被压扁 | 用 `loudnorm` 测积分响度，按 -14 / -16 归一 |
| BGM 盖住对白 | 人声不可懂，完播下降 | 对白段 BGM 降 12–18 dB，或 sidechain 闪避 |
| 全片拉到 -8 LUFS | 平台二次压限，动态全失 | 目标 -14 / -16，靠动态与层次做「响」 |
| 单遍 loudnorm 动态模式 | 动态被压平，呼吸感消失 | 两遍法 + `linear=true` 保动态 |
| `alimiter limit=-1` | 参数按线性值解析，直接报错 | 写 `0.841`（= -1.5 dBFS） |
| 交付 44.1kHz 或单声道 | 与视频流不统一，部分平台转码异常 | 统一 48kHz 立体声 |
| 前段 -20、后段 -10 | 观众反复调音量 | 控制 LRA 在目标区间，段落间做 1–2 dB 过渡 |

## 验证方式

- 响度：`ffmpeg -i output.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -20`，看最终 `I:`（应为 -14 / -16 ±1）、`TPK:`（≤ -1.5 dBTP）、`LRA:`。
- 两遍法有效性（[实测] 2026-11-03，ffmpeg 9.0.2）：8s 合成音源测得 `input_i=-27.85`、`input_tp=-23.17`，两遍归一化后积分响度 -14.0 LUFS、TPK -9.4 dBFS（源本身峰值低，TP 目标未触顶）。
- 规格：`ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of json output.mp4`，确认 AAC / 48000 / 2。
- 主观：手机外放、耳机、车载各听一遍；听不清对白就算失败。
- 失败信号：平台上传后明显变小 / 变闷；评论区说「听不清」；副歌处人声被埋。

## 关联条目

- 方法论：[字幕与信息密度](subtitle-density.md)、[节奏与卡点](pacing-beat.md)、[钩子与留存](hooks-retention.md)
- 工作流：`kb/transcode-delivery`、`kb/platform-specs`（下一轮产出）
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-oral-knowledge`、`sop/long-interview-podcast`、`sop/long-tutorial`

## 来源

1. [FFmpeg loudnorm 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)（访问 2026-11-03）：I / TP / LRA / measured_* / linear 参数定义。
2. [FFmpeg ebur128 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#ebur128)（访问 2026-11-03）：积分响度、LRA、真峰值输出。
3. [EBU R128 响度标准](https://tech.ebu.ch/publications/r128)（访问 2026-11-03）：LUFS / LRA / true peak 的定义来源。
4. 本机实测（2026-11-03，macOS Apple Silicon，ffmpeg 9.0.2）：两遍 loudnorm 将合成音源从 -27.85 LUFS 归一到 -14.0 LUFS，TPK -9.4 dBFS；`alimiter` 的 `limit` 范围为 0.0625–1（填 -1 报错）；sidechaincompress 闪避链输出 48kHz AAC 成功。
5. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）。
