---
id: kb/whisperx
title: "WhisperX · 词级时间戳转写与说话人分离"
type: 工具
domain: [字幕, 素材管理, 自动化]
status: 可用
confidence: 中
license: "BSD-2-Clause"
repo: "https://github.com/m-bain/whisperX"
docs: "https://github.com/m-bain/whisperX#readme"
language: Python
platform: [macOS, Linux, Windows]
tags: [语音转写, ASR, 词级时间戳, 字幕, 说话人分离, 对齐]
related: [kb/subtitle-density, kb/transcode-delivery, kb/code-video-pipeline]
updated: 2026-11-03
owner: lead
---

# WhisperX · 词级时间戳转写与说话人分离

## 一句话定位

在 Whisper 基础上做词级时间戳对齐与可选说话人分离，产出可直接用于字幕校时、粗剪定位与访谈剪辑的转写结果；在流水线中服务 S3 素材整理 / S7 字幕。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 语音转文字（多语言，含中文） | 替代人工校对：错别字、专有名词仍需修 |
| 词级时间戳，便于字幕精确断句与卡点 | 自动理解语义、生成脚本（需上层 Agent） |
| 说话人分离（需 Hugging Face token） | 直接产出平台合规的最终字幕样式 |
| 批量转写与 SRT/VTT/JSON 输出 | 高质量音乐/强噪声场景的可靠转写 |

## 核心能力

- 基于 faster-whisper 的转写；支持 VAD 预切分，减少静音段计算。
- 词级时间戳 + 强制对齐（alignment），比原始 Whisper 的段级时间更准。
- 可选说话人分离（diarization），用于访谈/播客多说话人标注。
- 输出 SRT / VTT / JSON / TXT；可接字幕清洗与烧录流程。
- 可选 `[fast]` 依赖（Numba）加速对齐。

## 安装 / 获取

```bash
# PyPI 3.8.6 要求 Python >=3.10,<3.14；本机 3.9.6 不满足
python3.11 -m venv .venv-whisperx
source .venv-whisperx/bin/activate
pip install whisperx
# GPU 用户按官方说明装匹配的 PyTorch/CUDA；CPU 可跑但慢
```

前提：FFmpeg；首次运行会下载模型权重；说话人分离需要 `--hf_token` 并接受 pyannote 模型协议。

## 最小可用示例

```bash
# 转写为 SRT（以 whisperx --help 的实际参数为准）
whisperx input.wav --model small --language zh --output_format srt --output_dir out

# 词级 JSON（便于字幕断句/卡点）
whisperx input.wav --model small --language zh --output_format json --output_dir out

# 说话人分离（需 token）
whisperx meeting.wav --model small --diarize --hf_token "$HF_TOKEN" --output_format json
```

预期结果：`out/input.srt` 或 `out/input.json`（含 word 级时间戳）。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 词级时间戳，字幕校时省大量手工 | Python 门槛：PyPI 3.8.6 要求 >=3.10,<3.14，本机 3.9.6 不可用 |
| 内置 VAD 与对齐，长音频更稳 | 首次模型下载大；GPU 环境配置成本高 |
| BSD-2 许可，商用友好 | 中文标点/断句仍需清洗（与 kb/subtitle-density 配合） |
| 可输出 JSON 供程序化剪辑 | 说话人分离依赖 HF token 与额外模型协议 |

## 适用 / 不适用

- 适用：口播/访谈/播客/课程转写、字幕制作、按语句定位粗剪点。
- 不适用：需要逐帧精确到毫秒的卡点（仍需人工/音频分析）；无音轨视频。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：[口播知识](../../sop/short-oral-knowledge.md) 的 S7 字幕、[教程长视频](../../sop/long-tutorial.md) 的 S3/S7、[访谈/播客](../../sop/long-interview-podcast.md) 的转写。
- 下游技能：[subtitle-pipeline](../../skills/subtitle-pipeline/SKILL.md)（断句/校时/烧录）。
- 关联条目：`kb/subtitle-density`、`kb/transcode-delivery`。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | 信息核验 | PyPI JSON / GitHub API | 版本 3.8.6，requires-python >=3.10,<3.14，BSD-2-Clause，仓库 2026-10 活跃 |
| 2026-11-03 | 本机 Python 3.9.6 | 安装探测 | 未安装：不满足 Python 要求，需另建 3.10+ venv 后补实测 |

## 来源

1. [m-bain/whisperX](https://github.com/m-bain/whisperX)（BSD-2-Clause，访问 2026-11-03）
2. [WhisperX README](https://github.com/m-bain/whisperX#readme)（pip 安装、diarization、fast 依赖，访问 2026-11-03）
3. [PyPI whisperx 3.8.6](https://pypi.org/project/whisperx/)（requires-python >=3.10,<3.14，访问 2026-11-03）