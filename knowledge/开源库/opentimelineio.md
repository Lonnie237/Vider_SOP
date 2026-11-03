---
id: kb/opentimelineio
title: "OpenTimelineIO · 时间线交换格式与 Python API"
type: 库
domain: [粗剪, 精剪, 交付, 自动化]
status: 可用
confidence: 中
license: "Apache-2.0"
repo: "https://github.com/AcademySoftwareFoundation/OpenTimelineIO"
docs: "https://opentimelineio.readthedocs.io/"
language: C++
platform: [macOS, Linux, Windows]
tags: [opentimelineio, otio, 时间线, 剪辑交换, edl, xml, 自动化]
related: [kb/ffmpeg, kb/auto-editor, kb/remotion]
updated: 2026-11-03
owner: lib-scout
---

# OpenTimelineIO · 时间线交换格式与 Python API

## 一句话定位

用一份开放的 JSON 结构（`.otio`）描述「哪段素材、从第几帧到第几帧、放在哪条轨」；它是剪辑决策的交换层，不是渲染器。服务 S4–S5 的结构化剪辑、S10 交付前与 NLE / 调色 / 混音的交接，让程序化剪辑与人工精剪共用同一份时间线。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 用 Python 程序化生成 / 修改时间线 | 直接解码、渲染、编码视频（本身不含媒体处理） |
| 在 NLE、调色、混音工具之间交换剪辑结构 | 完整表达任意 NLE 的全部特效与私有参数 |
| 导出 / 读入 FCP XML、EDL、AAF 等格式（需适配器） | 开箱即用覆盖所有格式（内置只有 .otio 系列） |
| 统一 clip 引用与时间范围，便于批量生成 ffmpeg 命令 | 替代 FFmpeg / Remotion 的成片产出环节 |

## 核心能力

- 数据模型：`Timeline` → `Track` → `Clip` / `Gap` / `Transition`，嵌套 `Stack` 表示多轨。
- 时间模型：`RationalTime`（帧数 + 帧率）与 `TimeRange`，避免浮点时间误差。
- 素材引用：`ExternalReference`（target_url）与 `MissingReference`，便于重链媒体。
- 适配器（adapter）：`otio.adapters.write_to_file` / `read_from_file`，内置 `otio_json`、`otiod`、`otioz`。
- 插件生态：官方 `OpenTimelineIO-Plugins` 与社区适配器补齐 FCP XML / EDL / AAF 等。
- 版本迁移：schema 有版本号，配套工具做旧工程升级。

## 安装 / 获取

```bash
# 本机 Python 3.9.6：0.18.1 提供 cp39 macOS arm64 wheel，可直接装
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "opentimelineio==0.18.1"
python -c "import opentimelineio as otio; print(otio.__version__)"   # 预期 0.18.1
```

前提：PyPI 的 `requires-python` 为 `>3.9.0`；wheel 覆盖 CPython 3.9–3.13（macOS arm64 要求 macOS 11+，本机满足），Linux 为 manylinux2014，Windows 为 win_amd64。其他解释器需源码构建（C++ 工具链）。

## 最小可用示例

```python
# demo.py —— 造一条 3 秒 clips 的时间线，存成 .otio 再读回
import opentimelineio as otio

timeline = otio.schema.Timeline(name="demo")
track = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
timeline.tracks.append(track)

clip = otio.schema.Clip(
    name="shot-01",
    media_reference=otio.schema.ExternalReference(
        target_url="file:///Users/me/media/input.mp4"
    ),
    source_range=otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(0, 30),
        duration=otio.opentime.RationalTime(90, 30),   # 90 帧 @30fps = 3s
    ),
)
track.append(clip)

otio.adapters.write_to_file(timeline, "demo.otio")
back = otio.adapters.read_from_file("demo.otio")
print(back.name, len(back.tracks))                        # demo 1
print(otio.adapters.available_adapter_names())            # 当前环境可用适配器
```

```bash
python demo.py
head -c 200 demo.otio      # 原生格式是可读 JSON
```

预期结果：生成 `demo.otio`（JSON，含 `OTIO_SCHEMA` 与 `metadata`），读回后名称与轨道数一致；`available_adapter_names()` 至少包含 `otio_json`。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 开放格式 + Apache-2.0，可安全嵌入商业流水线 | 只是数据层，渲染要自己做 |
| Python API 清晰，适合程序化剪辑 | 非原生格式依赖适配器，round-trip 会丢信息 |
| 被 Resolve / 多家后期工具生态支持 | 版本升级快，跨版本兼容需测试 |

1. **误以为 `.otio` 能直接出片**。现象：`ffmpeg -i demo.otio` 报 `Invalid data found`；把文件拖进播放器打不开。原因：OTIO 只记录「引用哪段素材 + 时间范围」，不含解码与渲染逻辑，FFmpeg 也没有 OTIO 解复用器。规避：在 Python 里遍历 `track` 的 `Clip`，按 `source_range` 生成 `ffmpeg -ss/-t` 命令再拼接；或把 .otio 交给 NLE / 支持 OTIO 的渲染工具。
2. **适配器找不到，读不了 NLE 工程**。现象：`read_from_file("edit.xml")` 抛 `Adapter ... not found`。原因：内置适配器只有 `otio_json`、`otiod`、`otioz`；FCP XML、EDL、AAF 等要另装 `OpenTimelineIO-Plugins` 或社区适配器（具体包名与支持矩阵以官方文档为准 [待确认]）。规避：先打印 `otio.adapters.available_adapter_names()` 确认能力，再决定转换路径。
3. **跨版本 / round-trip 丢信息**。现象：高版本生成的 `.otio` 在旧版库打不开；或 XML → OTIO → XML 后变速、特效、多机位丢失。原因：OTIO schema 随版本演进，各适配器实现程度不同，非原生概念只能降级表达。规避：团队锁定同一版本（如 0.18.1）；转换前后做小样本 round-trip 对比，把已知丢失项写成清单。
4. **媒体路径失效**。现象：换机器 / 改目录后 clip 全变 `MissingReference`，NLE 里素材离线。原因：`ExternalReference.target_url` 多为绝对路径。规避：统一素材根目录并用 `otio.media_linker` 重链，或在生成时写相对路径 / 归档时用 `.otiod` 打包素材。

## 适用 / 不适用

- 适用：程序化剪辑（批量切片、自动套版）、NLE 之间的剪辑结构交接、交付前把切点交给调色 / 混音、把 `kb/auto-editor` 的切点与人工精剪结果合并。
- 不适用：纯 FFmpeg 能完成的转码 / 裁剪（直接用 `kb/ffmpeg`）；需要渲染成片（用 FFmpeg / Remotion / NLE）；只做单轨简单拼接时，OTIO 增加一层抽象成本。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：访谈 / 播客 / 教程长视频的 S4–S5 剪辑交接，S10 交付前向调色、混音、字幕环节传递时间线。
- 关联条目：`kb/ffmpeg`（按 OTIO 切点渲染）、`kb/auto-editor`（初剪切点来源）、`kb/remotion`（渲染成片后作为 clip 引用）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / M5 / Python 3.9.6 | `python3 -c "import opentimelineio"` | 本机未安装；示例未在本机执行，API 与适配器按官方文档核验 |
| 2026-11-03 | PyPI / GitHub | 查版本与 wheel | release `v0.18.1`（2025-11-09）；PyPI `requires-python>3.9.0`，有 `cp39-macosx_11_0_arm64` wheel [事实] |

## 来源

1. [OpenTimelineIO GitHub 仓库](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)（访问 2026-11-03）：Apache-2.0、C++；最新 release `v0.18.1`（2025-11-09）
2. [OpenTimelineIO 官方文档](https://opentimelineio.readthedocs.io/)（访问 2026-11-03）
3. [Adapters 文档](https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html)（访问 2026-11-03）：内置 `otio_json` / `otiod` / `otioz`，其余靠 `OpenTimelineIO-Plugins` 与社区适配器
4. [PyPI opentimelineio](https://pypi.org/project/opentimelineio/)（访问 2026-11-03）：0.18.1，`requires-python>3.9.0`，wheel 覆盖 cp39–cp313 三平台
