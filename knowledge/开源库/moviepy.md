---
id: kb/moviepy
title: "MoviePy · Python 视频剪辑脚本库"
type: 库
domain: [粗剪, 精剪, 声音, 字幕, 动效, 交付]
status: 可用
confidence: 中
license: "MIT"
repo: "https://github.com/Zulko/moviepy"
docs: "https://moviepy.readthedocs.io/"
language: Python
platform: [macOS, Linux, Windows]
tags: [moviepy, python, 剪辑, 合成, 字幕, 自动化]
related: [kb/ffmpeg, kb/pyav, kb/environment-local]
updated: 2026-11-03
owner: lib-scout
---

# MoviePy · Python 视频剪辑脚本库

## 一句话定位

用 Python 代码完成「裁剪、拼接、叠加、字幕、音频」的剪辑库，把时间线写成脚本；主要服务 S4 粗剪、S5 精剪、S6 声音、S7 字幕，末尾调用 FFmpeg 完成 S10 导出。适合模板化批量生产与原型验证，不适合长片或 4K 的高性能处理。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 按时间码裁剪、拼接、变速、画中画叠加 | 多轨时间线的交互式预览与拖拽编辑 |
| 文本、图片、字幕层合成（Pillow 渲染） | 复杂转场与关键帧动画的可视化编排 |
| 音频混音、音量调整、音画对齐 | 长视频（>30min）或 4K 的高吞吐批处理 |
| 批量模板：固定版式 + 换素材 / 换文案 | 帧级色彩管理与专业调色 |

## 核心能力

- 时间线对象：`VideoFileClip` / `AudioFileClip` / `ImageClip` / `ColorClip`，组合成 `CompositeVideoClip`。
- 剪辑操作：`subclipped`、`resized`、`with_duration`、`with_position`、`concatenate_videoclips`。
- 文本与字幕：`TextClip`（v2 用 Pillow 渲染，需指定字体文件路径）。
- 音频：`AudioFileClip`、`CompositeAudioClip`、`with_volume_scaled`，可单独导出音轨。
- 导出：`write_videofile` 透传 FFmpeg 参数（codec、fps、bitrate、preset）。

## 安装 / 获取

```bash
# 本机 python3.9.6，用独立 venv 避免污染系统 Python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "moviepy==2.2.1"
python -c "import moviepy; print(moviepy.__version__)"   # 预期输出 2.2.1
```

前提：Python ≥3.9（2.2.x 的 `requires-python`）；依赖 `imageio_ffmpeg`、`pillow`、`numpy>=1.25`、`opencv-python-headless`，pip 会自动安装。Windows / Linux 同样适用。

## 最小可用示例

```python
# demo.py —— 与 moviepy 2.2.x 兼容（v2 API）
from moviepy import VideoFileClip

clip = VideoFileClip("input.mp4").subclipped(0, 5).resized(0.5)
clip.write_videofile(
    "out.mp4",
    codec="libx264",
    audio_codec="aac",
    fps=30,
    preset="veryfast",
    ffmpeg_params=["-crf", "23", "-pix_fmt", "yuv420p"],
)
clip.close()
```

```bash
python demo.py
ffprobe -v error -show_entries stream=width,height,codec_name:format=duration \
  -of default=nw=1 out.mp4
```

预期结果：`out.mp4` 时长 5 秒、宽度为原片一半、H.264 + AAC。若只做切割与转码，直接用 `kb/ffmpeg` 更快。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| Python 生态直通，容易接 CSV / 模板 / 数据 | 逐帧在 Python 层处理，长片性能差 |
| API 可读性高，适合原型和批量模板 | v1 → v2 破坏性改名，旧教程代码大量失效 |
| 自带 FFmpeg 依赖，开箱即用 | 内置 FFmpeg 与系统 FFmpeg 不是同一个二进制 |

1. **v2 断代：旧代码直接报错**。现象：`ModuleNotFoundError: No module named 'moviepy.editor'`，或 `AttributeError: 'VideoFileClip' object has no attribute 'subclip'`。原因：2.0 起移除 `moviepy.editor`，`.set_*` 全部改为 `.with_*`，`subclip` 改名 `subclipped`、`resize` 改名 `resized`、`Clip.fx` 改为 `with_effects`。规避：统一写成 `from moviepy import VideoFileClip`，按 v2 名字调用；升级文档见来源 3。
2. **内置 FFmpeg 与系统 FFmpeg 不一致**。现象：终端里 `ffmpeg` 能用的编码器 / 硬件加速，`write_videofile` 却报 unknown encoder 或速度明显不同。原因：MoviePy 默认调用 `imageio-ffmpeg` 自带的独立二进制，不看 `PATH`。规避：需要复用系统构建时设置 `os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"`；或让 MoviePy 只做剪辑、导出交给系统 FFmpeg。
3. **长片 / 4K 内存与耗时不可控**。现象：10 分钟 4K 素材合成时内存飙升、进度条长时间不动。原因：每帧解码成 numpy 数组在 Python 层合成，内存随分辨率与并发线性增长。规避：长片用 `kb/ffmpeg` 或 `kb/pyav` 做转码与切片，MoviePy 只处理短片段或固定模板。
4. **TextClip 找不到字体**。现象：服务器上渲染文字报字体相关错误或输出方块。原因：v2 的 `TextClip` 需要显式字体文件路径，且容器镜像常无中文字体。规避：安装字体（如 `font-noto-cjk`）并传 `font="/path/NotoSansCJK.ttc"`，或改用 Pillow 预渲染 PNG 再叠加。

## 适用 / 不适用

- 适用：固定模板的批量短视频（换文案 / 换素材）、字幕与图文叠加、音频替换与混音、把剪辑流程写成可版本管理的 Python 脚本。
- 不适用：30 分钟以上长片、4K 高码率批量转码（改用 `kb/ffmpeg`）；需要精确帧级控制与高性能解码（改用 `kb/pyav`）；交互式创作（改用 NLE）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：短视频模板化生产的 S4–S7（粗剪、字幕、混音），导出阶段交给 `kb/ffmpeg` 统一参数。
- 关联条目：`kb/ffmpeg`（底层与导出）、`kb/pyav`（更高性能的帧级替代）、[本机环境基线](../环境/environment-local.md)（Python 版本与已装包）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / Apple M5 / Python 3.9.6 | `python3 -c "import moviepy"` | `ModuleNotFoundError`，本机未安装；本文示例未在本机运行 |
| 2026-11-03 | PyPI / GitHub | 查 2.2.1 元数据与升级文档 | 最新版 2.2.1（2025-05-21），`requires-python>=3.9`，与 3.9.6 兼容 [事实] |

> 状态说明：结构、安装命令与版本兼容性已核验；示例代码未本机跑通，故标 `可用` 而非 `已验证`。

## 来源

1. [MoviePy GitHub 仓库](https://github.com/Zulko/moviepy)（访问 2026-11-03）：MIT 许可，Python；最新 release `v2.2.1`（发布 2025-05-21）
2. [MoviePy 官方文档](https://moviepy.readthedocs.io/)（访问 2026-11-03）
3. [MoviePy v2 升级文档（官方 docs 源文件）](https://github.com/Zulko/moviepy/blob/master/docs/getting_started/updating_to_v2.rst)（访问 2026-11-03）：移除 `moviepy.editor`、`.set_*`→`.with_*`、`resize`→`resized`、弃用 ImageMagick
4. [PyPI moviepy](https://pypi.org/project/moviepy/)（访问 2026-11-03）：2.2.1，`requires-python>=3.9`，依赖含 pillow / imageio_ffmpeg
