---
title: 团队协作与 Agent 分工
type: doc
status: 可用
updated: 2026-11-03
owner: lead
---

# 团队协作与 Agent 分工

> 本文件定义「谁写什么、怎么交接、怎么验收」。多 Agent 并行时，**边界清晰 > 沟通勤奋**。

---

## 1. 角色

| 角色 | 职责 | 产出 | 不做什么 |
|---|---|---|---|
| Lead | 架构、规范、模板、任务拆分、验收、索引与提交 | docs / templates / scripts / 索引 / 验收记录 | 不替成员写条目（除非救火） |
| 库调研 Agent | 开源库调研、能力矩阵、选型指南 | `knowledge/开源库/**`、调研笔记 | 不写 SOP / 技能 |
| 方法论 Agent | 方法论与工作流条目 | `knowledge/方法论/**`、`knowledge/工作流/**` | 不碰库条目 |
| SOP Agent（短 / 长） | 按形态写 SOP | `sop/short-*.md` / `sop/long-*.md` | 不新增公共工作流 |
| Skill Agent | 把 SOP / 工作流封装为可加载技能 | `skills/**` | 不重复知识库内容 |
| 质检 Agent（后续） | 独立抽检、跑实测、提返工 | 质检报告 / 实测记录 | 不直接改内容，只提问题 |
| 实测 Agent（后续） | 用真实素材跑端到端 demo | 样片 + 实测记录 + 缺陷单 | 不改规范 |

---

## 2. 阶段与并行度

```text
P0 骨架（Lead 独占）→ P1 内容（4–5 Agent 并行，写域互斥）
→ P1.5 Lead 验收 + 修漏 → P2 端到端实测（1 实测 Agent + Lead）
→ P3 产线化（按视频形态编排 Agent，质检 Agent 独立）
```

并行原则：

1. **写域互斥**：同一时刻一个文件只有一个作者。
2. **共享部分 Lead 先写**：规范、模板、公共工作流先落地，再放并行。
3. **依赖用任务阻塞表达**：SOP 依赖工作流条目时，任务卡写 `blocked_by`。
4. **单卡 ≤ 1 个交付单元**（一条 SOP / 一个技能包 / 3–5 个库条目）。

---

## 3. 任务板规则

- 立项：Lead 用 `team_task_create`，写清 `subject` / `description`（含验收标准）/ `write_scopes` / `blocked_by`。
- 认领：Agent `team_task_list` → `team_task_get` 取 revision → `team_task_update(action="claim", expected_revision=rev)`。
- 执行：只改 scope 内文件；跨域先留言。
- 完成：自检通过 → 任务卡写「产出 / 验证 / 遗留」→ `action="complete"`。
- 阻塞：不要静默停下；卡里写阻塞原因 + 需要谁做什么。

任务卡描述模板：

```text
目标：<一句话>
交付物：<文件清单>
验收：
1. validate.py 0 error
2. <本条特有标准>
3. 至少 <N> 条可用质量
写域：<scope>
依赖：<无 / task-id>
```

---

## 4. 交接与冲突

- **交接**：文件 + 状态 + 验证方式 + 遗留问题，四件套缺一不可。
- **冲突**：发现别人正在改同一文件 → 停手 → 任务卡记录 → 等 Lead。
- **返工**：Lead 给「文件 + 节 + 问题 + 期望」，不要只说“再改改”。
- **升级**：规范不清 / 范围爆炸 / 事实无法确认 → 升级 Lead，不自行发明规则。

---

## 5. 当前编制（2026-11-03）

| 成员 | 职责 | 写域 |
|---|---|---|
| lead | 架构、规范、验收、索引 | docs/ templates/ scripts/ team/ knowledge/环境/ skills/README + 示例技能 |
| lib-scout | 库调研 | knowledge/开源库/ research/ |
| method-writer | 方法论 / 工作流 | knowledge/方法论/ knowledge/工作流/ |
| sop-short | SOP 短形态 | sop/short-*.md |
| sop-long | SOP 长形态 | sop/long-*.md |
| skill-writer | 技能 | skills/（示例技能除外） |

> 2026-11-03 P1：6 名成员全部完成交付，任务板 task-1 ~ task-5 均为 completed；结果见 [P1 验收记录](验收记录-P1.md)。

---

## 6. 后续扩展角色（P2 / P3）

| 角色 | 触发条件 | 主要价值 |
|---|---|---|
| 实测 Agent | 进入 P2 | 用真实素材验证 SOP，产出可复现记录 |
| 质检 Agent | 条目 > 40 或并行 Agent > 5 | 独立抽检，避免作者自评偏差 |
| 素材 / 版权 Agent | 需要外部素材 | 素材来源合规、授权记录 |
| 平台规格跟踪 Agent | 平台规则变动 | 定期核对分辨率 / 时长 / 码率 / 审核规则 |
| 成片复盘 Agent | 有发布数据后 | 用数据回流修正 SOP 与钩子方法论 |

---

## 7. 沟通约定

- 任务相关：写任务卡，不写私聊（可追溯）。
- 需要 Lead 决策：一条消息说清「现状 / 选项 / 建议 / 影响」。
- 完成汇报格式：`产出：…；验证：…；遗留：…`。
- 不刷“收到 / 在做了”；只在状态变化时更新。
