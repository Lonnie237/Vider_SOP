---
id: sop/long-tutorial
title: "教程长视频 · 录屏 + 讲解的结构化 SOP"
type: sop
video_type: "教程长视频"
duration: "5–30min"
aspect: "16:9"
platforms: [B站, YouTube, 视频号]
difficulty: 中
tools: [OBS Studio, DaVinci Resolve, 剪映专业版, FFmpeg, Pillow]
status: 可用
updated: 2026-11-03
owner: sop-long
---

# 教程长视频 · SOP

> 读者：第一次做软件教学 / 知识课程长视频的人或执行 Agent。目标：录屏清晰、步骤可跟随、章节可检索，交付参数一次到位。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 软件操作、配置、编程、表格等「跟着做」的教学 | 纯观点 / 经验口播：用 `sop/short-oral-knowledge` |
| 有屏幕操作可录制、有人声讲解的 5–30min 内容 | 产品发布 / 品牌宣传：用 `sop/long-promo` |
| 需要章节、步骤标识、可检索的知识内容 | 多人对谈 / 播客：用 `sop/long-interview-podcast` |
| 单集课程：课程拆集后逐集套用本 SOP | 超过 30min 的整段：先拆集，不要硬塞进一条 |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 / 画幅 | 1920×1080（16:9） | 4K 母版另存；竖屏切片 1080×1920 |
| 帧率 | 30 fps 恒定（CFR） | 录屏可 60fps 采集，交付统一转 30fps |
| 视频编码 | H.264 High，VBR 平均 9Mbps / 峰值 12Mbps（区间 6–12Mbps） | 母版 ProRes 422 |
| 音频 | AAC 48kHz 立体声 192kbps，响度 -16 LUFS（±1） | 竖屏切片 -14 LUFS |
| 字幕 | 外挂 SRT（与视频同名）+ 章节标记 | 需烧录时走 NLE 或 Pillow overlay（本机 FFmpeg 无 libass） |
| 封装 / 命名 | .mp4（`+faststart`）；`<项目>-ep<两位序号>-v<版本>-<YYYYMMDD>.mp4` | 客户交付附 ProRes 母版 |
| 时长 | 5–30min；单集建议 8–18min | 30min 以上按章节拆集 |

## 前置准备

- 素材：录屏主画面 + 人声 + 必要 B-roll / 截图 + 可商用音乐。
- 工具：OBS Studio 录屏；DaVinci Resolve 或剪映专业版剪辑；FFmpeg 9.0.2 + Pillow 转码与字幕烧录（本机已装，见 [本机环境](../knowledge/环境/environment-local.md)）。
- 录制前系统设置：1920×1080、缩放 125%–150%、光标放大、关闭通知与自动更新、隐藏个人账号信息。
- 素材目录 `01_录屏/ 02_截图/ 03_音频/ 04_音乐/ 05_工程/ 06_导出/`，文件名 `<日期>-<步骤号>-<内容>.mkv`；立项填 [项目Brief](../templates/项目Brief.md)，步骤表用 [分镜表](../templates/分镜表.md)。

## 流程总览（阶段 × 产出 × 时间预算）

以 **10min 成片** 估算，同项目按比例缩放。

| 阶段 | 产出 | 时间预算 |
|---|---|---|
| S0–S1 选题 / 脚本 | 选题卡 + 章节表 + 逐步操作清单 + 录制清单 | 2h |
| S2 录屏采集 | 分段录屏 + 人声 | 2h（含重录） |
| S3 素材整理 | 场记：步骤号 ↔ 文件 ↔ 时间点 | 0.5h |
| S4 粗剪 | 按章节表拼出完整流程 | 2h |
| S5 精剪 | 步骤标识 + 缩放 / 高亮 + 节奏 | 2h |
| S6 声音 | 降噪、均衡、压缩、响度 | 1h |
| S7 字幕 | SRT + 章节时间戳 | 1.5h |
| S8–S9 调色 / 包装 | 录屏校正 + 章节卡 + 步骤角标 | 1.5h |
| S10 导出 | 交付文件 + 章节 + 分段文件 | 0.3h |
| S11 QC | QC 记录 + 问题清单 | 0.5h |

## 分阶段操作

### S0–S1 选题、脚本与章节表

- 判断标准：观众学完能**独立完成一个具体任务**；写不出一句「学完你能做 X」就换选题。
- 章节结构（5–9 章，每章 1–4min）：
  1. 0:00–0:30 钩子：先演示最终效果，再说「本集 3 个步骤」。
  2. 0:30–1:00 目录：报章节时间点（与最终章节时间戳一致）。
  3. 每章按「目标 → 操作 → 验证」三段式：先说要达到什么状态，再演示，最后给出确认结果。
  4. 收尾：操作清单回顾 + 下一步 / 资料获取方式。
- 输出：章节表（标题 + 预估时间点 + 步骤号）、逐步操作清单、录制清单。
- 返工点：脚本缺「验证」一步，观众不知道自己是否做对，后期补录成本最高。

### S2 录屏采集

- 分辨率：以 1920×1080 / 16:9 为基准窗口；必须 4K 录制时，交付前统一缩到 1080p，不混用多分辨率素材。
- 光标可见性：系统设置放大光标；OBS 开启光标捕获；剪辑时加点击高亮 / 光标追踪，录屏本身不加动态模糊。
- 录制参数（OBS）：`1920×1080`、`30fps`（手速演示用 60fps）、`x264`、`CQP 18` 或 `CRF 18`、封装 `mkv`（崩溃可恢复），录完无损转 mp4：

```bash
# MKV → MP4 无损重封装（不重编码，秒级完成）
ffmpeg -i step-01.mkv -c copy step-01.mp4
```

- 分段录制：一个操作步骤一段，命名带步骤号；讲错只重录该段。每步开头停顿 0.5s 再操作；输入文字先展示结果再回放过程。
- 常见坑：窗口小于录制区域出黑边；字体小于 18px@1080p 看不清；通知弹窗泄露隐私。

### S3–S4 素材整理与粗剪

- 场记表记录「步骤号 ↔ 文件 ↔ 时间点」；录屏与配音分开录时，先按步骤号搭时间线骨架再逐段贴配音。
- 粗剪只做结构：每步保留「讲目标 → 操作 → 验证」，删等待加载、重复操作、口误停顿；每步开头留 0.3–0.5s 静帧。
- 粗剪完成标准：不看字幕也能跟上操作；时长与章节表偏差 < 20%。

### S5 精剪（步骤标识 / 缩放 / 光标）

- 单镜头：演示操作 3–8s，静态讲解 2–5s；不要连续 10s 以上无变化画面。
- 步骤标识：左上角常驻「步骤 2/5」；关键操作放大 120%–150% 加圆角边框；每章开头章节卡 0.8–1.2s。
- 无效操作（进度条、加载、拖拽）加速 1.2–1.5×，关键操作保持 1×；加速段人声做音调补偿或静音。
- 转场：硬切为主，缩放定位用 0.2s 缓动，不用花哨转场。
- 常见返工点：缩放后画面糊（源分辨率不足）、标识挡操作区、加速段字幕没同步缩短。

### S6 声音

- 降噪：轻度降噪 + 高通 80Hz；混响重就重录，别硬拉降噪。动态用压缩比 3:1、阈值 -18dB；音乐垫底 -24 ~ -20 LUFS。
- 响度：成片 -16 LUFS（±1），真峰值 ≤ -1.5 dBTP；要求精确时用两遍法（见 S10）。

### S7 字幕

- 字体 / 字号：无衬线中文字体，42–48px@1080p；单行 ≤ 18 字，最多两行；数字、快捷键、代码保留原文大小写。
- 安全区：底部留 8%–10%；平台 UI 会遮挡底部，横屏也按此留。
- 断句按语义，不以标点为单位；外挂 SRT 用 UTF-8，文件名与视频一致。烧录（平台要求时）：本机 FFmpeg 无 libass，**不能用 `subtitles` 滤镜**；走 NLE 烧录，或 Pillow 渲染透明 PNG 序列 + `overlay` 合成。以下脚本最小骨架（Pillow 11.3.0 实测）：

```python
# render_subs.py：cues=[(start,end,text)]，按 30fps 生成全画幅透明 PNG 序列
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
cues = [(0.0, 3.0, "第一步：打开素材目录"), (3.0, 6.0, "第二步：建立代理文件")]
font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 52, index=0)
out = Path("subframes"); out.mkdir(exist_ok=True)
for i in range(300):  # 10s 成片
    t, img = i / FPS, Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for start, end, text in cues:
        if start <= t < end:  # 按 cue 画字幕，可扩展为多行
            b = d.textbbox((0, 0), text, font=font); x, y = (W - (b[2] - b[0])) // 2, int(H * 0.86)
            d.rounded_rectangle([x - 18, y - 18, x + b[2] - b[0] + 18, y + b[3] - b[1] + 18], 12, fill=(0, 0, 0, 150))
            d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    img.save(out / ("%05d.png" % i))
```

```bash
# 透明字幕层叠加；画面只重编码一次，音频直接复制
ffmpeg -y -i master_1080p.mp4 -framerate 30 -i subframes/%05d.png \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a copy out_subbed.mp4
```

### S8–S9 调色与包装

- 一级校正：录屏常见偏冷 / 偏紫，先校白场与对比，不把 UI 颜色调失真；人像画中画与录屏匹配色温；不加风格化 LUT（方法见 `kb/color-grading`）。
- 章节卡：章标题 + 编号停留 0.8–1.2s；进度条常驻；快捷键 / 代码用等宽字体单独贴片。
- 封面单独导出 1920×1080，不用视频第一帧。

### S10 导出

```bash
# 横屏交付：1080p30 / H.264 High / VBR 9M（峰值 12M）/ AAC 192k / -16 LUFS / faststart
ffmpeg -y -i master.mov \
  -c:v libx264 -preset slow -profile:v high -level 4.1 \
  -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart ep01-v1.mp4
```

```bash
# 写章节（MP4 metadata；START/END 单位毫秒，按最终成片对时）
cat > chapters.txt <<'EOF'
;FFMETADATA1
[CHAPTER]
TIMEBASE=1/1000
START=0
END=45000
title=00 开场：本集能解决什么
EOF
ffmpeg -y -i ep01-v1.mp4 -i chapters.txt -map_metadata 1 -codec copy ep01-v1-ch.mp4
```

```bash
# 长视频分段：按章节切成 20min 以内的段；分段 → 合并
ffmpeg -y -ss 0 -to 1200 -i ep01-v1-ch.mp4 -c copy part1.mp4
printf "file 'part1.mp4'\nfile 'part2.mp4'\n" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy ep01_full.mp4
```

- `-c copy` 按最近关键帧切，段间可能重复 1–2s；要求帧级精确时去掉 `-c copy` 重编码该段。
- 响度两遍法（要求精确 -16 LUFS）：先 `ffmpeg -i master.mov -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -` 测量，再把 `input_i / input_lra / input_tp / input_thresh / target_offset` 填入第二遍的 `measured_*` 并加 `linear=true`。

### S11 QC

按 [QC 清单](../templates/QC清单.md) 逐项过，并用 ffprobe 核对分辨率 / 码率 / 帧率 / 采样率 / 声道。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 录屏采集 | 分辨率 / 帧率 / 编码 | 1920×1080 / 30fps（或 60fps） / x264 CQP 18，MKV 封装 |
| 交付视频 / 音频 | 编码 / 码率 / 响度 | H.264 High VBR 9M（峰值 12M）+ AAC 48kHz 192k / -16 LUFS |
| 字幕 / 章节 | 字号 / 章节数 | 42–48px，单行 ≤18 字；5–9 章，每章 1–4min |
| 步骤标识 | 停留 | 常驻角标；章节卡 0.8–1.2s |

## 质量门禁（QC）

- [ ] 分辨率 / 帧率 / 码率 / 音频规格与交付规格一致（ffprobe 核对）
- [ ] 前 30s 给「学完能做到什么」与最终效果；章节可跳转、时间戳对齐
- [ ] 每一步都有「目标 → 操作 → 验证」；关键操作有缩放 / 高亮，角标不挡操作区
- [ ] 光标全程可见，无通知弹窗、无隐私信息
- [ ] 字幕同步（偏差 ≤0.3s），无错别字，快捷键大小写正确
- [ ] 响度 -16 LUFS（±1），无爆音、无底噪；无黑帧、无未授权素材 / 字体可商用
- [ ] 封面与标题就绪；上传后可播放、章节生效

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 缩放后画面糊 | 源分辨率 = 交付分辨率，放大即插值 | 用 2560×1440 或 4K 录屏，交付缩到 1080p |
| 光标看不见 / 找不到点击位置 | 系统光标小、未开光标捕获 | 放大系统光标，点击处加高亮 / 光标追踪，操作后停顿 0.3s |
| 字幕与操作不同步 | 加速、剪等待段后字幕没缩 | 先定剪再生成字幕，按最终时间线校对 |
| 导出后章节丢失 | 剪辑软件导出未写章节 metadata | 导出后用 ffmpeg `-map_metadata` 写入章节 |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 转码 / 响度 / 章节 | FFmpeg 一条命令或脚本 | `kb/ffmpeg`、`kb/transcode-delivery` |
| 字幕生成 | 转写 + 断句 + 校对 | `kb/whisperx`（本机未装，需先装） |
| 字幕烧录 | Pillow PNG 序列 + overlay | 本 SOP S7、`kb/ffmpeg` |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| B站 | 16:9、分P / 合集；简介写章节时间戳；B站会对上传视频二次编码，码率阈值以创作中心当期规则为准 [待确认] |
| YouTube | 16:9；官方建议 1080p 30fps SDR 上传 8Mbps（高帧率 12Mbps），与 6–12Mbps 区间吻合；章节写简介（0:00 起、至少 3 章） |
| 抖音 / 视频号 | 9:16 竖屏切片：1080×1920 / 30fps / 8–16Mbps / -14 LUFS；抽 1–3 个高价值步骤重剪 30–90s，字幕 64–72px |
| 客户交付 | ProRes 422 母版 + H.264 审片版 + SRT + 章节 txt + 封面；命名带版本与日期，不写 final |

## 复盘与改进

- 实测记录（2026-11-03，ffmpeg 9.0.2 / Python 3.9.6 / Pillow 11.3.0）：1080p30 VBR 9M 导出 10s 样片 1.86s（合成画面，实拍更慢）；Pillow 字幕 overlay 300 帧合成通过；章节 metadata 可被 ffprobe 读出；`-c copy` 分段 + concat 回读 10.09s（关键帧切点导致偏差）。
- 待优化：转写工具未装，字幕依赖人工或平台转写；4K 多机位教程的代理剪辑流程未测。

## 关联条目

- 方法论：`kb/narrative-structure`、`kb/sound-design`、`kb/color-grading`
- 工作流 / 库：`kb/transcode-delivery`、`kb/ffmpeg`、`kb/opentimelineio`（步骤表 / 剪辑决策表交接）
- 技能：`video-sop-selector`

## 来源

1. 本机实测命令（2026-11-03）：`ffmpeg -version` → 9.0.2；`ffmpeg -hide_banner -h filter=subtitles` → Unknown filter（无 libass）；Pillow 11.3.0；Python 3.9.6。
2. [本机环境基线](../knowledge/环境/environment-local.md)（访问 2026-11-03）。
3. [YouTube 推荐上传编码设置](https://support.google.com/youtube/answer/1722171)（访问 2026-11-03）：1080p 标准帧率 8Mbps、高帧率 12Mbps。
4. [FFmpeg loudnorm 文档](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)、[FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）。
