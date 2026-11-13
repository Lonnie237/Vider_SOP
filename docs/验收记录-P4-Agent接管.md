# P4 · Agent 接管 S1 脚本阶段（第一块）

- 日期：2026-11-13
- 目标：让「Agent 产线」真的由 Agent 产出，而不是脚本模板
- 结论：**S1 脚本阶段 Agent 接管成功，端到端 QC PASS**；P4 第 4 条从 ❌ 升为 🟡。

## 1. 做了什么

| 组件 | 文件 | 作用 |
|---|---|---|
| Agent 阶段工具 | pipeline/agent_stage.py | emit 提示词 + 校验 Agent 写回的 brief + 防原样返回 + 写 lock |
| Agent 流水线定义 | pipeline/definitions/short-oral-knowledge-agent.json | brief 指向 Agent 产物，后续阶段复用 |
| Agent 产物 | pipeline/demo/brief-agent-s1.json | 由子 Agent 独立写回的 9-beat 口播稿 |
| 校验 | agent_stage --check | 结构/钩子/字数/时长/CTA/改动量 |
| 产线 | run_agent_pipeline | 任务板 + 阶段执行 + QC + 复盘 |

## 2. 真实 Agent 过程

1. Lead 把角色卡 + 约束发给子 Agent（编导角色）；
2. 子 Agent 独立写 brief-agent-s1.json（10 beats）；
3. 首轮 check：PASS，但 TTS 实测 39.0s，QC 时长 FAIL；
4. Lead 把「实际 39.0s」反馈给子 Agent；
5. 子 Agent 删 1 个 beat、改 2 句，9 beats；
6. 二轮 check：PASS（预估 32.8–36.8s，9/9 beats 与模板不同）；
7. 产线跑完：实际 36.8s，QC PASS。

## 3. 证据

- check：status=PASS, beats=9, changed=9, range=32.8–36.8s, target=36s
- 成片：36.8s / 2.9 MB / 1080×1920 / -14.2 LUFS
- QC：**PASS**（18 PASS / 0 FAIL / 1 SKIP）
- 字幕：18 条；时长 36.8s 在 36±2s 内
- 复盘：pipeline/runs/demo-oral-agent/_pipeline/retro.md

## 4. 关键设计

- **防原样返回**：content+beats 与模板完全一致 → FAIL；
- **改动量检查**：至少 6 个 beat 与模板不同，否则 warning；
- **时长闭环**：check 用 4.8 字/秒估算，并给 +12% TTS 区间；仍以实测 QC 为准；
- **lock**：check 通过才写 agent-lock，后续阶段才允许跑。

## 5. 还没做

- 只有 S1 是 Agent 产出；S2–S7 仍是脚本；
- 没有四个形态闭环；
- 没有真实素材；
- 没有发布数据回流。

## 7. S3 视觉方案 Agent 接管（第二块）

- 子 Agent 读 brief + 版式能力，写 pipeline/demo/visual-plan.json；
- 9 个 beat 全覆盖；layout：center 4 / top 3 / bottom 2；accent 全部在允许集合；
- 校验：agent_stage --stage S3-visual --check PASS；
- S3 渲染消费该方案；修了 top 布局 index 与标题重叠的问题；
- 全流程跑完：36.8s / QC PASS（18 PASS / 0 FAIL / 1 SKIP）。

## 6. 下一步

1. 让 Agent 接管 S5 字幕断句；
2. 再接管 S6 导出规格；
3. 四类形态各跑一条 Agent 版；
4. 接发布数据回流。