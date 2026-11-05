---
id: sop/short-kepu-motion
title: "科普动画短视频 · 代码驱动（Remotion / HyperFrames）SOP"
type: sop
video_type: "科普动画"
duration: "45–120s"
aspect: "16:9 / 9:16"
platforms: [B站, YouTube, 抖音, 视频号]
difficulty: 高
tools: [Remotion, HyperFrames, Node.js, ffmpeg, TTS, WhisperX]
status: 可用
updated: 2026-11-05
owner: lead
---

# 科普动画短视频 · 代码驱动 SOP

> 读者：要用 Remotion 或 HyperFrames 做一条 45–120 秒科普动画的人或 Agent。目标：事实站得住、声音为轴、30 秒样片先验收、初次成片即可发布。

## 适用 / 不适用

| 适用 | 不适用（改用什么） |
|---|---|
| 知识科普、原理讲解、观点解读 | 真人出镜口播：[口播 SOP](short-oral-knowledge.md) |
| 需要代码绘制动画、批量、可复现 | 纯数据图表：[数据动画 SOP](long-data-animation.md) |
| 45–120s 竖屏/横屏 | 实拍产品演示：[产品说明 SOP](long-product-explainer.md) |
| Remotion（React）或 HyperFrames（HTML/JS） | 需要生成式视频/图像：本 SOP 不覆盖 |

## 交付规格

| 项 | 主规格 | 变体 |
|---|---|---|
| 分辨率 | 1920×1080（16:9） | 1080×1920（9:16） |
| 帧率 | 30 fps | 60 fps（动效密集） |
| 视频 | H.264 High，VBR 8–12 Mbps | 图形简单可 4–6 Mbps |
| 音频 | AAC 48 kHz 192 kbps，-14 LUFS | 纯 BGM 版 -16 LUFS |
| 字幕 | 烧录（默认）或外挂 | 平台自动字幕时外挂 |
| 封装/命名 | .mp4，`<主题>-kepu-v1-<date>.mp4` | 附封面、脚本、来源清单 |
| 时长 | 45–120s | 长讲解 2–8min（同流程扩分镜） |

## 前置准备

- 选题与事实台账：每个 claim 的来源；无法核实的标 [推断] 或删。
- 脚本：逐字稿（口语化），按句切分；中文约 250 字/分钟。
- 工具：Node 22+、ffmpeg；Remotion（`npx create-video@latest`）或 HyperFrames（`npx hyperframes init`）。
- 素材：字体（CJK）、CC0 音效/BGM、封面模板。
- 模板：4 套视觉模板（科技紫/科学 MG/纸感/黑板）或自定义主题，先锁定。
- 立项：填 [项目 Brief](../templates/项目Brief.md)；分镜用 [分镜表](../templates/分镜表.md)。

## 流程总览（60 秒成片，单人/Agent）

| 阶段 | 产出 | 时间预算 |
|---|---|---|
| S0 选题 + 事实台账 | 选题卡、来源表 | 0.5h |
| S1 模板选择 | 模板 ID、色彩/字体规范 | 0.2h |
| S2 逐字稿 | 分句脚本 | 1.0h |
| S3 TTS + 字幕 | 音频 + 词/句时间戳 | 0.3h |
| S4 分镜/时间轴 | 镜头表（画面/动效/音效） | 1.0h |
| S5 30s 样片 | 封面 + 钩子 + 首个知识点 | 1.5h |
| S6 全量开发 | Remotion/HyperFrames 镜头代码 | 3.0h |
| S7 渲染 | 低清 proof → 高清 MP4 | 0.3h |
| S8 QC | 自动检查 + 人工抽帧 | 0.5h |
| 合计 | — | 约 8h（Agent 可压缩） |

## 分阶段操作

### S0 选题 + 事实台账

- 一句话目标：「看完能解释 X」。
- 列 claim 表：claim / 来源 / 可信度 / 是否进片。
- 禁止先写画面再找事实。

### S1 模板选择

- 4 套模板：Tech Purple（AI/科技）、Science MG（工程/自然科学）、Editorial Paper（人文/生活）、Chalk Classroom（数学/物理）。
- 模板同时约束背景、卡片、光效、进度条、字体层级；中途不换。

### S2 逐字稿

- 口语化、短句；按句切分，方便字幕与分镜。
- 45–120s 约 200–500 字（按 4 字/秒）。
- 开头 3–5s 给结论/问题，不铺垫。

### S3 TTS + 字幕

- 一次生成音频与词/句时间戳；字幕是整片时间基准。
- 响度 -14 LUFS；保留自然停顿。

### S4 分镜/时间轴

- 按字幕句切镜头；每镜头一个视觉焦点。
- 标注：画面元素、动效（入场/强调/转场）、音效、字幕强调词。
- 每个镜头 2–6s；避免连续静态。

### S5 30 秒样片

- 做封面 + 钩子 + 第一个知识点；验收构图、字号、配色、语速、节奏。
- 样片通过才做剩余部分；不通过先改模板/文案。

### S6 全量开发

- Remotion：React 组件 + `useCurrentFrame/interpolate/spring`；确定性动画。
- HyperFrames：HTML + 可 seek 时间线（GSAP/CSS/Lottie）；`npx hyperframes lint` 校验。
- 每个镜头先渲染静帧检查，再整段渲染。
- 图元/组件复用；字幕安全区、文字自动缩放、卡片裁切分层。

### S7 渲染

- 先低清 proof（720p/低码率）验证节奏，再高清。
- 校验帧数 = `round(duration×30)`；音画同步。

### S8 QC

- 事实：每条 claim 有来源；无编造。
- 画面：文字不溢出/不出安全区；每镜头一个焦点；无静止过久。
- 字幕：与语音对齐、无错别字、不挡关键信息。
- 交付：规格/响度/帧数/命名通过；工程与来源清单齐全。

## 参数速查

| 场景 | 参数 | 值 |
|---|---|---|
| 时长 | 短视频 / 长讲解 | 45–120s / 2–8min |
| 语速 | 中文 | 约 250 字/分钟 |
| 单镜头 | 时长 | 2–6s |
| 字幕 | 行数/位置 | ≤2 行，底部安全区 |
| 画幅 | 横/竖 | 1920×1080 / 1080×1920 |
| 响度 | 交付 | -14 LUFS |
| 码率 | 交付 | 8–12 Mbps |
| 样片 | 验收长度 | 前 30s |

## 质量门禁（QC）

- [ ] 事实台账完整，无无来源 claim
- [ ] 30s 样片已验收
- [ ] 字幕时间轴与音频逐句对齐
- [ ] 文字不溢出、不出安全区；卡片/阴影无裁切
- [ ] 无连续 2–3s 静止；结尾有 1–2s 停留
- [ ] 帧数 = round(duration×30)；无音画漂移
- [ ] 规格/响度/命名通过 qc-deliver

## 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 字幕与画面不同步 | 先画画面再配音 | 回到声音为轴 |
| 文字溢出/被裁 | 未做自动缩放与分层 | 容器测量 + 安全区检查 |
| 画面各自为政 | 没有统一时间轴 | 用字幕时间驱动全部动画 |
| 返工大 | 全片做完才看 | 30s 样片先验收 |
| 渲染慢 | 高分辨率全量调试 | 低清 proof 后再高清 |
| 事实错误 | 没有事实台账 | claim 先核对来源 |

## 可自动化环节

| 环节 | 方式 | 工具 |
|---|---|---|
| 脚本/时间轴 | JSON/Markdown 单一数据源 | 自建脚本 |
| TTS/字幕 | TTS + 词级时间戳 | WhisperX / TTS |
| 动效渲染 | 代码组件 | Remotion / HyperFrames |
| 预检 | lint / stills / 帧数 | 框架 CLI + ffprobe |
| QC | 脚本 | 本仓 qc-deliver |

## 变体（平台 / 时长 / 素材条件）

| 变体 | 差异 |
|---|---|
| 横屏 16:9 | 信息密度高，适合 B站/YouTube |
| 竖屏 9:16 | 单屏一个信息点，字幕更大 |
| 长讲解 2–8min | 增加章节、进度条、30s 样片后分段开发 |
| 纯动画无口播 | 字幕承担叙事，音效/BGM 更强 |

## 复盘与改进

- **已跑通 Remotion 版科普样片（2026-11-05）**：[kepu-compare](../pipeline/remotion/kepu-compare/) · WorkBuddy vs Qoder，66.0s / 1978 帧 / 1920×1080 / -16 LUFS；Remotion 4.0.540 + Node 26 + Chrome for Testing + 阿里云 Qwen TTS（qwen-audio-3.1-tts-flash / longanhuan_v3.1），QC 通过。HyperFrames 仍未安装（[待确认]）。
- 交付码率说明：深色图形内容在 `-b:v 8M` 下实际约 1.4Mbps，属内容自适应；屏幕文字仍清晰。
- 音频：去掉 BGM，仅旁白 + 两遍 loudnorm；TTS 最终采用阿里云百炼 Qwen TTS（qwen-audio-3.1-tts-flash / longanhuan_v3.1）。
- 计费记录：[kepu-compare/TTS_BILLING.md](../pipeline/remotion/kepu-compare/TTS_BILLING.md)：10 次调用，input 292 / output 789 / total 1081 tokens（API 返回）。
- 回填：真实项目记录渲染耗时、返工点、有效开头。
- 与数据动画共用「帧=f(t)、静帧/接触表、帧数校验」的工程习惯。

## 关联条目

- 方法：[科普视频方法](../knowledge/方法论/kepu-video-method.md)、[剪辑决策方法](../knowledge/方法论/clip-skills-method.md)
- 工具：[HyperFrames](../knowledge/开源库/hyperframes.md)、[Remotion](../knowledge/开源库/remotion.md)
- 字幕：[字幕与信息密度](../knowledge/方法论/subtitle-density.md)

## 来源

1. [sixwei2025/psych-kepu-video-skill](https://github.com/sixwei2025/psych-kepu-video-skill)（MIT）
2. [liangdabiao/video-skills-toolkit](https://github.com/liangdabiao/video-skills-toolkit)
3. [ShiyouQi888/2D-kepu-donghua-Skill](https://github.com/ShiyouQi888/2D-kepu-donghua-Skill)
4. [howznguyen/shorts-kit](https://github.com/howznguyen/shorts-kit)
5. [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（Apache-2.0）
6. [remotion-dev/remotion](https://github.com/remotion-dev/remotion)
7. 本仓：[来源台账](../research/来源台账.md)