# vider_harness · 视频编辑知识与 SOP 工作台

[![quality](https://github.com/Lonnie237/Vider_SOP/actions/workflows/quality.yml/badge.svg)](https://github.com/Lonnie237/Vider_SOP/actions/workflows/quality.yml)
[![remote](https://img.shields.io/badge/remote-Lonnie237%2FVider__SOP-d97757)](https://github.com/Lonnie237/Vider_SOP)

> **一句话**：把“做视频”从个人手感，变成**可检索、可复用、可执行、可交给 Agent 跑**的工程资产。

---

## 0. 这个仓库是什么 / 不是什么

**是什么**

- 开源视频编辑**库/工具**的选型目录与最小可用用法（转码、剪辑、合成、字幕、音频、特效、动效、质检）。
- 按**视频形态**拆分的 **SOP**（口播知识、混剪卡点、直播切片、Vlog、教程长视频、访谈播客、产品宣传片、数据可视化动画等），每条 SOP 给阶段、参数、时间预算、质量门禁。
- 可被 DSH Agent 直接加载的 **Skills**（触发条件 + 步骤 + 命令 + 失败处理 + 自检）。
- 支撑以上三者的**模板、校验脚本与协作规范**。

**不是什么**

- 不存大素材与成片（只存索引、工程结构、脚本与规范；媒体文件走项目目录，不入库）。
- 不绑定单一 NLE（Premiere / DaVinci / 剪映 / Final Cut 都能用，接口通过 SOP 与 FFmpeg 命令衔接）。
- 不写“教程体”长文；每个条目以“能否照着干”为验收标准。

---

## 1. 能解决什么问题

| 痛点 | 本仓对应能力 |
|---|---|
| 工具太多，不知道选哪个 | [knowledge/开源库/](knowledge/开源库/) 能力矩阵 + 选型指南 |
| 每次做视频都从零想流程 | [sop/](sop/) 按视频形态路由，直接给阶段、参数、门禁 |
| 经验只存在脑子里 | [knowledge/方法论/](knowledge/方法论/) 结构化沉淀，可引用、可复盘 |
| 交给 Agent 不会干 / 干得不一样 | [skills/](skills/) 技能包 + [scripts/](scripts/) 可执行校验 |
| 不同平台规格记不住 | [templates/交付规格.md](templates/交付规格.md) 与 SOP 内联规格表 |
| 多人 / 多 Agent 协作产出不一致 | [AGENTS.md](AGENTS.md) + [docs/质量门禁.md](docs/质量门禁.md) + [docs/团队协作与Agent分工.md](docs/团队协作与Agent分工.md) |

---

## 2. 目录结构

```text
vider_harness/
├── README.md                 # 你在这里
├── AGENTS.md                 # Agent / 协作者必读的工作手册
├── INDEX.md                  # 全库自动索引（脚本生成）
├── docs/                     # 顶层规范：分类体系、写作规范、质量门禁、团队分工
├── knowledge/                # 知识库
│   ├── 开源库/               #   库与工具条目（含能力矩阵、选型指南）
│   ├── 方法论/               #   叙事、节奏、字幕、声音、调色、脚本等通用方法
│   ├── 工作流/               #   素材管理、代理剪辑、转码交付、自动化流水线、平台规格
│   └── 环境/                 #   本机 / 目标环境、依赖、容量与性能基线
├── sop/                      # 按视频形态拆分的标准作业流程
├── skills/                   # Agent 技能包（每个目录一份 SKILL.md）
├── templates/                # 项目 Brief、分镜、交付规格、QC、知识条目模板
├── research/                 # 调研笔记与来源台账（可追溯）
├── team/                     # 角色、协作流程、任务板与当前编制
├── pipeline/                 # 端到端流水线（口播知识样板：8 阶段 + 角色卡 + 编排器）
└── scripts/                  # validate.py 校验 / build_index.py 索引 / 辅助脚本
```

---

## 3. 怎么用（按角色）

### 3.1 我要做一条视频

1. 打开 [sop/README.md](sop/README.md) 的路由表，按「视频形态 + 平台 + 时长 + 素材条件」选一条 SOP。
2. 用 [templates/项目Brief.md](templates/项目Brief.md) 立项，用 [templates/分镜表.md](templates/分镜表.md) 拆镜。
3. 跟着 SOP 的阶段走；交付前用 [templates/QC清单.md](templates/QC清单.md) 自检。
4. 复盘结论回写到对应 SOP 的「常见问题 / 实测记录」，不要只留在聊天里。

### 3.2 我要选工具 / 写自动化脚本

1. 先看 [knowledge/开源库/capability-matrix.md](knowledge/开源库/capability-matrix.md) 按「环节 × 需求」筛，再用 [selection-guide.md](knowledge/开源库/selection-guide.md) 定组合。
2. 进单条目看「最小可用示例」和「坑位」，确认 license 与维护状态。
3. 自动化首选 **FFmpeg + Python/Node 编排**；交互式创作再上 NLE / Remotion / Blender。

### 3.3 我要跑一条完整流水线（P2 样板）

```bash
python3 pipeline/orchestrator.py --plan   # 看阶段与角色
python3 pipeline/orchestrator.py          # 口播知识 demo，约 60s
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json  # 数据动画：条形竞速
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-line.json       # 数据动画：折线
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-donut.json      # 数据动画：环图
```

产物：`pipeline/runs/demo-oral/`（口播知识）与 `pipeline/runs/demo-data-viz/`（数据动画），含成片、封面、SRT、QC 报告、接触表与运行报告。说明见 [pipeline/README.md](pipeline/README.md)。

### 3.4 我是 Agent

1. 读 [AGENTS.md](AGENTS.md) → [docs/写作与标注规范.md](docs/写作与标注规范.md) → 你的任务卡。
2. 只改任务卡 `write_scopes` 内的文件；跨域必须先在任务板说明。
3. 收工前跑 `python3 scripts/validate.py`，并跑对应 SOP / 技能的自检。
4. 把「做了什么、验证了什么、遗留什么」写回任务卡，不要只说“已完成”。

---

## 4. 内容状态与质量分级

所有知识条目与 SOP 使用三级状态（定义见 [docs/质量门禁.md](docs/质量门禁.md)）：

| 状态 | 含义 | 要求 |
|---|---|---|
| 草稿 | 结构完整、内容待验证 | frontmatter 齐全；允许标注「待补充」 |
| 可用 | 能照着干 | 步骤 / 参数 / 示例完整，来源可查，无死链 |
| 已验证 | 本机或真实项目跑通 | 有实测记录（日期、命令 / 工程、结果），可复现 |

当前（2026-11-05）：知识 35 条（33 可用 / 2 已验证）、SOP 11 条、技能 5 个、流水线 4 条；`python3 scripts/validate.py --strict` 为 0 error / 0 warning。

> 目标不是“写得多”，而是「已验证」条目占比。每次迭代看 [INDEX.md](INDEX.md) 的统计。

---

## 5. 当前进度与路线图

| 阶段 | 内容 | 状态 |
|---|---|---|
| P0 基础骨架 | 规范、模板、校验脚本、索引、示例技能 | **已完成（2026-11-03）** |
| P1 内容填充 | 开源库条目 + 能力矩阵、方法论、工作流、8 类 SOP、5 个技能 | **已完成（2026-11-03）**：35 条知识（含 P2 增补 14 条）/ 11 SOP / 5 技能，全部「可用」以上 |
| P2 端到端实测 | 口播知识 + 数据动画三种图表 + **Remotion 科普样片（102.9s）** 跑通；新增 PPT 转视频 / 产品说明 / 科普动画 SOP | **样例已完成**；待接真实素材/真实数据，HyperFrames 原型待补 |
| P3 Agent 产线 | 按视频形态编排子 Agent，任务板 + 质检 + 复盘闭环 | 待启动 |

任务与编制见 [team/README.md](team/README.md)；本轮验收记录见 [docs/验收记录-P1.md](docs/验收记录-P1.md)。

---

## 6. 质量门禁（所有人）

```bash
python3 scripts/validate.py             # frontmatter / ID / 死链 / 交叉引用 / 必备字段
python3 scripts/build_index.py          # 重建 INDEX.md
python3 scripts/build_index.py --check  # CI：索引是否最新
python3 scripts/healthcheck.py          # 体检：门禁 + 索引 + 计数一致性 + 流水线 + Git
```

**DoD（完成定义）**：格式过校验 → 内容有来源 / 有实测 → 对应用例可执行 → 任务卡写清验证方式。

---

## 7. 协作

- 角色与编制：[team/README.md](team/README.md)
- 分工与任务板规则：[docs/团队协作与Agent分工.md](docs/团队协作与Agent分工.md)
- 新增视频形态：先加路由与 SOP 骨架，再补知识条目（见 [docs/知识分类体系.md](docs/知识分类体系.md)）。
- 远程仓库、分支与 CI：[docs/远程仓库与协作.md](docs/远程仓库与协作.md)（[GitHub](https://github.com/Lonnie237/Vider_SOP)）。

---

## 8. 维护

- 当前维护者：Lead（架构、规范、验收）
- 贡献者：各内容子 Agent（见 [team/README.md](team/README.md) 编制表）
- 每次内容变更：更新条目 `updated` 字段，并在任务卡记录验证方式。