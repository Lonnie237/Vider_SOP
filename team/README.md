# team/ · 组织与协作

> 原则见 [docs/团队协作与Agent分工.md](../docs/团队协作与Agent分工.md)。本页维护**当前编制、任务板快照与验收/交接记录**。

## 当前编制（2026-11-03，P1 收尾）

| 成员 | 角色 | 本轮交付 | 状态 |
|---|---|---|---|
| lead | 架构 / 规范 / 模板 / 校验 / 验收 / 索引 | docs 6 篇、templates 7 份、scripts 2 个、示例技能 1 个、环境条目 1 条 | ✅ |
| lib-scout | 库调研 | 8 个库条目 + capability-matrix + selection-guide + 调研笔记 | ✅ task-1 |
| method-writer | 方法论 / 工作流 | 6 条方法论 + 4 条工作流 | ✅ task-2 |
| sop-short | SOP（轻量形态） | 口播 / 混剪 / 切片 / Vlog 4 条 | ✅ task-3 |
| sop-long | SOP（重流程形态） | 教程 / 访谈 / 宣传片 / 数据动画 4 条 | ✅ task-4 |
| skill-writer | 技能包 | 项目初始化 / 渲染 / 字幕 / 质检 4 个 | ✅ task-5 |

## 任务板快照（2026-11-03 收尾）

| 任务 id | 内容 | 负责人 | 状态 |
|---|---|---|---|
| task-1 | 开源库 8 条 + 能力矩阵 + 选型指南 + 调研笔记 | lib-scout | ✅ completed |
| task-2 | 方法论 6 条 + 工作流 4 条 | method-writer | ✅ completed |
| task-3 | SOP：口播 / 混剪 / 切片 / Vlog | sop-short | ✅ completed |
| task-4 | SOP：教程 / 访谈 / 宣传片 / 数据动画 | sop-long | ✅ completed |
| task-5 | 技能：项目初始化 / 渲染 / 字幕 / 质检 | skill-writer | ✅ completed |

> 权威状态以共享任务板（`team_task_list`）为准；本表是快照。

## P1 验收结果

| 指标 | 结果 |
|---|---|
| 知识条目 | 34（32 可用 / 2 已验证 / 0 草稿） |
| SOP | 11（短 4 + 长 7，全部可用） |
| 技能包 | 5（4 个含可运行脚本 + 1 个示例） |
| 模板 / 规范 | 7 / 6 篇 |
| 门禁 | `validate.py --strict` 0 error / 0 warning；索引最新 |
| 可用以上占比 | 100%（45/45，知识 + SOP） |

详细记录见 [P1 验收记录](../docs/验收记录-P1.md)。

## 交接记录

| 日期 | 从 → 到 | 内容 | 验证 |
|---|---|---|---|
| 2026-11-03 | lead → 全组 | 规范、模板、校验脚本、示例技能、任务卡 | `validate.py` 基线通过 |
| 2026-11-03 | 全组 → lead | 21 知识 + 8 SOP + 5 技能 | 各任务卡自检 + Lead 抽检 |
| 2026-11-03 | lead | 统一索引、修复链接、提交 | `validate.py --strict` 0/0 |

## 下一阶段（P2 建议）

> **P2 样板已完成**：口播知识 34.7s、数据动画三种图表（条形/折线/环图）、Remotion 科普样片 102.9s（WorkBuddy vs Qoder v3.3）均跑通，QC PASS。见 [pipeline/README.md](../pipeline/README.md)、`pipeline/runs/demo-*` 与 [kepu-compare](../pipeline/remotion/kepu-compare/)。下一步：真实素材/数据、HyperFrames 原型、更多图表类型。

1. **实测 Agent**：用真实素材端到端跑 `sop/short-oral-knowledge` 与 `sop/long-tutorial`，把状态升到「已验证」并回填工时基线。
2. **补缺条目**：whisperx / scenedetect / manim（S7 转写、S9 数据动画）；moviepy / pyav / auto-editor / OTIO 安装后补实测。
3. **质检 Agent**：对全部知识条目（当前 34 条）做独立抽检（每类 ≥1 条），重点核对平台参数与版本事实。
4. **P3 产线**：按视频形态编排 Agent（选题 → 脚本 → 素材 → 剪辑 → 质检），每类形态一条固定流水线。

## 沟通渠道

- 任务相关：共享任务板（可追溯）。
- 需要决策：发 Lead，格式「现状 / 选项 / 建议 / 影响」。
- 完成汇报：`产出 / 验证 / 遗留` 三段式。