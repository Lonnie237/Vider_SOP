---
id: kb/blender-vse
title: "Blender VSE · 开源 NLE 与 3D/合成一体"
type: 工具
domain: [粗剪, 精剪, 字幕, 调色, 动效, 交付]
status: 可用
confidence: 中
license: "GPL-2.0-or-later"
repo: "https://projects.blender.org/blender/blender"
docs: "https://docs.blender.org/manual/en/latest/video_editing/index.html"
language: "C / C++（Python bpy 脚本）"
platform: [macOS, Linux, Windows]
tags: [blender, vse, nle, 合成, 调色, 3d, bpy]
related: [kb/ffmpeg, kb/opentimelineio, kb/editly]
updated: 2026-11-03
owner: lib-scout
---

# Blender VSE · 开源 NLE 与 3D/合成一体

## 一句话定位

Blender 内置的视频序列编辑器（Video Sequence Editor，VSE）把「多轨剪辑 + 调色 + 合成 + 3D 动画」放在同一个工程里，并用 Python（`bpy`）脚本化。服务 S4–S5 剪辑、S7 字幕、S8 调色、S9 3D 包装、S10 导出；适合零成本的复杂包装与三维合成，不适合作为高频纯剪辑的主力工具。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 多轨剪辑、转场、文字/字幕条 | 高频纯剪辑的效率（拖拽、预览、快捷键不如专用 NLE） |
| 三维动画、粒子、合成节点与视频同工程 | 多人并行编辑同一工程（.blend 为二进制） |
| 色彩管理与调色（配合合成节点） | 轻量批处理与命令行流水线 |
| bpy 脚本化，可无头渲染 | 跨工具工程交换（需另存 OTIO / XML） |

## 核心能力

- VSE：多通道（channel）视频 / 音频 / 图片 / 文字条带（strip），内置 fade、wipe、gamma cross 等转场。
- 合成与 3D：同一场景里直接放 3D 对象、EEVEE / Cycles 渲染结果与视频叠加。
- 脚本化：`bpy` 可建条带、设渲染参数、批量渲染；`blender -b -P script.py` 无头执行。
- 导出：内置 FFmpeg 输出（容器 / 编码 / 码率 / 色彩），也可渲染为图片序列再交 `kb/ffmpeg`。

## 安装 / 获取

```bash
# macOS（cask 版本可能滞后于官网，安装后核对版本）
brew install --cask blender
blender --version | head -1        # 期望 5.2.x LTS

```

前提：桌面使用需图形环境，无头渲染 `blender -b` 不需要显示器；5.2 为 LTS（2 年维护），生产环境锁 LTS 小版本。Linux / Windows 用官网安装包。

## 最小可用示例

```python
# build_vse.py —— 无头建一条 VSE 时间线并渲染
# 用法：cd 到素材目录，执行 blender -b -P build_vse.py
import bpy

scene = bpy.context.scene
scene.sequence_editor_create()
editor = scene.sequence_editor
strips = getattr(editor, "strips", None) or editor.sequences   # 5.x / 旧版 API 兼容

clip = strips.new_movie("clip1", "input.mp4", channel=1, frame_start=1)
scene.frame_end = clip.frame_final_end - 1

# 输出规格：竖屏 1080×1920 / 30fps / H.264
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = "out.mp4"

# VSE 素材是 sRGB 视频，用 Standard 避免 AgX/Filmic 把画面洗灰
scene.view_settings.view_transform = "Standard"

bpy.ops.render.render(animation=True)
print("strips:", len(strips))
```

```bash
blender -b -P build_vse.py
ffprobe -v error -show_entries stream=width,height,codec_name:format=duration \
  -of default=nw=1 out.mp4
```

预期结果：终端打印条带数量，生成 `out.mp4`（1080×1920、H.264、时长等于素材）。

## 优缺点与坑位

优点：零成本、剪辑 + 3D + 合成一体、可脚本化与无头渲染。坑位按「现象 → 原因 → 规避」列出：

1. **导出画面发灰 / 过曝**。现象：VSE 里预览正常，渲染出的视频偏灰、对比度低。原因：Blender 默认视图变换（如 AgX）会作用于 VSE 输出，等于给 sRGB 视频又做了一次 filmic 映射。规避：渲染前设 `scene.view_settings.view_transform = "Standard"`，并核对素材色彩空间。
2. **工程打不开 / 脚本报错（版本与 API 双坑）**。现象：新版 Blender 保存的 `.blend` 在旧版打不开；脚本里 `editor.sequences` 报 `AttributeError`。原因：工程格式向后不兼容；VSE 条带 API 在新版由 `sequences` 更名为 `strips`。规避：团队锁同一 LTS 版本（5.2.x）；脚本用 `getattr(editor, "strips", None) or editor.sequences` 兼容两代 API。
3. **团队协作几乎不可行**。现象：两人同时改一个工程，合并时互相覆盖；Git diff 无意义。原因：`.blend` 是二进制快照，没有文本级时间线与锁机制。规避：时间线用 `kb/opentimelineio` 或 NLE 的 XML 交换，Blender 只承接 3D/合成片段；一人负责一个工程。
4. **把它当纯剪辑主力**。现象：素材多、时长长时拖拽卡顿，快捷键不符合剪辑习惯，返工多。原因：VSE 定位是「附带剪辑的三维软件」，不是高频 NLE。规避：粗剪交给 `kb/auto-editor` / `kb/ffmpeg`，精剪交给 NLE，Blender 只做包装、调色与合成段。

## 适用 / 不适用

- 适用：3D 片头 / 数据立体包装、视频与三维合成、零预算调色、需要脚本化批量出包装段的流水线。
- 不适用：高频纯剪辑（用 NLE 或 `kb/ffmpeg`）、多人协作项目（用 NLE 工程 + OTIO）、纯转码（用 `kb/ffmpeg`）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：宣传片 / 数据动画类 SOP 的 S9 三维包装与 S8 调色，成片交 `kb/ffmpeg` 做统一封装与响度。
- 关联条目：`kb/ffmpeg`（编码与后处理）、`kb/opentimelineio`（时间线交换；Blender 5.3 计划原生支持 OTIO）、`kb/editly`（轻量模板替代）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | blender.org | 查版本与许可 | 5.2.3 LTS（2026-10-22 发布）；源码默认 GPL-2.0-or-later；5.3 预计 2026-11-10 发布并原生支持 OTIO [事实] |

## 来源

1. [Blender 官网下载页](https://www.blender.org/download/)（访问 2026-11-03）：最新 5.2.3 LTS（2026-10-22 发布）；5.3 预计 2026-11-10，含 OpenTimelineIO 与 VSE 改进
2. [Blender 许可说明](https://www.blender.org/about/license/)（访问 2026-11-03）：源码默认 GPL v2 or later
3. [Blender 手册 · Video Editing](https://docs.blender.org/manual/en/latest/video_editing/index.html)（访问 2026-11-03）：VSE 条带、转场、渲染设置
