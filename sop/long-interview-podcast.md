---
id: sop/long-interview-podcast
title: "访谈 / 播客视频 · 多机位同步与长访谈精剪 SOP"
type: sop
video_type: "访谈 / 播客视频"
duration: "20–120min"
aspect: "16:9"
platforms: [YouTube, B站, 视频号]
difficulty: 高
tools: [DaVinci Resolve, FFmpeg, 转写工具, OpenTimelineIO, Pillow]
status: 可用
updated: 2026-11-03
owner: sop-long
---

# 访谈 / 播客视频 · SOP

> 读者：第一次做双人 / 多人对谈长视频的人或执行 Agent。目标：多机位不跑偏、长访谈剪得下去、观点可检索，交付一次过平台。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 双人 / 多人对谈、播客视频化、客户访谈、圆桌 | 单人软件教学：用 `sop/long-tutorial` |
| 20–120min 长内容，靠观点与人物关系留住观众 | 30–120s 卖点片：用 `sop/long-promo` |
| 有独立收音 + 至少 2 个机位，需要章节 / 字幕 / 金句 | 纯音频播客：先做音频母版，视频只做波形 / 封面版 |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 / 画幅 | 1920×1080（16:9） | 竖屏切片 1080×1920 |
| 帧率 | 30 fps 恒定；多机位统一 30fps（源 25/50fps 先转 30） | 60fps 仅在需要慢动作时 |
| 视频编码 | H.264 High，VBR 平均 9Mbps / 峰值 12Mbps（区间 6–12Mbps） | 母版 ProRes 422 |
| 音频 | AAC 48kHz 立体声 192kbps，响度 -16 LUFS（±1） | 竖屏切片 -14 LUFS |
| 字幕 | 外挂 SRT（标注说话人）+ 章节 | 烧录走 NLE 或 Pillow overlay（本机无 libass） |
| 封装 / 命名 | .mp4（`+faststart`）；`<节目>-ep<序号>-<嘉宾>-v<版本>-<YYYYMMDD>.mp4` | 客户交付附 ProRes + 文稿 + SRT |
| 时长 | 20–120min；超过 60min 建议按话题拆集 | 平台单文件上限见变体节 |

## 前置准备

- 素材：2–3 机位（主机位中景、副机位特写 / 侧 45°）、独立录音（领夹 + 备份录音笔）、场记单、嘉宾资料与授权书；工具：DaVinci Resolve（多机位）或 Premiere，FFmpeg 9.0.2 做同步校验 / 转码 / 章节，转写工具（本机**未装** whisper，按 S4 选型），Pillow 烧字幕。
- 同步方案二选一：**时间码**（机内 Timecode 或 Tentacle Sync 等同步器）或 **clap 拍手**（开机后对所有机位拍 3 次手）。
- 立项：填 [项目Brief](../templates/项目Brief.md)，镜头安排用 [分镜表](../templates/分镜表.md)；双人各一支麦、避免串音，机位不越 180° 轴线。

## 流程总览（阶段 × 产出 × 时间预算）

以 **60min 成片** 估算；20min 短访谈按 ×0.5 缩放。

| 阶段 | 产出 | 时间预算 |
|---|---|---|
| S0–S1 策划 / 机位 | 提纲 + 问题清单 + 机位图 + 同步方案 | 2.5h |
| S2 拍摄 | 多机位素材 + 场记（时间码 / clap 点） | 2h |
| S3 备份与同步 | 素材双备份 + 多机位同步工程 | 1.5h |
| S4 转写 | 文字稿 + 段落时间戳 + 剪辑点清单 | 1.5h（自动 + 校对） |
| S5 粗剪 | 内容结构版（按话题删减） | 3–4h |
| S6 精剪 | 气口 / 节奏 / 金句版 | 3–6h |
| S7 B-roll 与字幕 | B-roll 版 + SRT | 3h |
| S8 声音 | 混音版（降噪、平衡、响度） | 2h |
| S9 调色与包装 | 调色版 + 片头 / 章节卡 | 1.5h |
| S10–S11 导出 / QC | 交付文件 + 章节 + 字幕 + QC 记录 | 1.5h |

## 分阶段操作

### S0–S1 策划、机位与收音

- 一条目标：观众记住嘉宾的**一个观点**，问题围绕它设计；提纲：开场 30–60s → 3–5 个话题块（每块 10–20min）→ 收尾观点 + CTA。
- 机位：主机位双人中景（A）、副机位说话人特写（B）、可选环境侧机位（C），三机位全开；收音每人独立领夹麦进同一设备（分轨），机内音频只作同步参考。
- 同步：有时间码器就锁时间码；没有就开场拍手 3 次、间隔 1s，场记记录第 1 次拍手时间。

### S2 拍摄

- 开录顺序：录音设备先开 → 机位开录 → 拍手 → 开始说话，停机前保留 5s 空镜；场记每 10min 一行（时间码、话题、金句候选、补充画面 B-roll 位置），中途休息不断录。

### S3 备份与同步

- 素材双硬盘备份，校验文件数 / 大小；机内素材与独立录音放同一项目目录。
- 对齐：Resolve 选中全部机位素材 → 右键 **Create Multicam Clip** → Sync 选 **Sound**（有 Timecode 选 **Timecode**）→ 时间线右键 **Switch Angle** 切机位；也可提取音频比拍手尖峰，偏差 >1 帧手动滑移：

```bash
ffmpeg -y -i camA.mov -vn -ac 2 -ar 48000 -c:a pcm_s16le camA.wav
```

### S4 自动转写找剪辑点

- 目的：用文字稿定位「哪一段值得留」，比逐段看画面快一个数量级。
- 选型（本机未装，任选并记录安装方式）：whisper.cpp / faster-whisper 本地免费但需安装；剪映 / 飞书妙记 / YouTube 自动字幕上手快、需校对；商业 API 按分钟计费适合批量。whisper.cpp 示例（命令名随版本变化，先 `--help` 核对）：

```bash
# 需先安装 whisper.cpp 并下载模型；输出 interview.txt / interview.srt
whisper-cli -m models/ggml-large-v3.bin -f interview.wav -l zh -otxt -osrt
```

- 校对姓名、公司、数字、专名；文字稿按话题块分段标时间码，逐段标「保留 / 删除 / 待查证」。按时间码帧级切段（重编码保证切点准确；`-ss/-to` 放 `-i` 前只到关键帧）：

```bash
ffmpeg -y -ss 00:12:30.400 -to 00:14:05.200 -i interview_master.mov \
  -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k -ar 48000 seg01.mp4
```

### S5 粗剪（结构）

- 按话题块拼结构：开场 → 话题 1..N → 收尾；先删整块跑题，再删块内废话。
- 目标时长：原始素材的 40%–70%（60min 访谈通常从 90–120min 素材剪出）；不处理气口、不插 B-roll、不调色。

### S6 精剪（气口 / 节奏）

- 气口：删 >0.6s 停顿，保留 0.2–0.4s 呼吸；句间不要全剪空，交叉淡化 10–20ms 防爆音。
- 多人抢话：保留反应镜头，音频以主说话人为主，抢话段 0.3–0.5s 交叠；说话人切换即切特写，单人长说每 20–40s 换机位 / 景别。
- 用静音检测定位可删停顿（先小样本试参数再批量）：

```bash
ffmpeg -hide_banner -i interview.wav -af silencedetect=noise=-35dB:d=0.8 -f null -
```

- 返工点：气口剪太碎导致语义断裂；机位切换与重音错位；金句剪掉半句。

### S7 B-roll 与字幕

- B-roll 每 60–90s 一次画面变化（资料图、产品、环境空镜、字幕卡），覆盖在停顿或长句上；肖像、第三方素材、音乐授权逐条登记。
- 访谈**必须**上字幕并区分说话人（「主持人：」「嘉宾：」或颜色标签），42–48px@1080p、单行 ≤18 字；外挂 SRT 优先，烧录走 NLE 或按 [教程 SOP](long-tutorial.md) S7 的 Pillow overlay 流程。

### S8 声音

- 先修对白（降噪、去齿音、压缩 3:1）再让音乐避让，音乐垫底 -24 ~ -20 LUFS；双人音量差 >3dB 逐段增益不全局硬压；响度 -16 LUFS（±1）、真峰值 ≤ -1.5 dBTP。

### S9 调色与包装

- 多机位先统一白平衡与曝光，再整体微调，避免机位间肤色跳变（方法见 `kb/color-grading`）。
- 片头 5–10s：节目名 + 嘉宾身份；话题卡 1s；片尾放订阅 / 收听引导。

### S10 导出

```bash
# 横屏交付：1080p30 / H.264 High / VBR 9M（峰值 12M）/ AAC 192k / -16 LUFS
ffmpeg -y -i interview_master.mov \
  -c:v libx264 -preset slow -profile:v high -level 4.1 \
  -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p -r 30 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart ep01-v1.mp4
```

```bash
# 写章节（每个话题一章；START/END 毫秒，按最终成片对时）
cat > chapters.txt <<'EOF'
;FFMETADATA1
[CHAPTER]
TIMEBASE=1/1000
START=0
END=60000
title=00 开场与嘉宾介绍
EOF
ffmpeg -y -i ep01-v1.mp4 -i chapters.txt -map_metadata 1 -codec copy ep01-v1-ch.mp4
```

### S11 QC

按 [QC 清单](../templates/QC清单.md) 逐项过，重点：多机位同步、字幕说话人、章节时间、响度与规格。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 多机位 | 帧率 / 同步 | 30fps 统一；Timecode 或 clap + 波形 |
| 交付视频 / 音频 | 码率 / 响度 | H.264 High VBR 9M（峰值 12M）+ AAC 192k 48kHz / -16 LUFS |
| 气口 / B-roll | 删除 / 频率 | 删 >0.6s 停顿、留 0.2–0.4s；B-roll 每 60–90s 一次 |
| 机位切换 | 间隔 | 20–40s 一次，说话人切换即切 |
| 字幕 | 字号 / 行数 | 42–48px，单行 ≤18 字 |

## 质量门禁（QC）

- [ ] 多机位音画同步（偏差 ≤1 帧），切换处无跳帧、无音量突变
- [ ] 规格达标：1920×1080 / 30fps / 6–12Mbps / AAC 192k 48kHz
- [ ] 响度 -16 LUFS（±1），无爆音、无电流声、无串音
- [ ] 气口自然、语义完整，金句没有被剪断
- [ ] 字幕与语音同步、说话人正确，姓名 / 数字 / 公司名已核对；章节时间准确、首章从 0:00 开始
- [ ] B-roll / 音乐 / 肖像授权齐全，无隐私信息；封面 / 标题 / 简介就绪，上传后抽检开头 / 中段 / 结尾各 30s

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 机位不同步 / 越剪越漂 | 未锁时间码、未拍手，或采样率不一致 | 拍手 + 波形同步；统一 48kHz；漂移大就重拍 |
| 两人串音、副麦收到主麦 | 麦克风距离近、增益过高 | 分轨收音、降增益，后期门限 / 降噪分离 |
| 气口剪太碎，像背书 | 停顿全删、无呼吸 | 保留 0.2–0.4s 呼吸，句间留 1–2 帧 |
| 长访谈时间线卡顿 | 原素材码率高、无代理 | 生成代理剪辑（proxy editing），精剪后回链原素材 |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 转写 / 字幕初稿 | 本地 whisper 或平台自动字幕 | 需安装，见 S4 |
| 静音检测 / 气口定位 | `silencedetect` 输出时间点 | `kb/ffmpeg` |
| 多机位同步 / 交付 | Resolve Multicam + FFmpeg 转码 | `kb/opentimelineio`、`kb/transcode-delivery` |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| YouTube | 16:9；官方建议 1080p 30fps SDR 上传 8Mbps（高帧率 12Mbps）；章节写简介（首章 0:00 起、至少 3 章）；CC 字幕优先外挂 |
| B站 | 16:9，长内容分P / 合集；简介写话题时间戳；弹幕互动强，片头可留「弹幕提问」引导 |
| 抖音 / 视频号 | 9:16 竖屏切片：1080×1920 / 30fps / 8–16Mbps / -14 LUFS；从金句切 30–60s，字幕 64–72px，加说话人标签 |
| 客户交付 | ProRes 422 母版 + H.264 审片版 + SRT + 文字稿 + 章节表 + OTIO/EDL；时间码与素材清单一起归档 |

## 复盘与改进

- 实测记录（2026-11-03，ffmpeg 9.0.2）：1080p30 VBR 9M 与 -16 LUFS loudnorm 命令跑通（合成样片）；本机无 libass，字幕烧录只能走 NLE / Pillow。待优化：whisper 未装、S4 命令未实测；多机位同步只到面板层面。

## 关联条目

- 方法论：`kb/narrative-structure`、`kb/sound-design`、`kb/color-grading`
- 工作流 / 库：`kb/transcode-delivery`、`kb/ffmpeg`、`kb/opentimelineio`；兄弟 SOP：`sop/long-tutorial`、`sop/short-live-clip`

## 来源

1. 本机实测（2026-11-03）：`ffmpeg -version` → 9.0.2；`ffmpeg -hide_banner -h filter=subtitles` → Unknown filter（无 libass）；Pillow 11.3.0。
2. [本机环境基线](../knowledge/环境/environment-local.md)（访问 2026-11-03）。
3. [YouTube 推荐上传编码设置](https://support.google.com/youtube/answer/1722171)（访问 2026-11-03）：1080p 标准帧率 8Mbps、高帧率 12Mbps。
4. [OpenTimelineIO on PyPI](https://pypi.org/project/opentimelineio/)（访问 2026-11-03）：0.18.1，Apache 2.0；[FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）。
