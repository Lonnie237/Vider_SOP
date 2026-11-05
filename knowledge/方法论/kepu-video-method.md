---
id: kb/kepu-video-method
title: 科普视频方法 · 声音为轴、字幕为基准、事实台账
type: 方法论
domain: [脚本, 字幕, 动效, 交付]
status: 可用
confidence: 高
tags: [科普视频, Remotion, HyperFrames, 声音为轴, 事实台账, 故事流, 样片验收, QC]
related: [kb/hyperframes, kb/remotion, kb/clip-skills-method, kb/subtitle-density]
updated: 2026-11-05
owner: lead
---

# 科普视频方法 · 声音为轴、字幕为基准、事实台账

> 综合 Remotion / HyperFrames 生态中多个科普视频 Skill 的共性（psych-kepu、video-skills-toolkit、2D-kepu-donghua、shorts-kit、VibeDS）。不复制代码，只提炼方法；经验阈值标 [推断]。

## 一句话定位

科普视频不是「生成画面」，而是**一条以声音为轴的时间线**：先有逐字稿与音频，再拿字幕时间戳驱动所有画面、动画、音效；事实先核对，模板先锁定，30 秒样片先验收。

## 适用场景

- 45–120 秒的科普/知识短视频（横屏或竖屏）。
- 2–8 分钟的科普讲解长视频。
- 用 Remotion / HyperFrames 等代码化路线批量生产。
- 不适用：真人实拍为主、纯数据新闻（用 [数据动画 SOP](../../sop/long-data-animation.md)）。

## 原理与判断标准

1. **声音为轴**：逐字稿 → TTS → 字幕时间戳 → 画面/动画/音效全部对齐字幕；没有时间轴，画面各自为政。
2. **字幕是唯一基准**：改文案就重录/重对齐；字幕时间 = 动画时间的真源。
3. **事实台账**：每句 claim 先有来源记录，再进脚本；shorts-kit 甚至用 linter 强制。
4. **模板先选后做**：视觉模板/主题先锁定，再写文案与代码；同时约束背景、卡片、光效、进度条、字体层级。
5. **5 个确认点**：模板 → 时长/语言 → 口播文案 → 配音方案 → 前 30 秒样片；确认后全量开发。
6. **确定性动画**：画面是时间的函数；同一输入同一输出。
7. **QC 规则化**：文字溢出、越界、卡片裁切、静止过久、末拍停留、字幕安全区。

## 可操作步骤

1. **选题与受众**：一个具体问题；先写一句「看完能解释什么」。
2. **事实台账**：列出每个要讲的 claim、来源、可信度；无法核实的改成 [推断] 或删掉。
3. **选模板**：横屏/竖屏、4 套视觉模板（科技紫/科学 MG/纸感/黑板）或自定义主题；锁定后不改。
4. **定稿逐字稿**：口语化、按句切分；中文约 250 字/分钟；标出关键词与强调。
5. **TTS + 字幕**：一次生成音频与词/句时间戳；字幕作为整片时间基准。
6. **时间轴与分镜**：按字幕切镜头；每个镜头一个视觉焦点；标注动效与音效。
7. **30 秒样片**：先做前 30s（封面 + 钩子 + 第一个知识点），验收构图/字号/配色/语速/节奏。
8. **全量开发**：按分镜写 Remotion/HyperFrames 组件或 HTML；每个镜头渲染静帧检查。
9. **渲染与 QC**：低清 proof → 高清；自动 QC + 人工抽帧；交付视频 + 工程 + 来源 + QC 记录。

## 参数与阈值

| 参数 | 推荐值 | 依据 |
|---|---|---|
| 短视频时长 | 45–120s | 平台科普内容常见区间 |
| 长讲解 | 2–8min | 2D-kepu 默认 |
| 画面 | 1920×1080 或 1080×1920，30fps | 交付规范 |
| 语速 | 4–6 字/秒 | 与口播一致 |
| 单镜头 | 2–6s | 与字幕句长匹配 |
| 字幕 | 底部安全区，≤2 行 | 平台 UI 遮挡 |
| 静止画面 | 不超过 2–3s | [推断] 防流失 |
| 末拍停留 | 结尾留 1–2s | 来源 QC 规则 |
| 样片验收 | 前 30s | 2D-kepu 流程 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 先画画面再配音 | 节奏被画面绑架，字幕对不上 | 先逐字稿/音频/字幕 |
| 念 bullet | 听觉不友好 | 重写为口语句 |
| 没有事实台账 | 科普内容容易编造 | claim 先有来源 |
| 中途换模板 | 视觉语言混用 | 先锁定模板 |
| 全片做完才看 | 返工成本最高 | 30s 样片验收 |
| 文字溢出/出安全区 | 平台遮挡、看不清 | 自动 QC + 抽帧 |
| 无意义漂浮动画 | 干扰信息 | 动效服务叙事 |

## 验证方式

- 事实：每条 claim 有来源；无来源的标 [推断] 或删除。
- 音画：字幕时间轴与音频逐句对齐；抽 3 个切点核对。
- 画面：文字不溢出、不出安全区；每镜头一个焦点。
- 节奏：无连续 2–3s 静止；结尾有停留。
- 交付：规格/响度/帧数/命名通过 QC；工程与来源齐全。

## 关联条目

- 工具：[HyperFrames](../开源库/hyperframes.md)、[Remotion](../开源库/remotion.md)
- 剪辑决策：[剪辑决策方法](clip-skills-method.md)
- 字幕：[字幕与信息密度](subtitle-density.md)
- SOP：[科普动画短视频 SOP](../../sop/short-kepu-motion.md)

## 来源

1. [sixwei2025/psych-kepu-video-skill](https://github.com/sixwei2025/psych-kepu-video-skill)（MIT）：JSON 脚本驱动、45s、封面首帧、qc.sh。
2. [liangdabiao/video-skills-toolkit](https://github.com/liangdabiao/video-skills-toolkit)：逐字稿→TTS→字幕→动画→低清 proof→高清；字幕唯一基准。
3. [ShiyouQi888/2D-kepu-donghua-Skill](https://github.com/ShiyouQi888/2D-kepu-donghua-Skill)：4 模板、5 确认点、30s 样片、QC 与交付目录。
4. [howznguyen/shorts-kit](https://github.com/howznguyen/shorts-kit)：fact ledger、20+ 故事流、word-timed 字幕、安全区。
5. [dy-hashiqi/VibeDS-skill](https://github.com/dy-hashiqi/VibeDS-skill)（Apache-2.0）：HyperFrames 科普技能、lint→preview→render。
6. 本仓调研：[Remotion vs HyperFrames](../../research/2026-11-05-remotion-vs-hyperframes-科普视频.md)。