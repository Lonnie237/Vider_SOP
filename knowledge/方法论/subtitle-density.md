---
id: kb/subtitle-density
title: 字幕与信息密度 · 在可读前提下承载信息
type: 方法论
domain: [字幕, 剪辑, 交付]
status: 可用
confidence: 中
tags: [字幕, 信息密度, CPS, 安全区, Pillow, 烧录]
related: [kb/hooks-retention, kb/pacing-beat, kb/sound-design, kb/platform-specs, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 字幕与信息密度 · 在可读前提下承载信息

> 本机 ffmpeg 9.0.2 未编译 libass / freetype，`subtitles` / `drawtext` 都不可用；本文的烧录方案以 Pillow 渲染 PNG + `overlay` 为主，NLE 为备选。安全区数值随 App 版本变化，上线前用真机确认。

## 一句话定位

决定「一屏放多少字、放多久、放在哪」，目标是观众能边看画面边读完，不遮挡主体与平台 UI。用在 S7 字幕与图文包装；判断标准是 CPS ≤ 6、单行 ≤ 16 字（竖屏）、所有文字落在安全区内。

## 适用场景

- 适用：口播知识、教程、直播切片、Vlog、产品宣传片；需要「静音也能看懂」的成片。
- 不适用：纯音乐混剪（只留标题 / 花字，不做逐句字幕）；已用平台自动字幕且不打算精修的批量内容。

## 原理与判断标准

- 可读性由三个量决定：每秒字数（CPS）、单行字数、显示时长。中文阅读速度约 300–500 字/分钟，即 5–8 字/秒 [推断]；视频要同时看画面，留余量后取 4–6 字/秒。
- 信息密度 = 每屏信息点 / 时长。字幕只承载「听不清 / 需强调 / 不能外放」的信息，不是把口播全文贴上去。
- 什么算好：CPS 4–6；单行 ≤ 16 字（9:16）/ ≤ 20 字（16:9）；每屏 ≤ 2 行；单条显示 0.8–6s；全部文字在安全区内；样式统一。
- 什么算坏：一行 30 字；CPS > 8；字幕压住下巴或平台底部按钮；字号 < 屏宽 4.5%；描边太细，亮背景上糊成一片。

## 本机限制与替代路径

- [实测] 2026-11-03，ffmpeg 9.0.2：`ffmpeg -filters | grep -qw subtitles` 返回非 0；`drawtext` 同样缺失，无法用滤镜烧录。
- 探测技巧：`ffmpeg -h filter=subtitles` 即使滤镜不存在也返回退出码 0（只打印 Unknown filter），不能作为判断依据；详见 [本机环境](../环境/environment-local.md)。
- 方案 A（推荐，可批量）：Pillow 渲染透明 PNG 字幕层，再用 `overlay` 合成。本机 Pillow 11.3.0、numpy 2.0.2 可用。
- 方案 B：换用带 libass 的 FFmpeg 构建，或 NLE / Remotion / 剪映内烧录；FFmpeg 只负责转码。
- 方案 C：外挂 SRT 交给平台自动字幕；适合口播，但样式不可控。

## 可操作步骤

1. 转写：本机无 whisper / yt-dlp，用平台自动字幕、剪映「识别字幕」或人工听写，导出 SRT。产出：`subs.srt`。
2. 断句：一句一行，按语义断；竖屏每行 ≤ 16 字，横屏 ≤ 20 字，每屏最多 2 行。产出：清洗后的 SRT。
3. CPS 校验：跑下面脚本，把 OVER 的行拆短或延长显示时间，直到 `over_limit: 0`。产出：合规 SRT。
4. 渲染 PNG：按画幅与安全区生成每条字幕的透明 PNG，一条一图。产出：`cap_0001.png` …
5. 合成：`overlay` + `enable='between(t,起,止)'` 逐条叠加；字幕 ≤ 30 条可直接链式 overlay，更多条建议走 NLE。产出：`subbed.mp4`。
6. 抽帧检查：每条字幕中点抽帧看位置、字号、遮挡；再用手机竖屏预览一遍。

CPS 校验脚本（[实测] 2026-11-03，Python 3.9.6；阈值 6 时 3 条示例 0 条超限，阈值 3 时 2 条标 OVER）：

```bash
python3 cps_check.py subs.srt 6
```

```python
import sys
def to_sec(t):
    h, m, s, ms = t.replace(',', ':').split(':')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
cues, cur = [], []
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.rstrip()
    if not line:
        if cur: cues.append(cur); cur = []
        continue
    cur.append(line)
if cur: cues.append(cur)
limit = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
bad = 0
for c in cues:
    parts = c[1].split(' --> ')
    if len(parts) != 2: continue
    dur = to_sec(parts[1]) - to_sec(parts[0])
    text = ''.join(c[2:]).replace(' ', '')
    cps = len(text)/dur if dur > 0 else 999
    bad += cps > limit
    print(f"{'OVER' if cps > limit else 'ok  '} cps={cps:4.1f} dur={dur:4.2f}s chars={len(text):2d} | {text[:18]}")
print('over_limit:', bad)
```

Pillow 渲染字幕层（[实测] 2026-11-03，Pillow 11.3.0；同结构脚本在 1080×1920 上生成 74 KB PNG，并成功 overlay 编码）：

```python
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
font = ImageFont.truetype(FONT, 64, index=1)
lines = ["第一屏字幕内容", "第二行不超十六字"]
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
y = H - 320 - 84 * len(lines)
for line in lines:
    d.text((90, y), line, font=font, fill=(255, 255, 255, 255),
           stroke_width=4, stroke_fill=(0, 0, 0, 255))
    y += 84
img.save("cap_0001.png")
```

合成命令（[实测] 2026-11-03：两条 PNG 按时间叠加，输出 1080×1920 / 30fps / 5.000s）：

```bash
ffmpeg -y -hide_banner -i base.mp4 -i cap_0001.png -i cap_0002.png -filter_complex "[0:v][1:v]overlay=0:0:enable='between(t,0,2.5)'[v1];[v1][2:v]overlay=0:0:enable='between(t,2.5,5)'[v]" -map "[v]" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy subbed.mp4
```

## 参数与阈值

| 参数 | 9:16 竖屏（1080×1920） | 16:9 横屏（1920×1080） | 依据 |
|---|---|---|---|
| 主字幕字号 | 56–72px（推荐 64） | 36–48px（推荐 40） | 竖屏 ≈ 屏宽 5.2%–6.7%；横屏 ≈ 屏高 3.3%–4.4% [推断] |
| 次级字号 | ≥ 主字号 75% | ≥ 主字号 75% | [推断] 层级要一眼可分 |
| 单行字数 | ≤ 16 字 | ≤ 20 字 | [推断] 超过则行过长、扫视困难 |
| 每屏行数 | ≤ 2 行 | ≤ 2 行 | [推断] 3 行会压画面 |
| 阅读速度 CPS | 4–6（硬上限 7） | 4–6（硬上限 7） | [推断] 中文字速留余量 |
| 单条时长 | 0.8–6s | 0.8–6s | [推断] 低于 0.8s 读不完 |
| 行距 | 1.3–1.4 倍字号 | 同 | [推断] |
| 描边 / 阴影 | 3–5px + 1 层阴影 | 3–5px + 1 层阴影 | 亮背景可读性 |
| 底部安全区 | ≥ 320px | ≥ 120px | [推断] 平台 UI 会变，真机确认 |
| 顶部安全区 | ≥ 240px | ≥ 80px | [推断] |
| 左右边距 | ≥ 90px | ≥ 96px | [推断] |
| 字幕与口播对齐 | ≤ ±2 帧（67ms@30fps） | 同 | [推断] 超过则有「声画不同步」感 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 一行 30 字 | 观众读完已切镜 | 拆成 2 行、每行 ≤ 16 字，或拆成两条字幕 |
| CPS 8 以上 | 读不完，等于没字幕 | 延长显示或删字；口播稿先压短 |
| 字幕压在底部按钮上 | 平台 UI 遮挡，关键信息丢失 | 底部安全区 ≥ 320px（竖屏），抽真机帧核对 |
| 字号 < 屏宽 4.5% | 手机小屏不可读 | 主字幕 ≥ 56px（1080 宽） |
| 描边 1px 或无描边 | 白墙 / 天空背景直接消失 | 3–5px 描边 + 阴影，或加半透明底条 |
| 逐字弹出 / 花字过多 | 阅读被打断，信息密度反而下降 | 整句出现；花字只用于关键词 |
| 双语字幕各两行 | 四行占掉半屏 | 主语言 1 行 + 次语言 1 行，或只留主语言 |

## 验证方式

- CPS 校验：`python3 cps_check.py subs.srt 6` 输出 `over_limit: 0`。
- 抽帧：`ffmpeg -v error -ss 1.2 -i subbed.mp4 -frames:v 1 check1.png`，每 2–3 秒抽一帧检查位置与遮挡。
- 安全区：把抽帧叠到平台预览截图（或真机录屏）上比对底部按钮、右侧图标位置。
- 规格：`ffprobe -v error -show_entries stream=width,height,r_frame_rate -show_entries format=duration -of json subbed.mp4`，确认画幅与时长。
- 失败信号：自己看一遍需要暂停才能读完；字幕被平台 UI 盖住；同一句出现两种断句；字幕与口播差半拍。

## 关联条目

- 方法论：[钩子与留存](hooks-retention.md)、[节奏与卡点](pacing-beat.md)、[声音设计](sound-design.md)
- 工作流：`kb/platform-specs`（平台 UI 安全区差异，下一轮产出）
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-oral-knowledge`、`sop/long-tutorial`；技能 `subtitle-pipeline`

## 来源

1. 本机实测（2026-11-03，ffmpeg 9.0.2，Python 3.9.6，Pillow 11.3.0）：`ffmpeg -filters | grep -qw subtitles` 返回非 0；Pillow 生成 1080×1920 透明 PNG（74 KB）并用 overlay 输出 5.000s / 30fps 成片；CPS 脚本在示例 SRT 上按阈值 6 / 3 分别报 0 / 2 条超限。
2. [FFmpeg overlay 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#overlay)（访问 2026-11-03）
3. [Pillow ImageDraw 文档](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)（访问 2026-11-03）
4. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）：无 libass / drawtext 的实测依据。
5. [视频号助手 · 素材要求](https://findeross.weixin.qq.com/cgi-bin/mmfindernodelivecrmwebbroker-bin/helper-center/pages/DCbKPGzZkvVHcIr6)（访问 2026-11-03）：画幅比例要求。
