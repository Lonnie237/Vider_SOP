---
id: kb/storyboard-layout-cards
title: 分镜版式卡 · 用 4 个母版管住 8 个镜头
type: 方法论
domain: [分镜, 版式, 视觉设计, 工作流]
status: 可用
confidence: 中
tags: [分镜, 版式卡, 母版, 网格, 焦点, 分镜设计, 视觉一致性]
related: [kb/layout-patterns, kb/script-research-sop, kb/caption-motion-continuity, kb/agent-review-panel]
updated: 2026-11-05
owner: lead
---

# 分镜版式卡 · 用 4 个母版管住 8 个镜头

## 一句话定位

**每个分镜都要做版式设计，但不要每个都重新发明版式。** 先定一次全局系统，再选 3–5 个母版，最后给每个 Scene 填一张「版式卡」：结论、焦点、网格、层级、揭示、动效、字幕、风险。

## 适用场景

- 知识/科普/产品讲解视频的 5–15 个 Scene。
- 需要「视觉统一」又「每镜有焦点」的项目。
- 代码化视频（Remotion/HyperFrames）与实拍包装都适用。
- 不适用：纯剧情片、纯实拍对话（镜头逻辑不同）。

## 原理与判断标准

### 1. 理论支撑：不是拍脑袋

| 理论/来源 | 对版式卡的约束 |
|---|---|
| Mayer 多媒体原则（ coherence、signaling、spatial contiguity、segmenting） | 一屏一个信息；用视觉信号标当前焦点；相关元素靠近；长内容分段 |
| 认知负荷理论（Sweller） | 减少外在负荷：固定网格/字号/安全区，观众不用每镜重新找结构 |
| 逆向设计（Wiggins & McTighe） | 每个 Scene 先有「一句结论 + 目标」，再决定版式 |
| 镜头语法（creator-playbook 7 类） | 结论/对比/流程/层级/问题-方案/分类/CTA，决定空间拓扑 |
| 修辞场景（explainer-scenes 8 类） | 按论证任务选 compare/flow/stat/checklist 等，不按「好看」选 |
| 版式库（20 种） | 提供母版与参数，不每镜重造 |
| 单一焦点/安全区（video-layout） | 1 秒内知道看哪；重要内容不出安全区；用时间解决拥挤 |

> 这些理论支持「为什么这样设计」，但不证明某个具体画面一定有效；仍需线框/静帧/试播验证。

### 2. 为什么是「母版 + 版式卡」

- 8 个 Scene 全用同一模板 → 像 PPT，没有焦点；
- 8 个 Scene 八套原创 → 视觉语言碎，制作成本高，观众要重新学构图；
- **4 个母版 + 8 张微调卡**：视觉语法稳定，内容结构各得其所。

### 3. 版式卡必须回答的 8 个问题

1. 这一镜的一句话结论是什么？
2. 用哪个母版？
3. 构图：左右/居中/全宽，各占几列？
4. 唯一焦点是什么？
5. 元素层级（谁前谁后、谁压暗）？
6. 揭示顺序：先给结构，还是按锚点出现？
7. 动效：最多一个主要动作？
8. 字幕、屏显、转场、风险分别是什么？

## 可操作步骤

### Phase 1 · 全局系统（一次）

- 画布/网格/安全区；
- 字体层级与字号；
- 色彩语义（阵营/强调/正误）；
- 字幕规格（单行 12–16 字、静态）；
- 动效语言（写入/生长/翻牌/预测停）；
- 5 条以内「禁止项」。

产出：视觉 token 表。

### Phase 2 · 选母版（一次）

按叙事任务选 3–5 个母版：

- A 全屏问题/主物（hook、结论、CTA）；
- B 左右对照（A vs B、规定 vs 规定）；
- C 三格/清单（三个例子、三个检查）；
- D 全宽数轴/时间线（位置、流程、距离）；
- 可选 E 真实界面/证据（文档、代码、录屏）。

产出：母版 → Scene 映射表。

### Phase 3 · 逐镜版式卡（每 Scene 一张）

按「8 个问题」填；每张卡只允许一个焦点；文字块 ≤3 行；长内容拆镜。

### Phase 4 · 线框验证（不渲染）

- 黑白线框：只看构图/焦点/层级；
- 遮住旁白看静帧：1 秒能否说出结论？
- 检查安全区、字幕区、文字溢出；
- 线框不过，不进动画。

### Phase 5 · 动效与字幕

- 每个 Scene 只做一个主要动作；
- 字幕单行静态；屏显不复述字幕；
- 预测/停顿写成时间点，不靠「感觉」。

### Phase 6 · 评审

- 用 [Agent 评审团](agent-review-panel.md) 或人工看线框；
- P0（焦点不明/溢出/安全区/信息过载）清零再制作。

## 参数与阈值

| 项 | 推荐 |
|---|---|
| 母版数量 | 3–5 |
| 每镜焦点 | 1 |
| 每镜文字块 | ≤3 行 |
| 标题字号 | 72–96px（1080p） |
| 正文字号 | 32–40px |
| 字幕 | 单行 12–16 字 |
| 安全区 | 左右 96px；下 154px |
| 主要动效 | ≤1 个/镜 |
| 同一母版连续使用 | 不超过 3 镜（避免单调） |

## 常见反例

| 反例 | 问题 | 改法 |
|---|---|---|
| 8 镜 8 套版式 | 视觉碎、成本高 | 收敛到 4 母版 |
| 8 镜同一模板 | 没有焦点、像 PPT | 每镜换焦点/结构 |
| 先做动画再想构图 | 返工大 | 先黑白线框 |
| 一镜两个焦点 | 观众不知道看哪 | 拆镜/压暗一个 |
| 文字溢出/出安全区 | 平台遮挡 | 线框阶段检查 |
| 母版连续用 5 次 | 节奏单调 | 插入对照/清单/数轴变体 |
| 字幕与屏显同句 | 冗余 | 字幕=旁白，屏显=关键词 |

## 验证方式

- 8 张版式卡是否都填了 8 个字段？
- 黑白线框遮住旁白，能否 1 秒说出结论？
- 每镜是否只有一个焦点？
- 母版映射是否覆盖所有 Scene，且没有连续 3 镜以上同构？
- 文字/字幕是否在安全区？
- Agent/人工评审 P0 是否为 0？

## 关联条目

- [常用视频版式](layout-patterns.md)
- [脚本调研 SOP](script-research-sop.md)
- [单行字幕与持续动效](caption-motion-continuity.md)
- [Agent 评审团](agent-review-panel.md)
- 案例：[初中数学第一课版式卡](../../research/2026-11-05-初中数学第一课-版式卡v1.md)

## 来源

1. [常用视频版式](layout-patterns.md)：20 种版式/6 族/选型规则。
2. Mayer, R. E. *Multimedia Learning*；[Using multimedia for e-learning (2017)](https://onlinelibrary.wiley.com/doi/10.1111/jcal.12197)。
3. Sweller, J. 认知负荷理论；[ScienceDirect 综述](https://www.sciencedirect.com/science/article/abs/pii/S0747563220302557)。
4. Wiggins, G. & McTighe, J. *Understanding by Design*（逆向设计）。
5. [creator-playbook](https://github.com/chukeru1993/creator-playbook)：7 种镜头语法。
6. [explainer-scenes](https://github.com/kaienzo-ai/explainer-scenes)：8 种修辞场景。
7. [video-layout](https://github.com/guanyang/open-agent-hub/blob/ce4f3ce64873e6e36e5eee84d077d572e24e90b1/skills/remotion/rules/video-layout.md)：一镜一焦点/安全区/时间解决拥挤。
