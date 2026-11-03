---
id: sop/short-oral-knowledge
title: "口播知识 · 竖屏知识口播 SOP（30–180s）"
type: sop
video_type: "口播知识"
duration: "30–180s"
aspect: "9:16"
platforms: [抖音, 视频号, 小红书, YouTube Shorts]
difficulty: 中
tools: [手机或相机, 无线领夹麦, Premiere Pro / DaVinci Resolve / 剪映专业版, ffmpeg, Pillow]
status: 可用
updated: 2026-11-03
owner: sop-short
---

# 口播知识 · 竖屏知识口播 SOP

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 单人口播讲清一个观点 / 方法 / 判断，成片 30–180s | 需要双人对话、追问 → `sop/long-interview-podcast` |
| 已有文字稿，需要竖屏成片 + 字幕 | 素材驱动、无真人出镜 → `sop/short-montage-beat` |
| 科普、职场、效率、知识付费账号日常更新 | 超过 3 分钟的课程 → `sop/long-tutorial` |
| 一人一机一支麦即可开工 | 需要大量外景与生活素材 → [Vlog](short-vlog.md) |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 / 画幅 | 1080×1920（9:16） | 1920×1080 横版（B 站 / YouTube 长版，响度改 -16 LUFS） |
| 帧率 | 30 fps 恒定 | 素材 60 fps 可保留，交付统一 30 fps |
| 视频编码 / 码率 | H.264 High、level 4.2、VBR 8–16 Mbps（目标 12 Mbps） | 上限 16 Mbps，再高对信息流无收益 |
| 音频 | AAC 48 kHz 立体声 192 kbps、-14 LUFS ±1、真峰值 ≤ -1.5 dBTP | 平台自动归一后仍以 -14 为准 |
| 字幕 | 烧录（Pillow overlay 或 NLE） | 平台自动字幕可用时改外挂 SRT |
| 封装 / 命名 | .mp4 / `oral-<主题>-<时长>-v<n>-<日期>.mp4` | 母版另存 ProRes 422 单独归档 |
| 时长 | 30–180s，钩子在前 3s | 30–45s 是信息流最优区间 |

## 前置准备

- 素材：文字稿 1 份（按 4.5 字/秒 折算字数）、A-roll 3–5 条 take、截图或 B-roll 6–12 个、可商用音乐 1 首。
- 工具：手机后摄或相机 + 无线领夹麦；NLE 三选一（Premiere Pro / DaVinci Resolve / 剪映专业版）；本机 ffmpeg 9.0.2 + Pillow（无 libass，见 [本机环境](../knowledge/环境/environment-local.md)）。
- 素材整理：按 `素材/<日期>_<主题>/{A-roll,B-roll,audio,music}` 建目录，文件名 `<日期>-<场景>-<序号>.mp4`；立项用 [项目 Brief](../templates/项目Brief.md)，拆镜用 [分镜表](../templates/分镜表.md)。

## 流程总览（阶段 × 产出 × 时间预算）

> 基准：3 分钟（180s）成片、单人操作、1 轮拍摄 3–5 条 take。换算：目标时长 T 秒 → 可变工时 ×（T/180），固定工时不变；总预算 = 固定 + 可变 ×（T/180）。固定 80 min、可变 170 min；例：60s 片 = 80 + 170/3 ≈ 137 min ≈ 2h20m。

| 阶段 | 产出 | 时间预算（180s 基准） | 缩放 | 负责人 |
|---|---|---|---|---|
| S0 选题与角度 | 选题卡 | 15 min | 固定 | 编导 |
| S1 脚本与字数预算 | 口播稿 | 40 min | 线性 | 编导 |
| S2 提词器与机位 | 可拍状态 | 15 min | 固定 | 编导 + 摄像 |
| S3 拍摄 | A-roll 素材 | 25 min | 固定 | 出镜人 |
| S4 素材整理与转写 | 转写稿 | 10 min | 固定 | 剪辑 |
| S5 粗剪 | 结构版 | 30 min | 线性 | 剪辑 |
| S6 精剪 | 节奏版 | 35 min | 线性 | 剪辑 |
| S7 声音 | 混音版 | 15 min | 线性 | 剪辑 |
| S8 字幕 | SRT + 烧录版 | 20 min | 线性 | 剪辑 |
| S9 调色与包装 | 包装版 | 30 min | 线性 | 剪辑 |
| S10 导出 | 交付文件 | 5 min | 固定 | 剪辑 |
| S11 QC | QC 记录 | 10 min | 固定 | 编导 |
| 合计 | — | 250 min ≈ 4h10m | — | — |

## 分阶段操作

### S0 选题与角度

- 判断标准：能一句话回答「看完这 60 秒，观众会知道什么 / 会做什么」，且评论区能复述。
- 输出：选题卡写清「目标受众 / 一个核心结论 / 3 个论据 / CTA」；题目太大就拆成系列。

### S1 脚本与字数预算

- 语速换算：按 4.5 字/秒 规划（[分镜表](../templates/分镜表.md) 约定中文口播 4–5 字/秒，取中间值留 10% 余量）；录制 4.0–5.0 字/秒 可用，低于 3.5 显拖。
- 稿子要求：每句 ≤25 字、能一口气读完；删掉「大家好」「今天我们来聊聊」，输出口播稿 + [分镜表](../templates/分镜表.md)。

| 目标时长 | 规划字数（×4.5） | 上限（5 字/秒） |
|---|---|---|
| 30s | 135 | 150 |
| 60s | 270 | 300 |
| 90s | 405 | 450 |
| 180s | 810 | 900 |

- 结构模板：钩子 0–3s（≤13 字，直接抛结论或冲突）→ 承诺 3–8s（「看完你能……」）→ 主体 3 个论据、每 15–20s 一个信息峰值 → 收尾 5–8s（一句话总结 + CTA）。

### S2 提词器与机位

- 提词器：字号 60–72 px（6.7 寸手机），行宽 ≤15 字；滚动速度按「30 字 / 10 秒」校准；视距 0.8–1.2 m。
- 机位：镜头与眼睛齐平；胸像景，头顶留 8–12%；眼睛落在画面上 1/3 线；下 1/5 留白给字幕。
- 灯光与收音：主光 45° 侧前方 + 柔光，避免顶光；领夹麦距嘴 15–20 cm，先录 5 秒环境声供降噪。

### S3 拍摄

- 3–5 条 take，每条开头多录 2 秒、结尾停 1 秒；每段开头拍手一次制造波形尖峰，便于音画对齐。
- 录音峰值 -12 ~ -6 dBFS、48 kHz / 24 bit；不要用手机内置麦做母版。

### S4 素材整理与转写

- 按前置准备建目录导入，NLE 内按场景分 bin。转写两条路：剪映专业版「文本 → 智能字幕 → 识别字幕」；或云端 ASR，先抽 16 kHz 单声道音频：

```bash
ffmpeg -i take1.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le take1_asr.wav
```

- [待确认] 素材能否上传第三方 ASR 服务，按项目保密要求确认后再选路径。

### S5 粗剪

- 先音后画：按转写稿删口误、重复、长停顿（>0.6s 压到 0.25–0.35s）。

### S6 精剪

- 单镜头 4–10s；每 8–15s 给一次视觉变化（跳剪 punch-in 105–115%、B-roll、花字）。
- 跳剪（jump cut）：同机位剪掉停顿并配 5–8% 缩放变化，避免画面「闪一下」。
- B-roll 覆盖 30–40% 时长，每个观点至少 1 个画面证据；前 3s 最多 2 个镜头。

### S7 声音

- 降噪用 NLE 内置（Premiere「基本声音 → 对话 → 减少杂音」/ DaVinci「Fairlight → Noise Reduction」），强度 30–50%，过头会发闷。
- EQ：高通 80–100 Hz，2–4 kHz 提 1–2 dB，齿音重时 6–8 kHz 压 2–3 dB；压缩 3:1、阈值 -18 dBFS。
- 响度目标 -14 LUFS / 真峰值 -1.5 dBTP；先跑测量，把数值填进 S10 导出命令（本机实测 2026-11-03）：

```bash
ffmpeg -hide_banner -nostats -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | tail -12
```

### S8 字幕

- 断句按语义，单行 ≤12–14 字、最多 2 行；数字与中英文之间加空格；位置固定在底部安全区（≥300 px，字幕底边不低于 y=1620）。
- 路径 B 用 Pillow 渲染 PNG + `overlay`（本机无 libass，已实测）。存为 `srt2png.py`，SRT 每条 cue 先断好 ≤2 行：

```python
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
F, W, H, SZ, MX = '/System/Library/Fonts/Hiragino Sans GB.ttc', 1080, 1920, 64, 13
LH, BT = int(SZ * 1.35), int(H * 0.16)                 # 行高 / 底部安全区
def ts(s):
    h, m, rest = s.split(':'); return int(h) * 3600 + int(m) * 60 + float(rest.replace(',', '.'))
cues = []
for b in Path(sys.argv[2]).read_text(encoding='utf-8').replace(chr(13), '').split(chr(10) * 2):
    l = [x for x in b.split(chr(10)) if x.strip()]
    if len(l) > 2 and '-->' in l[1]:
        a, z = l[1].split('-->')
        cues.append((ts(a), ts(z), ' '.join(l[2:])))
tmp, inp, fc, prev = Path(tempfile.mkdtemp()), [], [], '[0:v]'
for i, (a, z, t) in enumerate(cues):
    ls = [t[k:k + MX] for k in range(0, len(t), MX)]
    if len(ls) > 2:
        sys.exit('字幕超过 2 行，请先在 SRT 断句：' + t)
    im = Image.new('RGBA', (W, LH * len(ls) + 24))
    d, f = ImageDraw.Draw(im), ImageFont.truetype(F, SZ)
    for j, ln in enumerate(ls):
        y = 12 + LH * j + LH // 2
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            d.text((W // 2 + dx, y + dy), ln, font=f, fill=(0, 0, 0, 255), anchor='mm')
        d.text((W // 2, y), ln, font=f, fill=(255, 255, 255, 255), anchor='mm')
    p = tmp / ('c%03d.png' % i); im.save(p)
    inp += ['-loop', '1', '-i', str(p)]
    fc.append("%soverlay=x=0:y=%d:enable='between(t,%.3f,%.3f)'[v%d]" % (prev, H - BT - im.size[1], a, z, i))
    prev = '[v%d]' % i
cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', sys.argv[1]] + inp + [
    '-filter_complex', ';'.join(fc), '-map', prev, '-map', '0:a?',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-c:a', 'copy', '-shortest', '-movflags', '+faststart', sys.argv[3]]
subprocess.run(cmd, check=True)
print('完成', sys.argv[3], len(cues), '条字幕')
```

```bash
python3 srt2png.py cut.mp4 subs.srt cut_sub.mp4
```

### S9 调色与包装

- 一级校正：白平衡 → 曝光 → 对比度，目标 Rec.709；肤色落在矢量示波器肤色线上。
- 标题条前 3s 出现、停留 2–3s，避开字幕区；花字 2–4 个/分钟，只标关键词。

### S10 导出

- NLE 导出设置：H.264、High、1080×1920、30 fps、VBR 2-pass 目标 12 Mbps / 最大 16 Mbps、AAC 192 kbps 48 kHz。
- 命令行（本机实测 2026-11-03：输出 H.264 High / 12.2 Mbps / AAC 48 kHz，退出码 0）：

```bash
ffmpeg -hide_banner -y -i cut_sub.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1" -c:v libx264 -preset slow -profile:v high -level 4.2 -pix_fmt yuv420p -r 30 -b:v 12M -maxrate 16M -bufsize 24M -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart out.mp4
```

- 音频未达标时在 `-c:a aac` 前加 `-af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=...:measured_TP=...:measured_LRA=...:measured_thresh=...:offset=...:linear=true"`，数值取 S7 测量结果。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 语速 | 规划 / 录制区间 | 4.5 字/秒 / 4.0–5.0 字/秒 |
| 字幕 | 字号 / 单行 / 底部安全区 | 60–72 px / ≤13 字 / ≥300 px |
| 声音 | 人声峰值 / 响度 | -12 ~ -6 dBFS / -14 LUFS |

## 质量门禁（QC）

- [ ] 规格：1080×1920 / 30 fps / H.264 High / 8–16 Mbps / AAC 48 kHz 192k / .mp4
- [ ] 时长 30–180s；前 3s 钩子成立（静音播放也能看懂结论）
- [ ] 响度 -14 LUFS ±1、真峰值 ≤ -1.5 dBTP；无爆音、无底噪
- [ ] 字幕 ≤2 行、单行 ≤14 字、无错别字、不出底部安全区
- [ ] 音画同步：口型偏差 ≤40 ms（30 fps 一帧约 33 ms）

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 成片比稿子长 20% | 实际语速慢、停顿多 | 按字数表减 10% 稿量；粗剪压停顿 |
| 字幕压脸或被平台 UI 挡住 | 只按构图没留安全区 | 字幕底边 ≥300 px；上 200 px 不放关键信息 |
| `subtitles` 滤镜报 Unknown filter | 本机 ffmpeg 未编译 libass | 走 Pillow overlay 或 NLE 烧录（S8） |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 响度测量 / 归一 | loudnorm 两遍 | ffmpeg（`kb/ffmpeg`） |
| 字幕渲染烧录 | SRT → PNG → overlay | Pillow + ffmpeg（`kb/ffmpeg`） |
| 规格校验 | ffprobe 输出 JSON 比对 | ffprobe + 脚本 |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| 抖音 | 9:16；前 3s 定生死；开放平台建议 ≥720p、mp4/webm（[事实]，来源 2）；字幕更大更粗 |
| 视频号 | 9:16；官方建议码率 ≥10 Mbps、手机端单文件 ≤2 GB（[事实]，来源 3）；封面按分享卡片设计 |
| 小红书 | 9:16 或 3:4；首帧即封面，标题字 ≥72 px；码率/体积上限 [待确认]，以创作者中心为准 |
| YouTube Shorts | 9:16 或 1:1；2024-10-15 起 ≤3 分钟竖屏/方形自动归为 Shorts（[事实]，来源 4）；建议配英文字幕 |

## 复盘与改进

- 实测记录：2026-11-03 本机以合成源（testsrc2）验证导出链，1080×1920 → H.264 High / 12.2 Mbps / AAC 48 kHz；字幕脚本 2 条 cue 烧录成功；loudnorm 两遍在横屏用例输出 -16.0 LUFS。真实拍摄素材尚未端到端跑通。

## 关联条目

- 方法论 / 工作流（id 由其他 Agent 并行产出，路径就绪后由 Lead 统一改为相对链接）：`kb/hooks-retention`、`kb/subtitle-density`、`kb/sound-design`、`kb/transcode-delivery`
- 工具：`kb/ffmpeg`；模板：[分镜表](../templates/分镜表.md)、[QC 清单](../templates/QC清单.md)、[交付规格](../templates/交付规格.md)
- 同批 SOP：[混剪卡点](short-montage-beat.md)、[直播切片](short-live-clip.md)、[Vlog](short-vlog.md)

## 来源

1. 本机实测（2026-11-03）：`ffmpeg -version` → 9.0.2；2s 1080×1920 合成源导出 → H.264 High / 12.2 Mbps / AAC 48 kHz；Pillow + overlay 烧录 2 条字幕成功。
2. [抖音开放平台 · 上传视频](https://open.douyin.com/platform/resource/docs/openapi/video-management/douyin/create/upload/)（访问 2026-11-03）：建议 ≥720p，支持 mp4/webm。
3. [视频号助手 · 素材要求](https://findeross.weixin.qq.com/cgi-bin/mmfindernodelivecrmwebbroker-bin/helper-center/pages/DCbKPGzZkvVHcIr6)（访问 2026-11-03）：手机端 3s–60 min、≤2 GB，码率建议 ≥10 Mbps。
4. [YouTube Help · 3 分鐘的 Shorts](https://support.google.com/youtube/answer/15424877)（访问 2026-11-03）：2024-10-15 起 ≤3 分钟方形/直式视频归为 Shorts。