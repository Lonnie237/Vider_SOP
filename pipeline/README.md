# pipeline/ · 端到端流水线 + P3 Agent 产线

> 这一层不是新工具，而是把 SOP + 技能 + ffmpeg/Pillow/TTS **串成可重复执行的流水线**：每个阶段一个脚本、一个角色、一个输入输出契约，可单独重跑、可交给不同 Agent。
>
> **P3 起，所有流水线统一走 Agent 产线调度器**：任务板 + 阶段执行 + 质检门禁 + 复盘闭环。

## P3 Agent 产线（2026-11-13）

| 组件 | 文件 | 作用 |
|---|---|---|
| 定义 | `definitions/*.json` | 阶段、角色、脚本、SOP、运行目录、brief |
| 任务板 | `board.py` | 认领/开始/完成/失败/阻塞 + 复盘草稿 |
| 调度器 | `run_agent_pipeline.py` | 一条命令跑完：init → 逐阶段 → QC → retro |
| 阶段执行 | `orchestrator.py` | 单阶段/续跑/只跑某段/打印提示词 |
| 复盘 | `<run>/_pipeline/retro.md` | 尝试次数、返工点、门禁结论 |

### 一条命令

```bash
cd vider_harness
python3 pipeline/run_agent_pipeline.py --pipeline pipeline/definitions/short-oral-knowledge.json
python3 pipeline/run_agent_pipeline.py --pipeline pipeline/definitions/data-viz-line.json --force
python3 pipeline/run_agent_pipeline.py --pipeline ... --from S4-audio --force   # 断点续跑
python3 pipeline/run_agent_pipeline.py --pipeline ... --only S7-qc             # 只跑质检
python3 pipeline/run_agent_pipeline.py --pipeline ... --dry-run                # 只看计划
```

### 任务板

```bash
python3 pipeline/board.py --pipeline ... --list          # 看任务
python3 pipeline/board.py --pipeline ... --claim S2-voice --owner 配音
python3 pipeline/board.py --pipeline ... --start
python3 pipeline/board.py --pipeline ... --done S2-voice --note "34.7s，27 条字幕"
python3 pipeline/board.py --pipeline ... --fail S5-subtitle --note "越界 2 条"
python3 pipeline/board.py --pipeline ... --status        # 数据 + 门禁
python3 pipeline/board.py --pipeline ... --retro         # 生成复盘
```

### 门禁规则

- 阶段顺序执行；前一段失败即停，后续任务保持 pending；
- 失败阶段记录 attempts + note，复盘里列入「返工点」；
- 全部阶段 done 才显示「门禁：可完成」；
- 质检阶段（S7-qc / S8-qc）由 `skills/qc-deliver` 给出 PASS/FAIL，FAIL 不进交付。

### 实测（2026-11-13，本机）

| 流水线 | 阶段 | 结果 |
|---|---|---|
| 口播知识 | 8 | 全部 done，QC PASS；34.7s / 2.7 MB；S5 烧录 33.6s 是瓶颈 |
| 数据动画 · 折线 | 9 | 全部 done，QC PASS；33.6s / 2.2 MB；D4 渲染 1008 帧 |
| 数据动画 · 条形竞速 | 9 | 全部 done，QC PASS |
| 数据动画 · 环图 | 9 | 全部 done，QC PASS |

复盘样例：`pipeline/runs/demo-oral/_pipeline/retro.md`、`pipeline/runs/demo-data-viz-line/_pipeline/retro.md`。

## P4 · Agent 接管 S1（2026-11-13）

- 工具：pipeline/agent_stage.py（emit/check/lock）
- 定义：pipeline/definitions/short-oral-knowledge-agent.json
- Agent 产物：pipeline/demo/brief-agent-s1.json（9 beats，与模板 9/9 不同）
- 实测：36.8s / QC PASS；首轮 39.0s FAIL，Agent 按实测反馈缩短后通过
- S3 视觉方案：pipeline/demo/visual-plan.json（子 Agent 产出，9 beats / 3 种 layout）
- S5 字幕方案：pipeline/demo/subtitle-plan.json（子 Agent 产出，9 beats / 15 条字幕）
- 验收：docs/验收记录-P4-Agent接管.md

## 四条样板流水线

| 流水线 | 定义 | 画幅 | 成片 | 状态 |
|---|---|---|---|---|
| 口播知识 | [definitions/short-oral-knowledge.json](definitions/short-oral-knowledge.json) | 1080×1920 | 34.7s / QC PASS | ✅ |
| 数据动画 · 条形竞速 | [definitions/data-viz-animation.json](definitions/data-viz-animation.json) | 1920×1080 | 37.6s / QC PASS | ✅ |
| 数据动画 · 折线/面积 | [definitions/data-viz-line.json](definitions/data-viz-line.json) | 1920×1080 | 33.6s / QC PASS | ✅ |
| 数据动画 · 环图 | [definitions/data-viz-donut.json](definitions/data-viz-donut.json) | 1920×1080 | 23.2s / QC PASS | ✅ |
| 数据动画 · 真实数据 | [definitions/data-viz-real.json](definitions/data-viz-real.json) | 1920×1080 | 36.2s / QC PASS | ✅ |

## 快速开始（原 orchestrator）

```bash
python3 pipeline/orchestrator.py                                             # 口播知识样板
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-line.json
python3 pipeline/orchestrator.py --pipeline ... --plan
python3 pipeline/orchestrator.py --pipeline ... --only D4-render --force
python3 pipeline/orchestrator.py --pipeline ... --emit-prompt S5-subtitle
```

## 示例运行结果（2026-11-03，本机）

| 项 | 结果 |
|---|---|
| 成片 | `pipeline/runs/demo-oral/05-交付/final/oral-hook-3s-v1-2026-11-03.mp4` |
| 时长 / 大小 | 34.7s / 2.8 MB |
| 规格 | 1080×1920 / 30fps / H.264 + AAC 48kHz / -14.2 LUFS |
| 质检 | **PASS**（18 PASS / 0 FAIL / 1 SKIP） |
| 全流程耗时 | 约 60s（字幕烧录约 39s，是当前瓶颈） |

## 代码化科普 demo（Remotion）

- 项目：[pipeline/remotion/kepu-compare](remotion/kepu-compare/)（WorkBuddy vs Qoder v3.3，102.9s / 1920×1080 / -16 LUFS，含封面）
- 方法：声音为轴 → 时间轴 → React 场景/字幕/动效；事实台账见项目 `FACTS.md`