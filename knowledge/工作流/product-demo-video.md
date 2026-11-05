---
id: kb/product-demo-video
title: 产品演示视频 · 录屏/DSL 驱动的功能说明
type: 工作流
domain: [脚本, 录屏, 剪辑, 包装, 交付]
status: 可用
confidence: 中
tags: [产品演示, 官网视频, 功能说明, 录屏, DSL, Playwright, 字幕, CTA]
related: [kb/clip-skills-method, kb/hooks-retention, kb/subtitle-density, kb/remotion]
updated: 2026-11-04
owner: lead
---

# 产品演示视频 · 录屏/DSL 驱动的功能说明

## 一句话定位

面向「公司官网说明、产品功能 walkthrough、SaaS onboarding」的 60–180 秒短片：用录屏或 DSL 自动截图作为画面，旁白讲清「痛点 → 方案 → 操作 → 证据 → 下一步」，初次剪辑即可交付。

## 适用场景

- 官网首页/落地页的说明视频、产品功能更新、客户交付的 walkthrough。
- 有可操作的产品界面（Web/App/桌面），需要真实操作而非纯动画。
- 不适用：品牌形象片（用 [产品宣传片](../../sop/long-promo.md)）、长教程（用 [教程长视频](../../sop/long-tutorial.md)）。

## 原理与判断标准

- 观众不是来看功能清单，是来看「我能得到什么」；每个操作必须对应一个结果。
- 60–180s 只讲 3–5 个功能点；每个功能点 = 一个动作 + 一个可见结果。
- 画面要「可读」：界面文字在手机上能看清；必要时放大/裁切，不要塞满全屏。
- 真实操作优先：录屏/自动化截图的可信度高于纯动画；动画只做转场与标注。

## 可操作步骤

1. **Brief**：目标用户、他们的问题、3–5 个功能点、CTA、目标时长（60/90/120/180s）。
2. **脚本**：钩子（5s 内给结果）→ 问题 → 演示步骤（3–5 个）→ 证据/对比 → CTA；每步一句旁白（4–6 字/秒）。
3. **分镜**：每个功能点写「页面 / 操作 / 镜头（全屏或放大）/ 旁白 / 标注」；准备测试数据与干净账号。
4. **录屏/采集**：
   - 手工：OBS 或系统录屏，1080p/60fps 采集（滚动更顺），隐藏书签栏/个人信息/通知。
   - 自动化：Playwright/DemoDSL 按 YAML 步骤 navigate/scroll/click/type 截图或录屏，旁白与步骤绑定。
5. **粗剪（音频驱动）**：先按旁白定时间轴，删掉等待、误操作、空白页；每个动作 3–6s。
6. **精剪**：放大关键区域（1.2–1.5×）、聚光灯/箭头/编号标注、光标高亮、转场；字幕不遮挡 UI。
7. **声音**：旁白响度 -14 LUFS；BGM 压低到 -18～-24dB 并在旁白处 ducking；操作音效克制。
8. **包装与导出**：片头/片尾/Logo/CTA；输出 1920×1080 或 1080×1920，H.264 8–12Mbps，AAC 48k。
9. **QC**：前 5s 是否给结果、每个功能点是否有可见结果、隐私泄露、字幕安全区、音画同步、规格。

## 参数与阈值

| 参数 | 推荐值 | 依据 |
|---|---|---|
| 时长 | 60–180s（官网 60–90s） | [推断] 落地页注意力 |
| 功能点 | 3–5 个 | [推断] 超过记不住 |
| 每步时长 | 3–6s | [推断] 与操作复杂度匹配 |
| 录屏采集 | 1080p / 60fps | 滚动更顺，交付转 30fps |
| 放大倍率 | 1.2–1.5× | 保证 UI 文字可读 |
| 旁白语速 | 4–6 字/秒 | 与口播一致 |
| 响度 | -14 LUFS；BGM 低 18–24dB | 本仓交付规范 |
| 码率 | 8–12Mbps | 屏幕文字需要更高码率 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 从公司介绍讲起 | 前 5s 没有用户价值 | 先给结果/痛点 |
| 鼠标乱晃、等待加载 | 观众流失 | 剪掉等待，必要时加速 |
| 全屏 UI 不放大 | 手机上文字看不清 | 放大关键区域 + 标注 |
| 功能点全讲 | 记不住 | 只留 3–5 个，其余进官网 |
| 暴露真实邮箱/密钥/客户数据 | 合规风险 | 测试数据 + 打码/遮罩 |
| 字幕压住按钮/菜单 | 看不清操作 | 字幕放安全区，必要时上移 |
| 只有操作没有结果 | 观众不知道价值 | 每步给可见结果/数据 |

## 验证方式

- 前 5s 能说出「这产品帮我做什么」。
- 每个功能点都有「操作 + 结果」；无连续 3s 无信息。
- 画面文字在手机尺寸可读；字幕不挡 UI。
- 隐私扫描：无真实邮箱/密钥/客户名；录屏前已清数据。
- QC：规格/响度/黑帧/命名全过。

## DSL / 自动化路径（可选）

- DemoDSL：YAML 定义场景（url、viewport、steps、narration、effects），先 `validate`/`probe`/`storyboard`/`estimate` 再渲染；支持光标、弹卡、字幕、ducking。
- Playwright 自建：录制脚本 + 稳定选择器 + 固定 viewport；每一步截图，旁白按步骤时长合成。
- 注意：DemoDSL 为非 OSI 许可，只借 DSL 结构；自建时用 Playwright + ffmpeg 即可。

## 关联条目

- 剪辑决策：[剪辑决策方法](../方法论/clip-skills-method.md)
- 钩子/字幕：`kb/hooks-retention`、`kb/subtitle-density`
- 代码化包装：`kb/remotion`
- SOP：[产品功能/官网说明视频 SOP](../../sop/long-product-explainer.md)

## 来源

1. [Fran-cois/demodsl](https://github.com/Fran-cois/demodsl)（DemoDSL Community License，访问 2026-11-04）：YAML 场景、validate/probe/storyboard/estimate、光标/字幕/ducking。
2. [0xSero/video-edit](https://github.com/0xSero/video-edit)（MIT）：录屏精剪、静态画面检测、隐私打码、音频链、输出校验。
3. [danielmeppiel/apm-onemin-video](https://github.com/danielmeppiel/apm-onemin-video)（Remotion 60s 产品视频示例，访问 2026-11-04）。
4. 本仓来源台账：[research/来源台账.md](../../research/来源台账.md)。
