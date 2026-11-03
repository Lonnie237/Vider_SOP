---
id: kb/auto-editor
title: "Auto-Editor · 按音量自动去静音的粗剪工具"
type: 工具
domain: [素材管理, 粗剪, 精剪, 自动化]
status: 可用
confidence: 中
license: "Unlicense（公有领域）"
repo: "https://github.com/WyattBlue/auto-editor"
docs: "https://auto-editor.com/"
language: Nim
platform: [macOS, Linux, Windows]
tags: [auto-editor, 去静音, 粗剪, 口播, 播客, 自动化]
related: [kb/ffmpeg, kb/opentimelineio, kb/environment-local]
updated: 2026-11-03
owner: lib-scout
---

# Auto-Editor · 按音量自动去静音的粗剪工具

## 一句话定位

分析音频响度（或画面运动、字幕）自动找出「死空气」，把长素材压成紧凑初剪；主要服务 S3 素材粗筛与 S4 粗剪，是口播、访谈、播客、课程录屏的第一道工序，产出的时间线可交给 NLE 继续精剪。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 自动切掉静音 / 停顿，大幅缩短初剪时间 | 理解语义，判断哪句话该留（只按阈值） |
| 按响度、运动、字幕多种方法组合判定 | 处理音乐卡点、复杂转场与调色 |
| 导出 Premier / Resolve / FCP / ShotCut / Kdenlive 时间线 | 替代 NLE 做精剪与多轨编排 |
| 命令行批处理，可脚本化 | 保留原片所有音画细节（默认会重编码） |

## 核心能力

- 自动判定：默认 `--edit audio:threshold=0.04,stream=all`，也可用 dB（`audio:-19dB`）或画面运动（`motion:threshold=0.02`）。
- 组合条件：`--edit "(or audio:0.03 motion:0.06)"`，多轨可分别设参。
- 留白控制：`--margin 0.2sec`（默认 0.2s），让切口不突兀。
- 时间线导出：`--export premiere | resolve | final-cut-pro | shotcut | kdenlive | clip-sequence`。
- 标签体系：`--edit:2` / `--when:2` 可给片段打多类标签并做不同动作（如「保留语音 + 加速高音量段」）。

## 安装 / 获取

macOS（Homebrew，推荐）：

```bash
brew install auto-editor
auto-editor --version      # 期望 31.x；若为 29.x 说明装到了旧 pip 包
```

官方二进制（三平台，版本最全）：从 [GitHub Releases](https://github.com/WyattBlue/auto-editor/releases) 下载对应平台文件，改名 `auto-editor`，`chmod +x` 后放入 PATH。

Linux：Arch 用 `yay -S auto-editor`，或 Homebrew for Linux；apt 源版本很旧。

**不要用 pip 安装 CLI**：官方安装页明确「the auto-editor cli is no longer being published on pip」，PyPI 上停留在 `29.3.1`（旧 Python 实现版本线），与当前 31.x 文档不一致。

前提：官方二进制与 Homebrew 包自带所需 FFmpeg 组件；从源码构建需 Nim / nimble / cmake / meson / ninja 并执行 `nimble makeff`。

## 最小可用示例

```bash
# 1) 口播粗剪：切掉静音，默认 0.2s 余量，输出到指定文件
auto-editor input.mp4 -o out.mp4

# 2) 自定义阈值：只保留高于 -19dB 的片段，前后留 0.3s
auto-editor input.mp4 --edit audio:-19dB --margin 0.3s -o out.mp4

# 3) 只导出时间线给 Premiere，不渲染（快，适合先看切点）
auto-editor input.mp4 --export premiere      # 生成 input_ALTERED.xml

# 4) 导出每段 clip 的清单，便于后续用 FFmpeg 精确切
auto-editor input.mp4 --export clip-sequence
```

预期结果：命令 1 生成 `out.mp4`（默认不指定 `-o` 时为 `input_ALTERED.mp4`），时长明显短于原片；命令 3 只产出 XML，不重新编码。

Python 侧调用（当前版本为 Nim CLI，官方不再提供新版 Python 包，用 subprocess 编排）：

```python
import subprocess

subprocess.run(
    ["auto-editor", "input.mp4", "-o", "out.mp4", "--margin", "0.2s"],
    check=True,
)
```

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 长素材初剪从数小时压到几分钟 | 阈值法不懂语义，音乐与噪声易误判 |
| 开源许可宽松（Unlicense） | pip 安装得到旧版，与文档不符 |
| 时间线可导出到主流 NLE | 默认重编码整片，长素材耗时长、占空间 |

1. **pip 装到旧版，命令与文档对不上**。现象：`pip install auto-editor` 后 `--version` 显示 29.x，官网 31.x 的新参数报未知选项。原因：官方已停止通过 pip 发布 CLI，PyPI 停在 `29.3.1`；31.x 只走 Homebrew / GitHub 二进制 / AUR。规避：用 `brew install auto-editor` 或下载官方二进制，装完先 `auto-editor --version` 核对。
2. **音乐 / 环境音导致误判**。现象：整段音乐被当语音保留，或语速慢的语音被切碎。原因：默认按响度阈值判「有声」，持续音乐同样超过阈值，而轻声说话可能低于阈值。规避：口播/访谈用人声分离后再检测；音乐内容改用 `--edit motion`；拿不准先 `--export premiere` 看切点，再决定是否渲染。
3. **默认输出同目录，批量跑爆磁盘**。现象：处理一批 4K 素材后同目录多出等量 `*_ALTERED.mp4`，磁盘告急。原因：默认不覆盖原片、输出与源同目录。规避：批量脚本统一 `-o /work/tmp/xxx.mp4` 指向临时盘，处理完清理。
4. **渲染耗时被低估**。现象：1 小时访谈跑 30 分钟以上。原因：默认动作是完整重编码，不是只切点。规避：先 `--export` 出时间线确认，最终渲染可按切点用 `kb/ffmpeg` 的 `-ss/-t` 批量切再拼接，速度更快。

## 适用 / 不适用

- 适用：口播 / 访谈 / 播客 / 课程录屏的静音剔除与初剪、会议回放压缩、需要把切点交给 NLE 的流水线。
- 不适用：音乐卡点混剪（改用 `kb/ffmpeg` + 节拍分析 + 人工）；需要语义判断的剪辑（人工或 ASR 辅助）；需要保留全部原始音画细节时（改用 `--export` + 精确切）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：口播、访谈、播客类 SOP 的 S3 粗筛与 S4 粗剪；产出 XML 后进入 NLE 精剪（S5）。
- 关联条目：`kb/ffmpeg`（按切点精确切 / 重编码）、`kb/opentimelineio`（时间线交换）、[本机环境基线](../环境/environment-local.md)（本机未安装，需先 `brew install`）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / M5 | `which auto-editor` | 本机未安装；示例命令未在本机执行，安装方式与 CLI 参数按官方文档核验 |
| 2026-11-03 | PyPI / GitHub | 查版本 | GitHub 最新 release `31.8.0`（2026-10-30）；PyPI 仍为 `29.3.1`，官方声明 CLI 不再发布到 pip [事实] |

## 来源

1. [Auto-Editor 官网](https://auto-editor.com/)（访问 2026-11-03）
2. [Auto-Editor 安装页](https://auto-editor.com/installing)（访问 2026-11-03）：Homebrew / 官方二进制 / AUR；pip 停止发布 CLI 的说明
3. [Auto-Editor GitHub 仓库](https://github.com/WyattBlue/auto-editor)（访问 2026-11-03）：Unlicense、Nim；最新 release `31.8.0`（2026-10-30）
4. [Auto-Editor README](https://github.com/WyattBlue/auto-editor/blob/master/README.md)（访问 2026-11-03）：`--margin`、`--edit`、`--export` 用法
5. [PyPI auto-editor](https://pypi.org/project/auto-editor/)（访问 2026-11-03）：最新 PyPI 版本 `29.3.1`，`requires-python>=3.9`
