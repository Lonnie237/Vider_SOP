---
id: kb/pyav
title: "PyAV · FFmpeg 库的 Python 绑定"
type: 库
domain: [素材管理, 粗剪, 精剪, 声音, 交付]
status: 可用
confidence: 中
license: "BSD-3-Clause"
repo: "https://github.com/PyAV-Org/PyAV"
docs: "https://pyav.basswood.io/docs/stable/"
language: Python
platform: [macOS, Linux, Windows]
tags: [pyav, python, ffmpeg, 解码, 转码, 抽帧]
related: [kb/ffmpeg, kb/moviepy, kb/environment-local]
updated: 2026-11-03
owner: lib-scout
---

# PyAV · FFmpeg 库的 Python 绑定

## 一句话定位

把 FFmpeg 的容器、流、编解码器、帧直接暴露给 Python：需要逐帧读写、精确控制编码参数时用它。服务 S3 抽帧与转码、S4–S5 逐帧处理、S6 音频、S10 交付编码，介于「subprocess 调 ffmpeg」和 `kb/moviepy` 的剪辑抽象之间。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 逐帧解码为 numpy 数组，处理后重新编码 | 现成的时间线 / 剪辑语义（无 clip、拼接 API） |
| 精确控制编码器、码率、像素格式、关键帧 | 滤镜图的简写封装（需自己串 `av.filter`，API 底层） |
| 按流 / 包处理，做 remux、抽帧、音轨提取 | 跨平台一致的 FFmpeg 版本（wheel 内置版本固定） |

## 核心能力

- 容器与流：`av.open()`、`container.streams`、`demux()` / `decode()` / `mux()`。
- 帧与数组：`frame.to_ndarray(format="rgb24")`、`frame.to_image()`、`VideoFrame.reformat()`。
- 编码：`container.add_stream("libx264", rate=...)` 后设置 `width` / `height` / `pix_fmt`，再 `stream.encode(frame)`。
- 音频与时间戳：音频流解码 / 重采样；`frame.pts`、`frame.time` 用于按时间定位；滤镜可用 `av.filter.Graph` 自搭。

## 安装 / 获取

本机 Python 3.9.6（19.x 要求 ≥3.12，需 pin 15.1.0）：

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "av==15.1.0"          # 最后一个支持 Python 3.9 的版本线
python -c "import av; print(av.__version__)"  # 预期 15.1.0
```

要最新版（需 Python ≥3.12）：`brew install python@3.12` → `python3.12 -m venv .venv312` → `pip install "av==19.0.2"`。

前提：PyPI 提供 macOS / Linux / Windows 预编译 wheel，内置 FFmpeg，无需系统装 FFmpeg；macOS arm64 的 cp39 wheel 要求 macOS 13+（本机满足）。

## 最小可用示例

```python
# 1) 解码并抽帧为 numpy 数组（S3 素材整理 / 缩略图）
import av
with av.open("input.mp4") as container:
    stream = container.streams.video[0]
    for i, frame in enumerate(container.decode(stream)):
        img = frame.to_ndarray(format="rgb24")   # (H, W, 3)
        if i == 0:
            print(img.shape, frame.time)         # 例如 (720, 1280, 3) 0.0
        if i >= 4:
            break

# 2) 转码为 H.264 / yuv420p（S10 交付）
src = av.open("input.mp4")
dst = av.open("out.mp4", mode="w")
in_stream = src.streams.video[0]
out_stream = dst.add_stream("libx264", rate=in_stream.average_rate)
out_stream.width = in_stream.codec_context.width
out_stream.height = in_stream.codec_context.height
out_stream.pix_fmt = "yuv420p"
for frame in src.decode(in_stream):
    for packet in out_stream.encode(frame.reformat(format="yuv420p")):
        dst.mux(packet)
for packet in out_stream.encode():   # flush：不写会丢尾部帧
    dst.mux(packet)
src.close()
dst.close()
```

```bash
python demo.py
ffprobe -v error -show_entries stream=codec_name,width,height -of default=nw=1 out.mp4
```

预期结果：抽出 5 帧 RGB 数组（打印 shape 与时间戳）；`out.mp4` 为 H.264 / yuv420p，分辨率与源一致。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 帧级控制，性能远好于 Python 层逐帧合成 | API 底层，没有剪辑语义，代码量大 |
| wheel 内置 FFmpeg，安装即用 | Python 版本门槛高，旧解释器装不上新版 |
| 与 NumPy / Pillow 数据互通 | 忘记 flush / close 会产出坏文件 |

1. **Python 版本门槛导致装不上**。现象：py3.9 执行 `pip install av` 报 `No matching distribution found` 或解析到旧版本。原因：19.x 要求 ≥3.12，18.x 要求 ≥3.11，16–17.x 要求 ≥3.10，15.x 才支持 3.9。规避：3.9 环境显式 `pip install "av==15.1.0"`，或装 `python@3.12` 建新 venv；不要写不锁版本的 `av`。
2. **wheel 内置 FFmpeg 与系统 FFmpeg 不是一回事**。现象：系统 `ffmpeg` 有的编码器 / 滤镜，PyAV 里找不到，或同一参数输出不同。原因：官方 wheel 打包固定版本的 FFmpeg，与 `/opt/homebrew/bin/ffmpeg` 构建配置不同。规避：需要系统那套能力时改用 CLI，或 `pip install av --no-binary av` 针对系统 FFmpeg 自编译。
3. **忘记 flush 与 close，输出文件损坏**。现象：`out.mp4` 能生成但尾部缺帧、时长变短，或文件为 0 字节。原因：编码器有内部缓冲，需 `encode()` 无参 flush 后才完整；容器不 close 不写索引。规避：编码循环后必须 flush 再 `close()`（或用 with）。
4. **颜色通道错位**。现象：抽出的图偏蓝 / 偏红。原因：`to_ndarray()` 默认 RGB，而 OpenCV 习惯 BGR。规避：显式写 `format="rgb24"`，用 OpenCV 前转 `bgr24`，或 `frame.to_image()` 直接拿 PIL Image。

## 适用 / 不适用

- 适用：批量抽帧 / 缩略图、逐帧算法（检测、水印）、精确编码参数、音轨提取、把处理嵌进 Python 服务。
- 不适用：只想裁剪拼接转码（用 `kb/ffmpeg` CLI 更省事）；需要剪辑语义与快速原型（用 `kb/moviepy`）；交互式创作（用 NLE）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：S3 素材抽帧与代理生成、S10 定制编码参数的交付变体；水印 / 检测类逐帧流程以本文为接口。
- 关联条目：`kb/ffmpeg`（CLI 与能力边界）、`kb/moviepy`（更高层剪辑封装）、[本机环境基线](../环境/environment-local.md)。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / M5 / Python 3.9.6 | `python3 -c "import av"` | `ModuleNotFoundError`，本机未安装；示例未在本机运行 |
| 2026-11-03 | PyPI 元数据 | 查各版本 `requires_python` 与 wheel 文件名 | 19.0.2 要求 ≥3.12；15.1.0 要求 ≥3.9 且有 `cp39-macosx_13_0_arm64` wheel [事实] |

> 状态说明：版本矩阵与安装可行性已核验；示例未本机跑通，故标 `可用`。

## 来源

1. [PyAV GitHub 仓库](https://github.com/PyAV-Org/PyAV)（访问 2026-11-03）：BSD-3-Clause；最新 release `v19.0.2`（2026-10-21）
2. [PyAV 官方文档](https://pyav.basswood.io/docs/stable/)（访问 2026-11-03）：容器 / 流 / 帧模型与 cookbook
3. [PyPI av](https://pypi.org/project/av/)（访问 2026-11-03）：各版本 `requires_python` 与 wheel 平台标签
4. [PyAV 安装文档](https://pyav.org/docs/stable/overview/installation.html)（访问 2026-11-03）：wheel 内置 FFmpeg，三平台均有预编译包
