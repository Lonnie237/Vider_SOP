# pipeline/ · 端到端流水线（口播知识 / 数据动画）

> 这一层不是新工具，而是把 [SOP](../sop/short-oral-knowledge.md) + [技能](../skills/README.md) + ffmpeg/Pillow/TTS **串成可重复执行的流水线**：每个阶段一个脚本、一个角色、一个输入输出契约，可单独重跑、可交给不同 Agent。

## 四条样板流水线

| 流水线 | 定义 | 画幅 | 成片 | 状态 |
|---|---|---|---|---|
| 口播知识 | [definitions/short-oral-knowledge.json](definitions/short-oral-knowledge.json) | 1080×1920 | 34.7s / QC PASS | ✅ |
| 数据动画 · 条形竞速 | [definitions/data-viz-animation.json](definitions/data-viz-animation.json) | 1920×1080 | 37.6s / QC PASS | ✅ |
| 数据动画 · 折线/面积 | [definitions/data-viz-line.json](definitions/data-viz-line.json) | 1920×1080 | 33.6s / QC PASS | ✅ |
| 数据动画 · 环图 | [definitions/data-viz-donut.json](definitions/data-viz-donut.json) | 1920×1080 | 23.2s / QC PASS | ✅ |

数据动画流水线参考了 [code-video-showcase](https://github.com/Moessif/code-video-showcase) 的「帧 = f(t)、剪辑表驱动、逐帧渲染、帧数校验」方法，见 [调研笔记](../research/2026-11-03-code-video-showcase.md) 与 [纯代码视频管线](../knowledge/工作流/code-video-pipeline.md)。

## 快速开始

```bash
# 口播知识样板
python3 pipeline/orchestrator.py

# 数据动画样板（三种图表，共用同一条流水线）
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json  # 条形竞速
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-line.json       # 折线/面积
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-donut.json      # 环图

# 看阶段 / 只跑某段 / 从某段续跑
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json --plan
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json --only D4-render --force
python3 pipeline/orchestrator.py --pipeline pipeline/definitions/data-viz-animation.json --from D4-render --force

# 产出位置
#    pipeline/runs/demo-oral/05-交付/final/*.mp4
#    pipeline/runs/demo-data-viz/05-交付/final/*.mp4
#    */_pipeline/run-report.md
```

重跑与局部调试：

```bash
python3 pipeline/orchestrator.py --force                 # 覆盖重跑全部阶段
python3 pipeline/orchestrator.py --from S4-audio --force # 从声音阶段续跑
python3 pipeline/orchestrator.py --only S7-qc            # 只跑质检
python3 pipeline/orchestrator.py --emit-prompt S5-subtitle  # 打印该阶段给 Agent 的提示词
```

## 示例运行结果（2026-11-03，本机）

| 项 | 结果 |
|---|---|
| 成片 | `pipeline/runs/demo-oral/05-交付/final/oral-hook-3s-v1-2026-11-03.mp4` |
| 时长 / 大小 | 34.7s / 2.8 MB |
| 规格 | 1080×1920 / 30fps / H.264 + AAC 48kHz / -14.2 LUFS |
| 质检 | **PASS**（18 PASS / 0 FAIL / 1 SKIP；视频码率 472kbps 属静态图文卡的内容适配值） |
| 语速 | 1.45 倍（say -r 261，实测约 1.43×；由 S2 自动校准） |
| 全流程耗时 | 约 60s（其中字幕烧录约 39s，是当前瓶颈） |
| 阶段 | S0–S7 全部 ok，逐阶段耗时见 `_pipeline/run-report.md` |

> 注：demo 为「无实拍素材」模式，码率按图文卡内容自适应为 500kbps 档；实拍成片按 SOP 的 8–16Mbps 执行。

### 数据动画样板结果（2026-11-03）

三种图表类型共用同一条流水线，只改 `brief.dataviz.chart`（`bar-race` / `line` / `donut`）：

| 图表 | 定义 | 成片 | 质检 |
|---|---|---|---|
| 条形竞速 | data-viz-animation.json | 37.6s / 2.4 MB | PASS |
| 折线/面积 | data-viz-line.json | 33.6s / 2.3 MB | PASS |
| 环图 | data-viz-donut.json | 23.2s / 1.5 MB | PASS |

- 共同规格：1920×1080 / 30fps / H.264 + AAC 48kHz / -14.2 LUFS；图形内容码率 330–370kbps（内容适配值）。
- 渲染：Pillow 逐帧 → ffmpeg rawvideo 管道；D4 产出 5 张静帧、每秒接触表，并校验帧数 = `round(duration×30)`。
- 数据：`pipeline/demo/data-viz{,-line,-donut}/` 下的 brief + dataset（虚构示例，8 年 × 6 赛道，界面已标「示例数据」）。

**数据动画流水线阶段**：S0 初始化 → S1 旁白校验 → S2 TTS → **D3 数据/故事板**（`stages/d3_data.py`）→ **D4 逐帧渲染**（`stages/d4_render.py`，支持条形竞速/折线/环图）→ S5 响度合板 → S6 字幕烧录 → S7 规格导出 → S8 质检。新角色：分析师 [roles/analyst.md](roles/analyst.md)、动效 [roles/motion.md](roles/motion.md)。

## 代码化科普 demo（Remotion）

- 项目：[pipeline/remotion/kepu-compare](remotion/kepu-compare/)（WorkBuddy vs Qoder，66.0s / 1920×1080 / -16 LUFS）
- 方法：声音为轴 → 时间轴 → React 场景/字幕/动效；事实台账见项目 `FACTS.md`
- 渲染：Remotion 4.0.540 + Chrome for Testing；交付编码后 QC
- 这是 [科普动画 SOP](../sop/short-kepu-motion.md) 的第一个可运行样板

## 口播知识流水线：阶段与角色

| # | 阶段 | 角色 | 脚本 | 输入 → 输出 |
|---|---|---|---|---|
| S0 | 初始化 | 编导 | `stages/s0_init.py` | brief → 项目目录、交付规格、manifest |
| S1 | 脚本校验 | 编导 | `stages/s1_script.py` | brief → 脚本.md、分镜表.md、script.json |
| S2 | 配音 | 配音 | `stages/s2_tts.py` | 口播文本 → voice.wav、逐句时间轴 |
| S3 | 画面 | 剪辑 | `stages/s3_visual.py` | 时间轴 → 图文卡、base.mp4、封面 |
| S4 | 声音 | 声音 | `stages/s4_audio.py` | voice + base → voice_norm、base_av |
| S5 | 字幕 | 字幕 | `stages/s5_subtitle.py` | base_av + 时间轴 → voice.srt、subbed.mp4 |
| S6 | 导出 | 剪辑 | `stages/s6_export.py` | subbed + 交付规格 → 成片 |
| S7 | 质检 | 质检 | `stages/s7_qc.py` | 成片 → QC 报告、成片说明 |

角色卡在 [roles/](roles/)：编导、配音、剪辑、声音、字幕、质检。每个阶段都能以 Agent 身份独立执行（见「Agent 协作模式」）。

## 产物结构

```text
pipeline/runs/demo-oral/
├── manifest.json / 项目Brief.md / 分镜表.md
├── 01-素材/{视频/cards,音频/{beats,voice.wav,voice_norm.wav},图片}
├── 02-工程/{脚本.md,工程文件,proxy}
├── 03-导出/{preview/{base,base_av,subbed}.mp4, master}
├── 04-字幕/{srt/voice.srt, png}
├── 05-交付/{final/<slug>-v1-<date>.mp4, 封面.png, 交付规格.md, QC报告.md, 成片说明.md}
└── _pipeline/{run.json, run-report.md, brief.json, script.json, voice.json, audio.json, subtitle.json, export.json, qc.json, segments/}
```

> `pipeline/runs/` 是运行产物（含媒体），已在 `.gitignore` 中排除，不入库；入库的是流水线定义、阶段脚本、角色卡与 demo 输入。

## Agent 协作模式

流水线的设计目标是「一个阶段 = 一个 Agent 任务」：

1. 编排器按定义顺序执行；每个阶段独立进程、独立退出码。
2. 某个阶段要换人/换 Agent：`--emit-prompt <阶段>` 生成该阶段提示词（角色卡 + 输入输出契约 + 命令）。
3. Agent 执行完只需保证：退出码 0、stdout 末行输出 JSON 摘要、产物落在约定路径。
4. 失败即停：编排器记录失败阶段、stderr 尾部与已产出的上游文件，修好后 `--from <阶段> --force` 续跑。
5. 阶段之间只通过文件和 `_pipeline/*.json` 通信，不共享内存，便于并行与重试。

示例（把字幕阶段交给另一个 Agent）：

```bash
python3 pipeline/orchestrator.py --emit-prompt S5-subtitle > /tmp/subtitle-task.md
# 把 /tmp/subtitle-task.md 交给 Agent；它跑：
# python3 pipeline/stages/s5_subtitle.py --run-dir pipeline/runs/demo-oral --force
```

## 换成真实素材 / 真实配音

| 想替换 | 做法 |
|---|---|
| 选题与口播稿 | 改 `pipeline/demo/brief.json`（或复制一份新 brief，改定义里的 `run.brief` 与 `run.dir_name`） |
| 配音 | S2 的 `--voice` 换音色、`--rate-multiplier` 改语速（默认读 `brief.voice.rate_multiplier=1.45`）；或把 `voice.wav` 换成真人录音后跳过 S2（保持 48 kHz 单声道，并重算时间轴） |
| 画面 | S3 支持替换成实拍：把 `base.mp4` 换成实拍裁切后的无声底片（1080×1920/30fps，时长与 voice.wav 一致），后续阶段不变 |
| 平台规格 | 改 `brief.json` 的 `spec`（分辨率/帧率/码率/响度），manifest 会自动带上 |
| 字幕样式 | S5 的 `burn.py` 参数：字号、位置、底框、安全边距 |

## 与知识库的关系

- 方法依据：[钩子与留存](../knowledge/方法论/hooks-retention.md)、[节奏与卡点](../knowledge/方法论/pacing-beat.md)、[字幕与信息密度](../knowledge/方法论/subtitle-density.md)、[声音设计](../knowledge/方法论/sound-design.md)
- 流程依据：[口播知识 SOP](../sop/short-oral-knowledge.md)
- 复用技能：[video-project-init](../skills/video-project-init/SKILL.md)、[ffmpeg-render](../skills/ffmpeg-render/SKILL.md)、[subtitle-pipeline](../skills/subtitle-pipeline/SKILL.md)、[qc-deliver](../skills/qc-deliver/SKILL.md)
- 环境约束：[本机环境](../knowledge/环境/environment-local.md)（ffmpeg 9.0.2 无 libass，字幕走 Pillow overlay）

## 已知限制

- 示例是「无实拍素材」版本：TTS + 图文卡，适合知识口播的批量模板化；真人出镜仍需替换 S3 素材来源。
- TTS 音色与语气有限（本机 `say`）；商用发布建议换真人配音或高质量 TTS。
- 平台参数（码率/时长/审核）属易变事实，发布前按平台后台核对。
- 字幕烧录走 Pillow overlay，长字幕/复杂样式效率低于 libass；需要复杂字幕时换带 libass 的 FFmpeg 构建。