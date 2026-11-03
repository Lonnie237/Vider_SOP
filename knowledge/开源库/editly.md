---
id: kb/editly
title: "Editly · Node.js 声明式剪辑与模板出片"
type: 工具
domain: [粗剪, 精剪, 字幕, 动效, 交付]
status: 可用
confidence: 中
license: "MIT"
repo: "https://github.com/mifi/editly"
docs: "https://github.com/mifi/editly#readme"
language: TypeScript
platform: [macOS, Linux, Windows]
tags: [editly, nodejs, 声明式, 模板, 转场, 字幕]
related: [kb/remotion, kb/ffmpeg, kb/moviepy]
updated: 2026-11-03
owner: lib-scout
---

# Editly · Node.js 声明式剪辑与模板出片

## 一句话定位

用一份 JSON / JSON5「剪辑规格」描述 clips、layers、转场、字幕与配乐，由 Node.js 调 ffmpeg 流式出片。服务 S4–S5 模板化剪辑、S7 图文与字幕、S9 转场包装、S10 出片；适合「固定版式 + 换素材 / 换文案」的批量短视频。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| JSON 规格批量出片（片头 / 拼图 / 图文卡） | 多轨精细剪辑与实时预览 |
| 自动转场、音频交叉淡化、ducking、响度归一 | 专业调色、复杂合成节点 |
| 自动缩放 / 加黑边适配任意画幅，输出 GIF | 长期维护保障（项目已不活跃） |
| 自定义 Canvas / GL 动态层 | 时间线交换与 NLE 协作 |

## 核心能力

- 剪辑规格：`clips` 数组 + 每段 `layers`（video / image / title / subtitle / canvas / gl）。
- 时间控制：`duration` 与 `cutFrom` / `cutTo`，自动变速对齐段长。
- 转场：每段可配 `transition: {name, duration}`，内置 fade / wipe 等。
- 音频：`--audio-file-path` 配乐，自动 ducking、crossfade、normalization。
- 输出：任意宽高比自动 letterbox，支持 mp4 / GIF、`--fast` 快速模式。

## 安装 / 获取

```bash
# Node 需已安装（本机 Node 26.12.0）；editly 不自带 ffmpeg，必须先有 ffmpeg/ffprobe
ffmpeg -version | head -1          # 本机 9.0.2，满足
npm i -g editly
editly --help                      # 验证安装
```

前提：Node LTS（README 建议最新 LTS）；`ffmpeg`、`ffprobe` 在 `PATH` 中；Linux 上若用 `gl` 层还需 headless-gl 的系统依赖。

维护状态（截至 2026-11-03）：npm 稳定版 `0.14.2`；GitHub 最新 release 为 `v0.15.0-rc.1`（2025-01-19）；仓库最后提交 2025-05-12。**属维护不活跃**，新项目应先评估替代（见「适用 / 不适用」）。

## 最小可用示例

```json5
// my-spec.json5 —— 两段：视频片段 + 标题卡，带淡入转场
{
  outPath: "out.mp4",
  width: 1080,
  height: 1920,
  fps: 30,
  clips: [
    { duration: 3, layers: [{ type: "video", path: "clip1.mp4" }] },
    {
      duration: 2,
      transition: { name: "fade", duration: 0.5 },
      layers: [{ type: "title", text: "Hello Editly", fontSize: 0.1 }],
    },
  ],
}
```

```bash
# 出片（配乐可选）
editly my-spec.json5 --out out.mp4 --audio-file-path music.mp3
ffprobe -v error -show_entries stream=width,height:format=duration -of default=nw=1 out.mp4
```

预期结果：生成 1080×1920、约 5 秒的 H.264 mp4，第二段以 0.5s 淡入出现。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 声明式规格，批量出片代码量极小 | 项目维护不活跃，依赖版本风险 |
| 流式编辑，省磁盘、速度快 | 依赖外部 ffmpeg，环境不达标直接失败 |
| 自带 Canvas 渲染文字，不依赖 libass | 复杂时间线与特效能力有限 |

1. **维护停滞与版本分裂**。现象：按 README 的 ESM 写法在 npm 稳定版上报 `ERR_REQUIRE_ESM` 或语法错误。原因：npm 稳定版停在 `0.14.2`，ESM-only 变更在 0.15 线（仍是 rc），文档与已发布版本不一致。规避：锁死版本并确认其模块格式；长期项目改用 `kb/remotion` 或 `kb/ffmpeg` 模板方案。
2. **ffmpeg 不在 PATH 直接失败**。现象：`spawn ffmpeg ENOENT` / `ffprobe not found`。原因：editly 不自带 ffmpeg，全部调用系统二进制。规避：先跑 `ffmpeg -version` 与 `ffprobe -version`；本机 Homebrew 构建可用（无 libass 不影响 editly，文字由 Canvas 渲染）。
3. **画幅与尺寸被首个素材决定**。现象：输出尺寸/帧率与规格不符。原因：不加 `--fast` 时默认采用第一段输入的 width/height/fps。规避：在 spec 中显式写 `width` / `height` / `fps`，或统一加 `--fast`。
4. **canvas / gl 层的原生依赖**。现象：用 `gl` 层或自定义 canvas 时 node-gyp 编译失败、运行时报 `headless-gl` 错误。原因：依赖原生模块，需要系统图形库与匹配的 Node ABI。规避：优先用 title / image / video 层；必须用 gl 时按 README 安装系统依赖并固定 Node 版本。

## 适用 / 不适用

- 适用：图文卡片、片头片尾、相册式幻灯片、固定版式的批量短视频、快速把多段素材拼成成片。
- 不适用：需要长期维护与复杂交互的项目（改用 `kb/remotion`）；多轨精剪（改用 NLE / `kb/blender-vse`）；纯转码与切片（改用 `kb/ffmpeg`）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：轻量模板类 SOP 的 S4 拼片、S7 标题卡、S9 转场、S10 出片；批量换文案场景可直接复用 spec。
- 关联条目：`kb/remotion`（声明式渲染的活跃替代）、`kb/ffmpeg`（底层与后处理）、`kb/moviepy`（Python 侧同类方案）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / M5 / Node 26.12.0 / ffmpeg 9.0.2 | `which editly` | 本机未安装；示例未执行，安装方式与 CLI 按官方 README 核验 |
| 2026-11-03 | npm / GitHub | 查版本与活跃度 | npm latest `0.14.2`；GitHub release `v0.15.0-rc.1`（2025-01-19）；最后提交 2025-05-12 [事实] |

## 来源

1. [Editly GitHub 仓库](https://github.com/mifi/editly)（访问 2026-11-03）：MIT、TypeScript；release `v0.15.0-rc.1`（2025-01-19），最后提交 2025-05-12
2. [Editly README](https://github.com/mifi/editly#readme)（访问 2026-11-03）：安装 `npm i -g editly`、JSON5 spec、CLI 参数、ESM-only 说明
3. [npm editly](https://www.npmjs.com/package/editly)（访问 2026-11-03）：npm latest `0.14.2`，MIT
4. 本机实测：`node -v`（26.12.0）、`ffmpeg -version`（9.0.2）（2026-11-03）
