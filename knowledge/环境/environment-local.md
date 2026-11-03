---
id: kb/environment-local
title: 本机环境 · macOS Apple Silicon 工具链基线
type: 环境
domain: [转码, 剪辑, 自动化, 交付]
status: 已验证
confidence: 高
tags: [环境, ffmpeg, python, node, 性能, videotoolbox]
related: [kb/ffmpeg, kb/automation-pipeline, kb/transcode-delivery]
updated: 2026-11-03
owner: lead
---

# 本机环境 · macOS Apple Silicon 工具链基线

> 本文所有数据为 **2026-11-03 本机实测**，用于判断「某条 SOP / 命令在这台机器上能不能跑、跑多快」。换机或升级后必须重测并更新日期。

## 一句话定位

记录当前开发机的硬件、已装工具、FFmpeg 能力边界与性能基线；是自动化脚本与 SOP 可行性判断的前提。

## 适用场景

- 写 FFmpeg / Python 自动化脚本前，确认编解码器与滤镜是否存在。
- 评估一条 SOP 的时间预算是否现实。
- 排查「命令在别处能跑、在这跑不了」的环境差异。

## 环境事实

| 项 | 值 | 验证方式 |
|---|---|---|
| 系统 | macOS 27.2（build 26B123） | `sw_vers` [实测] |
| 芯片 | Apple M5（arm64） | `sysctl -n machdep.cpu.brand_string` [实测] |
| 内存 | 24 GB | `sysctl -n hw.memsize` [实测] |
| 磁盘可用 | 约 767 GB | `df -h .` [实测] |
| git | 2.54.0 (Apple Git-157) | `git --version` [实测] |
| FFmpeg / ffprobe | 9.0.2（Homebrew，GPL 构建） | `ffmpeg -version` [实测] |
| Python | 3.9.6（系统自带） | `python3 -V` [实测] |
| Node / pnpm | 26.12.0 / 12.6.0 | [实测] |
| 已装 Python 包 | numpy、Pillow（PIL） | `importlib.util.find_spec` [实测] |
| 未装 | pyyaml、cv2、moviepy、torch、whisper、auto-editor、yt-dlp、sox、ImageMagick | [实测] |

> **推论**：本仓脚本一律只用 Python 标准库；需要第三方包时在技能包内写清安装步骤，不假设已装。

## FFmpeg 能力边界（关键）

构建配置（节选）：`--enable-gpl --enable-libx264 --enable-libx265 --enable-libsvtav1 --enable-libvpx --enable-libdav1d --enable-libvmaf --enable-libopus --enable-libmp3lame --enable-videotoolbox` [实测]

| 能力 | 是否可用 | 说明 |
|---|---|---|
| libx264 / libx265 | ✅ | H.264 / H.265 软编 |
| libsvtav1 | ✅ | AV1 软编 |
| libvpx-vp9 | ✅ | VP9 |
| prores（含 prores_videotoolbox） | ✅ | 母版 / 中间格式 |
| h264_videotoolbox | ✅ | 硬件加速；速度优先场景 |
| loudnorm 滤镜 | ✅ | EBU R128 响度标准化 |
| xfade / overlay / zoompan / concat | ✅ | 转场、叠加、运镜、拼接 |
| **subtitles / ass 滤镜** | ❌ | **该构建未启用 libass**，无法烧录字幕 |
| **drawtext 滤镜** | ❌ | **未启用 freetype**，无法直接绘制文字 |

### 字幕烧录的替代方案（按推荐顺序）

1. **Pillow 渲染 PNG 字幕层 + `overlay` 合成**：本机 Pillow 可用，可完全脚本化；适合批量、模板化字幕。
2. **换用带 libass 的 FFmpeg**：如 `brew tap homebrew-ffmpeg/ffmpeg` 后装带 `--with-libass` 的构建（需编译，耗时）；装好后 `subtitles` 滤镜可用。
3. **NLE / 剪映 / Remotion 内烧录**：交互式项目直接由上层工具出片，FFmpeg 只做转码。

> 任何依赖 `subtitles` / `drawtext` 的技能与 SOP，执行前必须先探测：`ffmpeg -hide_banner -h filter=subtitles`，失败则走方案 1 或 3。

## 性能基线

测试素材：`testsrc2` 合成 1080p30 / 10s / H.264 源（合成画面编码压力低于实拍，结果偏乐观）。

| 任务 | 参数 | 耗时 | 相对实时 |
|---|---|---|---|
| H.264 软编 | libx264 `-preset veryfast -crf 23` | 0.63 s | ≈ 16× |
| H.264 软编 | libx264 `-preset medium -crf 23` | 1.35 s | ≈ 7.4× |
| H.264 硬编 | h264_videotoolbox `-b:v 4M` | 1.27 s | ≈ 7.9× |
| 响度测量 | loudnorm 单遍 | < 1 s | — |

[推断] 实拍 4K 素材的软编速度会明显低于上表；代理剪辑仍是 4K 项目的默认策略。批量导出前先用 30s 片段估算总时长。

## 可操作步骤（新建项目 / 新机器时的环境自检）

```bash
cd <仓库根目录>
python3 scripts/validate.py
ffmpeg -version | head -1
ffmpeg -hide_banner -encoders | grep -E 'libx264|libx265|libsvtav1|prores'
ffmpeg -hide_banner -h filter=subtitles >/dev/null 2>&1 && echo "字幕滤镜可用" || echo "字幕滤镜缺失：走 Pillow overlay 方案"
python3 -c "import PIL, numpy; print('PIL', PIL.__version__, 'numpy', numpy.__version__)"
```

## 参数与阈值

| 场景 | 参数 | 值 |
|---|---|---|
| 短视频交付 | H.264 / AAC / 1080p | crf 20–23，音频 192k |
| 母版 | ProRes 422 / 422 HQ | 保留最大后期空间 |
| 响度 | 短视频 / 长视频 | -14 LUFS / -16 LUFS（±1） |
| 硬件编码 | videotoolbox | 只在赶时间时用，质量弱于 x264 medium |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 假设机器上有 libass / drawtext | 本机构建未启用，命令直接报 Unknown filter | 先探测，或走 Pillow overlay |
| 用 `python3 -m pip install` 装一堆包 | 系统 Python 3.9 较旧，依赖冲突风险高 | 用独立 venv 或 Node/FFmpeg 方案 |
| 在系统 Python 里跑长期任务 | 3.9 已停止安全更新 [事实] | 建 `.venv` 并用 3.11+ 做新脚本 |

## 验证方式

- 环境是否可用：跑上面「可操作步骤」全绿。
- 命令是否兼容：先 `ffmpeg -f lavfi -i testsrc2` 生成测试片段跑通，再上真实素材。

## 关联条目

- 库：kb/ffmpeg、kb/moviepy、kb/pyav
- 工作流：kb/transcode-delivery、kb/automation-pipeline
- 技能：ffmpeg-render、subtitle-pipeline、qc-deliver

## 来源

1. 本机实测命令输出（2026-11-03）：`sw_vers`、`sysctl`、`ffmpeg -version`、`ffmpeg -filters`、`ffmpeg -buildconf`。
2. [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）
3. [Homebrew ffmpeg formula](https://formulae.brew.sh/formula/ffmpeg)（访问 2026-11-03）
