---
id: sop/short-vlog
title: "Vlog · 生活叙事 Vlog SOP（3–15min）"
type: sop
video_type: "Vlog"
duration: "3–15min"
aspect: "16:9"
platforms: [B 站, YouTube, 抖音, 视频号]
difficulty: 中
tools: [手机或相机, 无线麦, Premiere Pro / DaVinci Resolve / 剪映专业版, ffmpeg]
status: 可用
updated: 2026-11-03
owner: sop-short
---

# Vlog · 生活叙事 Vlog SOP

> 读者：第一次完整做 Vlog 的人或执行 Agent。目标：3–15min 成片有清晰叙事线、B-roll 够、配乐不抢戏，3min 成片单人 1 天内可交付。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 生活 / 旅行 / 探店 / 一日记录，3–15min | 单人口播知识 → [口播知识](short-oral-knowledge.md) |
| 有多个场景、需要叙事而不是卡点 | 音乐驱动无叙事 → [混剪卡点](short-montage-beat.md) |
| 主发 B 站 / YouTube，可竖版二次分发 | 直播拆条 → [直播切片](short-live-clip.md) |
| 一人或双人小团队 | 多机位长访谈 / 播客 → `sop/long-interview-podcast` |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 / 画幅 | 1920×1080（16:9） | 1080×1920 竖版（抖音 / 视频号二次分发，字幕重排） |
| 帧率 | 30 fps 恒定 | 运动镜头多可 60 fps，交付统一 30 fps |
| 视频编码 / 码率 | H.264 High、level 4.1、VBR 6–12 Mbps（目标 9 Mbps） | 4K 源可出 4K 母版，平台交付仍走 1080p |
| 音频 | AAC 48 kHz 立体声 192 kbps、-16 LUFS ±1、真峰值 ≤ -1.5 dBTP | 竖版分发时平台可能归一，仍以 -16 为准 |
| 字幕 | 烧录（移动端为主）或外挂 SRT（B 站 / YouTube） | 双语字幕用 SRT + 平台自动翻译 |
| 封装 / 命名 | .mp4 / `vlog-<主题>-<时长>-v<n>-<日期>.mp4` | 母版 ProRes 422 单独归档 |
| 时长 | 3–15min | 3–6min 完播最好，8min 以上需要章节 |

## 前置准备

- 素材：成片时长的 10–15 倍素材量（3min 成片 → 30–45min 可用素材）、空镜 ≥10 个/场景、环境声每场景 30s。
- 工具：手机 / 相机 + 无线麦（领夹或枪麦）；NLE 三选一；本机 ffmpeg 9.0.2 做转码、代理、导出（无 libass）。
- 授权：音乐与素材商用授权；出现路人正脸需虚化或取得同意；商家拍摄先打招呼。
- 立项：填 [项目 Brief](../templates/项目Brief.md)（写清一句话主题与目标受众）；机位与场景用 [分镜表](../templates/分镜表.md) 变体。

## 流程总览（阶段 × 产出 × 时间预算）

> 基准：3 分钟（180s）成片、单人操作、素材为自拍自剪。换算：目标时长 T 秒 → 可变工时 ×（T/180），固定工时不变。
> 固定工时 = S0+S1+S9+S10+S11 = 78 min；可变工时 = S2–S8 = 300 min。例：8min 成片 ≈ 78 + 300×2.67 ≈ 878 min ≈ 14h40m（约 2 个工作日）。

| 阶段 | 产出 | 时间预算（180s 基准） | 缩放 | 负责人 |
|---|---|---|---|---|
| S0 立项与叙事线 | 叙事大纲 | 25 min | 固定 | 编导 |
| S1 拍摄计划 | 场景表 + 镜头清单 | 20 min | 固定 | 编导 |
| S2 拍摄 | 素材 + 场记 | 75 min | 线性 | 出镜 / 摄像 |
| S3 素材整理与转写 | 选段清单 | 45 min | 线性 | 剪辑 |
| S4 粗剪（结构） | 结构版 | 45 min | 线性 | 剪辑 |
| S5 精剪（节奏 / B-roll） | 节奏版 | 60 min | 线性 | 剪辑 |
| S6 声音（人声 / 配乐 / 音效） | 混音版 | 30 min | 线性 | 剪辑 |
| S7 调色 | 调色版 | 20 min | 线性 | 剪辑 |
| S8 字幕与章节 | 字幕 + 章节 | 25 min | 线性 | 剪辑 |
| S9 包装与封面 | 包装版 | 15 min | 固定 | 剪辑 |
| S10 导出 | 交付文件 | 8 min | 固定 | 剪辑 |
| S11 QC | QC 记录 | 10 min | 固定 | 编导 |
| 合计 | — | 378 min ≈ 6h18m | — | — |

## 分阶段操作

### S0 立项与叙事线

- 三条常用叙事线，只选一条：时间线（一天从早到晚）、问题—解决（出发 → 遇阻 → 解决）、地点线（按地点推进）。
- 三段式：开场 0–15s（钩子 + 价值承诺）→ 主体 3–5 段（每段 45–120s，段首有小钩子）→ 收尾 15–30s（一句话总结 + CTA / 下集预告）。
- 输出叙事大纲表：`段落 | 时长 | 事件 | 情绪 | 关键画面`；每段只承载一个信息点。

### S1 拍摄计划

- 场景表：地点 / 时间 / 光线方向 / 镜头清单（远中近特）/ 收音方式。
- 光线优先：日出后 1 小时、日落前 1 小时；室内靠窗，避免顶灯直射。
- 每个场景至少拍：1 个广角定场、1 个中景叙事、2–3 个细节空镜；空镜用于转场和 B-roll。

### S2 拍摄

- 16:9、4K30 或 1080p30，全片统一帧率；运动镜头用稳定器或倚靠固定物。
- 收音优先于人像：有对白必上无线麦；环境声单独录 30s，后期补空间感。
- 每个场景开头拍手或报场景号，方便对齐；当天素材当天备份到两块盘。

### S3 素材整理与转写

- 目录：`素材/<项目>/{A-roll,B-roll,audio,music,drone}`；导入后先粗看打星（1–5 星）。
- 4K 素材先建代理（proxy editing）再剪；本机可用 ffmpeg 批量生成 720p 代理：

```bash
ffmpeg -hide_banner -y -i 4k_clip.mp4 -vf "scale=1280:720" -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k proxy_4k_clip.mp4
```

- 转写：有对白就转写并检索关键词；无对白靠日志与星标选段。

### S4 粗剪（结构）

- 先搭骨架：按叙事大纲放每段主镜头与关键对白，不管 B-roll、不调色、不加音乐。
- 时长控制：主体每段 ≤120s；先砍重复动作与无效移动，再谈节奏。
- 静音测试：关掉声音看一遍，画面能否讲清发生了什么；不能就补旁白或补镜头。

### S5 精剪（节奏 / B-roll / 转场）

- B-roll 覆盖 30–50% 时长；每个事件后接 2–3s 空镜或细节，给观众消化时间。
- 单镜 3–8s（叙事）/ 1–3s（段落加速）；口播段用跳剪压停顿，配 5% 缩放变化。
- 转场：硬切 ≥90%；地点转换用空镜或 0.3–0.5s 黑场；不用旋转、翻页、故障转场。
- 段落之间留 1 个「呼吸点」：空镜 + 音乐 break（0.5s 无人声）。

### S6 声音

- 人声：降噪（≤50%）→ 高通 80–100 Hz → 压缩 3:1 → 2–4 kHz 提 1–2 dB。
- 配乐 3–5 段，按情绪换：开场轻快 → 主体跟随事件 → 收尾舒缓；每段音乐 -22 ~ -26 LUFS 垫在人声下。
- 环境声保留 -20 dB 左右；音效只在转场与强调处用，全片 ≤10 个。
- 响度：-16 LUFS、真峰值 -1.5 dBTP；两遍 loudnorm（本机实测 2026-11-03，横屏用例输出 -16.0 LUFS）：

```bash
ffmpeg -hide_banner -nostats -i vlog_mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | tail -12
```

### S7 调色

- 一级：白平衡 → 曝光 → 对比度；同一场景内先匹配，再跨场景统一。
- 二级：肤色保护（矢量示波器肤色线）、天空单独压高光；风格 LUT 强度 40–70%。
- 不做：全片一个高饱和 LUT、每镜单独调色导致跳色。

### S8 字幕与章节

- 字号 42–52 px（1080p），单行 ≤20 字、≤2 行，底部安全区 ≥120 px。
- 断句按语义；人名、地名、品牌首次出现加注；口播段可只给关键词。
- 章节：≥8min 的片子加时间码章节（YouTube 简介 / B 站分段），每章 1.5–3min。

### S9 包装与封面

- 片头 3–5s：标题 + 地点 + 日期，不做过长动画。
- 章节卡 1–2s；片尾 CTA + 下集预告 ≤10s。
- 封面：选有信息、有情绪的一帧，标题 ≤8 字，避开平台 UI。

### S10 导出

- NLE 导出设置：H.264、High、1920×1080、30 fps、VBR 2-pass 目标 9 Mbps / 最大 12 Mbps、AAC 192 kbps 48 kHz。
- 命令行（本机实测 2026-11-03：输出 H.264 High / 9.44 Mbps / AAC 48 kHz、-16.0 LUFS，退出码 0）：

```bash
ffmpeg -hide_banner -y -i vlog_cut.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" -c:v libx264 -preset slow -profile:v high -level 4.1 -pix_fmt yuv420p -r 30 -b:v 9M -maxrate 12M -bufsize 18M -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-21.8:measured_LRA=0.0:measured_TP=-20.78:measured_thresh=-31.8:offset=-0.01:linear=true" -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart out.mp4
```

- 竖版二次分发：宽度改 1080、高度 1920、码率 12 Mbps（8–16）、响度 -14 LUFS，字幕重排到安全区。
- 自查：`ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=profile,width,height,r_frame_rate -of compact out.mp4`。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 素材量 | 拍摄 / 成片比 | 10–15×（3min 成片 30–45min 素材） |
| B-roll | 覆盖比例 / 单条时长 | 30–50% / 2–3s |
| 声音 | 人声 / 音乐 / 响度 | -12 ~ -6 dBFS / -22 ~ -26 LUFS / -16 LUFS |
| 交付 | 码率 / 帧率 | 9 Mbps（6–12）/ 30 fps |

## 质量门禁（QC）

- [ ] 规格：1920×1080 / 30 fps / H.264 High / 6–12 Mbps / AAC 48 kHz 192k / .mp4
- [ ] 时长 3–15min；开场 15s 内有承诺，主体段落边界清晰
- [ ] 静音可懂：关掉声音能看出发生了什么
- [ ] B-roll 覆盖 30–50%；无重复镜头凑时长
- [ ] 响度 -16 LUFS ±1；人声清晰，音乐不压人声
- [ ] 字幕无错别字、不出安全区；≥8min 有章节时间码
- [ ] 调色统一：场景切换无跳色；路人隐私已处理
- [ ] 授权可追溯：音乐、素材、出镜人同意
- [ ] 在手机与电脑各预览 1 次

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 像流水账、完播低 | 没有一条叙事线 | 先写一句话主题，按三段式重组，砍掉无关段落 |
| 剪出来比预想长 | 舍不得删素材 | 按「每段只留一个信息点」砍，先砍无对白无事件的段落 |
| 音乐压人声 | 只调总音量 | 音乐单独轨 -22 ~ -26 LUFS，人声段 duck -3 ~ -6 dB |
| 场景之间跳得生硬 | 缺转场素材 | 补空镜 / 环境声过渡；用 0.3–0.5s 黑场硬切 |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 代理生成 | 批量 scale 到 720p | ffmpeg（`kb/transcode-delivery`） |
| 响度测量 / 归一 | loudnorm 两遍 | ffmpeg（`kb/ffmpeg`） |
| 字幕烧录 | SRT → PNG → overlay | Pillow + ffmpeg（见 [口播 SOP](short-oral-knowledge.md)） |
| 规格校验 | ffprobe JSON 比对 | ffprobe + 脚本 |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| B 站 | 16:9 主战场；封面标题 + 分区正确；简介写章节与素材说明 |
| YouTube | 16:9；≥8min 加章节时间码；配英文字幕；缩略图单独设计 |
| 抖音 | 竖版 1080×1920、-14 LUFS；剪 60–90s 预告版导流，正片不放全 |
| 视频号 | 16:9 或竖版；官方建议码率 ≥10 Mbps（[事实]，来源 3）；封面按分享卡片设计 |
| 小红书 | 9:16 或 3:4；图文 + 视频混发；首帧即封面 |

## 复盘与改进

- 实测记录：2026-11-03 本机验证 16:9 导出（1920×1080 → H.264 High / 9.44 Mbps / AAC 48 kHz）、两遍 loudnorm 输出 -16.0 LUFS、代理生成与竖屏模糊背景滤镜命令退出码 0。真实 Vlog 素材尚未端到端跑通。
- 改进项：用一次真实拍摄（≥30min 素材）跑完整流程，记录选段命中率与实际总工时。

## 关联条目

- 方法论 / 工作流（id 由其他 Agent 并行产出，路径就绪后由 Lead 统一改为相对链接）：`kb/narrative-structure`、`kb/sound-design`、`kb/subtitle-density`、`kb/transcode-delivery`
- 工具：`kb/ffmpeg`；模板：[项目 Brief](../templates/项目Brief.md)、[分镜表](../templates/分镜表.md)、[QC 清单](../templates/QC清单.md)
- 同批 SOP：[口播知识](short-oral-knowledge.md)、[混剪卡点](short-montage-beat.md)、[直播切片](short-live-clip.md)
- 环境：[本机环境基线](../knowledge/环境/environment-local.md)

## 来源

1. 本机实测（2026-11-03）：`ffmpeg -version` → 9.0.2；3s 1920×1080 源导出 → H.264 High / 9.44 Mbps / AAC 48 kHz；`ebur128` 校验 -16.0 LUFS；代理与竖屏重构命令退出码 0。
2. [FFmpeg Filters · loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)（访问 2026-11-03）：两遍测量与线性归一参数说明。
3. [视频号助手 · 素材要求](https://findeross.weixin.qq.com/cgi-bin/mmfindernodelivecrmwebbroker-bin/helper-center/pages/DCbKPGzZkvVHcIr6)（访问 2026-11-03）：手机端 3s–60 min、≤2 GB，码率建议 ≥10 Mbps。