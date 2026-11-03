---
id: kb/ffmpeg
title: "FFmpeg · 音视频处理的命令行瑞士军刀"
type: 工具
domain: [素材管理, 粗剪, 精剪, 声音, 字幕, 调色, 动效, 交付]
status: 已验证
confidence: 高
license: "LGPL-2.1-or-later（核心）/ GPL-2.0-or-later（启用 --enable-gpl 的构建整体适用 GPL）"
repo: "https://git.ffmpeg.org/ffmpeg.git"
docs: "https://ffmpeg.org/documentation.html"
language: C
platform: [macOS, Linux, Windows]
tags: [ffmpeg, 转码, 命令行, 滤镜, 自动化, 交付]
related: [kb/environment-local, kb/moviepy, kb/pyav, kb/capability-matrix, kb/selection-guide]
updated: 2026-11-03
owner: lib-scout
---

# FFmpeg · 音视频处理的命令行瑞士军刀

## 一句话定位

给自动化流水线提供「一条命令完成解码 → 滤镜 → 编码 → 封装」的底层引擎；它贯穿 S3 素材管理到 S10 导出交付的每个环节，是脚本化剪辑的默认底座。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 批量转码、代理（proxy）生成、抽帧、封装转换 | 交互式多轨时间线编辑与实时预览 |
| 用 filter graph 做裁剪、拼接、叠加、调色、响度标准化 | 关键帧动画的图形界面编排与预览 |
| 无头环境跑脚本（CI / 服务器 / 批量任务） | 复杂转场、合成节点的可视化调试 |
| 帧级截取、切片、拼接，以及 ffprobe 读参数做 QC | 跨工具的时间线工程交换（需 OTIO / XML） |

## 核心能力

- 编解码与封装：libx264 / libx265 / libsvtav1 / libvpx / prores；mov / mp4 / mkv / webm。
- 滤镜图（`-vf` / `-af` / `-filter_complex`）：scale、crop、concat、xfade、overlay、zoompan、eq、loudnorm 等。
- 硬件加速：videotoolbox（macOS）、nvenc（NVIDIA）、qsv（Intel）、vaapi（Linux），按机器可用性选择。
- 帧精确操作：`-ss` 放输入侧是快速定位，放输出侧是精确裁剪；`-t` / `-frames:v` 控制取量。
- 媒体分析与质检：ffprobe 读流参数、时长、码率；blackdetect / silencedetect 做自动 QC。
- 可脚本化：稳定的退出码、`-progress` 进度输出、`-nostdin` 适配批处理。

## 安装 / 获取

macOS（Homebrew）：

```bash
brew install ffmpeg            # 本机为 Homebrew 7.0.7 / ffmpeg 9.0.2
ffmpeg -version | head -1
```

Ubuntu / Debian：

```bash
sudo apt update && sudo apt install -y ffmpeg
```

Windows（winget）：

```powershell
winget install --id Gyan.FFmpeg
```

前提：也可用官方静态构建或源码编译（[下载页](https://ffmpeg.org/download.html)、[编译指南](https://trac.ffmpeg.org/wiki/CompilationGuide)）。不同发行版的构建**可选组件不同**，装完必须探测滤镜与编码器（见「优缺点与坑位」第 1 条）。

## 最小可用示例

```bash
# 1) 转码交付：H.264 / AAC / mp4，faststart 便于网页秒开
ffmpeg -i input.mp4 -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart out.mp4

# 2) 裁剪 + 缩放：从第 5 秒取 10 秒，宽度缩到 640
ffmpeg -ss 00:00:05 -i input.mp4 -t 10 -vf "scale=640:-2" \
  -c:v libx264 -crf 23 -c:a aac out_cut.mp4

# 3) 响度标准化：短视频常用 -14 LUFS，视频流直接复制不重编码
ffmpeg -i input.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k out_loud.mp4
```

预期结果：三条命令退出码均为 0；`ffprobe -v error -show_entries format=duration -of default=nw=1 out.mp4` 能读出预期时长。本机实测见下表。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 能力覆盖全流程，几乎每个环节都能用 | 选项多且位置敏感，参数写错不报错只出错结果 |
| 无头可跑，天然适合批量与 CI | 发行版构建的可选组件不一致，换机即失效 |
| 生态最大：几乎所有视频库都以它为后端 | 许可证分 LGPL / GPL 两档，分发前必须确认构建配置 |

1. **字幕 / 文字滤镜不可用**。现象：`Unknown filter 'subtitles'`，`-vf drawtext` 同样失败。原因：本机 Homebrew 9.0.2 构建配置里没有 `--enable-libass` / `--enable-libfreetype`，不是命令写错。规避：执行前先探测 `ffmpeg -hide_banner -h filter=subtitles`；缺失时改用 Pillow 渲染 PNG 字幕层再 `overlay`，或换装带 libass 的构建。详见 [本机环境基线](../环境/environment-local.md)。
2. **GPL 传染性**。现象：内部用没问题，一旦对外分发或把转码做成闭源服务，就会卡在许可证审核。原因：本机构建启用 `--enable-gpl` 且链接 libx264 / libx265，按官方说明此时整体适用 GPL-2.0-or-later；核心库默认才是 LGPL-2.1-or-later。规避：闭源分发用 LGPL 配置（`--disable-gpl --disable-nonfree` + 动态链接）自行编译，并保留对应源码与编译说明。
3. **`-ss` 位置不同，切点不同**。现象：同一个 `-ss 5` 放在 `-i` 前后，输出起点差几帧。原因：输入侧 seek 依赖关键帧索引，快但可能偏移；输出侧先解码再裁，帧精确但慢。规避：粗剪用输入侧，交付级精确裁剪把 `-ss` 放到 `-i` 之后。
4. **输出选项写到输入前面**。现象：`-c:v libx264` 写在 `-i` 之前时编码器设置不生效或直接报错。原因：FFmpeg 的参数按位置绑定到其后的输入 / 输出。规避：所有输出选项统一放在最后一个 `-i` 之后、输出文件名之前。

## 适用 / 不适用

- 适用：批量转码、代理与抽帧、拼接与剪切、响度标准化、LUT 调色、交付编码、自动化 QC，以及 CI / 服务器无头环境。
- 不适用：交互式多轨剪辑与实时预览（改用 DaVinci Resolve / Premiere / Final Cut）；跨工具时间线交换（改用 `kb/opentimelineio`）；声明式程序化合成（改用 `kb/remotion`）；节点式合成与三维（改用 Blender VSE / Natron）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：各 SOP 的 S3 素材转码 / 代理生成与 S10 导出参数都以本文命令为基线；涉及字幕烧录的 S7 必须先按坑位 1 探测。
- 关联条目：[本机环境基线](../环境/environment-local.md)（构建配置与性能）、`kb/moviepy` / `kb/pyav`（以 FFmpeg 为后端的 Python 封装）、`kb/capability-matrix`（横向对比）、`kb/selection-guide`（何时选它）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / Apple M5 / ffmpeg 9.0.2（Homebrew，GPL 构建） | `ffmpeg -f lavfi -i testsrc2=size=1280x720:rate=30:duration=3 ... demo.mp4` | 3s 720p30 H.264+AAC 用时 0.12s，产物 1.0 MB |
| 2026-11-03 | 同上 | `ffmpeg -ss 1 -i demo.mp4 -t 1 -vf scale=640:-2 ...` | 用时 0.07s，输出 640×360 / 1.000s |
| 2026-11-03 | 同上 | `ffmpeg -i demo.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy ...` | 用时 0.08s，时长保持 3.000s |
| 2026-11-03 | 同上 | `ffmpeg -hide_banner -h filter=subtitles` | `Unknown filter 'subtitles'`（构建无 libass） |

## 来源

1. [FFmpeg 官网](https://ffmpeg.org/)（访问 2026-11-03）
2. [FFmpeg License and Legal Considerations](https://ffmpeg.org/legal.html)（访问 2026-11-03）：核心 LGPL-2.1-or-later，启用 GPL 组件后整体适用 GPL-2.0-or-later
3. [FFmpeg Download](https://ffmpeg.org/download.html)（访问 2026-11-03）
4. [FFmpeg releases 目录](https://ffmpeg.org/releases/)（访问 2026-11-03）：`ffmpeg-9.0.2.tar.xz` 时间戳 2026-09-19
5. [FFmpeg GitHub 镜像](https://github.com/FFmpeg/FFmpeg)（访问 2026-11-03）
6. 本机实测：`ffmpeg -version`、`ffmpeg -encoders`、`ffmpeg -h filter=...` 与上表命令（2026-11-03）
