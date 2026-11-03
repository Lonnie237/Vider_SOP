---
name: video-project-init
description: "当开始一条新视频、需要新建项目目录与立项文档（项目Brief、分镜表、交付规格、QC清单）时使用；也用于把交付规格固化成 manifest.json，供 ffmpeg-render 与 qc-deliver 自动读取。输入项目名、视频形态、目标平台即可生成 01-素材/02-工程/03-导出/04-字幕/05-交付 五级目录，并渲染仓库 templates/ 中的模板。"
version: 0.1.0
---

# video-project-init · 视频项目初始化

> 一次输入，生成可执行的项目骨架：目录、立项文档、交付规格、机器可读 manifest。模板来自仓库 `templates/`，不复制死内容。

## 何时使用

- 新项目开工，还没有目录、Brief、分镜表或交付规格。
- 要把交付规格固定下来，让渲染（ffmpeg-render）和质检（qc-deliver）读同一份参数。
- 多项目并行，希望目录结构与文档字段保持一致。
- 模板更新后，希望新项目自动跟随最新模板，而不是手抄旧版本。

## 不适用

- 项目已存在，只想导出成片：用 ffmpeg-render 技能。
- 只有一条临时视频、不需要立项文档：直接 ffmpeg 即可。
- 跨机器同步、权限管理、云端协作：本技能只写本地目录。
- 修改模板本身：`templates/` 由仓库维护者负责，技能只读取。
- 素材整理、剪辑、转码：先立项，再按 SOP 执行。

## 输入（缺什么问什么）

| 输入 | 必填 | 默认值 / 取值 | 说明 |
|---|---|---|---|
| `--name` | 是 | — | 项目名；用于标题与默认目录名 |
| `--form` | 是 | 口播知识 / 混剪卡点 / 教程长视频 / Vlog / 访谈 / 宣传片 / 数据动画 | 别名：教程→教程长视频、口播→口播知识、vlog→Vlog |
| `--platform` | 是 | 抖音 / 视频号 / 小红书 / B站 / YouTube / 客户交付 | 决定画幅、分辨率、帧率、响度默认档 |
| `--root` | 否 | 当前目录 | 项目目录的父目录 |
| `--duration` | 否 | 按形态：口播/宣传片/数据动画 60s、混剪 30s、Vlog 180s、教程/访谈 300s | 目标成片时长（秒） |
| `--width` / `--height` / `--fps` | 否 | 按平台档 | 覆盖平台默认，如竖屏 1080×1920 / 30fps |
| `--video-bitrate` | 否 | 按平台档（6000–12000 kbps） | 本仓默认档，非平台官方值 |
| `--crf` | 否 | 23 | 备选质量档（渲染时可选 CRF 而非码率） |
| `--loudness` | 否 | 竖屏平台 -14 LUFS、横屏/客户 -16 LUFS | 响度目标 |
| `--owner` | 否 | 当前系统用户 | 负责人 |
| `--delivery-date` | 否 | 空 | `YYYY-MM-DD`；为空会写进 manifest 的 `open_questions` |
| `--date` | 否 | 今天 | 生成日期，仅影响文档落款与文件名示例 |
| `--templates` | 否 | 自动定位仓库 `templates/` | 模板目录；找不到会明确报错 |

平台默认档是**本仓默认档**：分辨率/帧率/响度用于自动化；码率不是平台官方推荐值，生成文档中标注 `[待确认]`，发布前必须按平台说明核对。

## 步骤

1. 先判断「形态 × 平台」是否匹配：竖屏形态（口播/混剪/数据动画）配横屏平台（B站/YouTube/客户交付）时先确认画幅，别默认硬套。
2. 干跑，确认要创建的目录与文件（不落盘）：

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness
python3 skills/video-project-init/scripts/init_project.py \
  --name "三分钟讲清楚代理剪辑" --form 口播知识 --platform 抖音 \
  --root /tmp/demo --dry-run
```

3. 正式生成（去掉 `--dry-run`；默认日期为今天，可用 `--date` 固定）：

```bash
python3 skills/video-project-init/scripts/init_project.py \
  --name "三分钟讲清楚代理剪辑" --form 口播知识 --platform 抖音 \
  --root /tmp/demo --date 2026-11-03
```

4. 验收目录与 manifest：

```bash
find "/tmp/demo/三分钟讲清楚代理剪辑" -maxdepth 2 -type d | sort
python3 -c "import json;m=json.load(open('/tmp/demo/三分钟讲清楚代理剪辑/manifest.json'));print(m['project']['platform'], m['delivery_spec']['width'], m['delivery_spec']['loudness_lufs'])"
```

5. 补人工字段：`项目Brief.md` 的目标/受众/内容骨架、`分镜表.md` 的镜头、`05-交付/交付规格.md` 的平台码率核对。脚本只填已知字段，留空处是设计，不是缺漏。
6. 衔接后续技能：渲染用 ffmpeg-render 读 `manifest.json` 或 `05-交付/交付规格.md`；质检用 qc-deliver 读 `delivery_spec` / `duration_target_s` / `max_size_mb`。

常用变体：

```bash
# 覆盖平台默认值（例：Vlog 形态临时按竖屏交付）
python3 skills/video-project-init/scripts/init_project.py \
  --name "露营一日" --form Vlog --platform 抖音 \
  --width 1080 --height 1920 --fps 30 --loudness -14 --root /tmp/demo

# 只输出 manifest（便于脚本消费）
python3 skills/video-project-init/scripts/init_project.py \
  --name demo --form 口播知识 --platform B站 --json --dry-run

# 写入已存在的非空目录（只覆盖同名文件，不删除其他内容）
python3 skills/video-project-init/scripts/init_project.py \
  --name demo --form 口播知识 --platform 抖音 --root /tmp/demo --force
```

## 输出格式

- 目录（15 个，含子目录）：

```text
<项目目录>/
├── 项目Brief.md
├── 分镜表.md
├── manifest.json
├── 01-素材/{视频,音频,图片}/
├── 02-工程/{工程文件,proxy}/
├── 03-导出/{preview,master}/
├── 04-字幕/{srt,png}/
└── 05-交付/{交付规格.md,QC清单.md,final}/
```

- `manifest.json` 顶层字段：`schema_version`、`generated_at`、`generator`、`project`、`directories`、`files`、`delivery_spec`、`platform_defaults_note`、`open_questions`、`templates_used`、`tool_versions`。
- `delivery_spec` 关键字段：`width` `height` `fps` `video_codec` `video_bitrate_kbps` `crf` `audio_codec` `audio_sample_rate` `audio_channels` `audio_bitrate_kbps` `loudness_lufs` `container` `duration_target_s` `max_size_mb` `naming`。
- 终端摘要示例：`项目已初始化：/private/tmp/skillw-doc/demo`，随后列出目录、文件与 `待确认` 项。
- 退出码：`0` 成功；`2` 参数/平台/模板/目录错误（stderr 以「错误：」开头）。

## 失败处理

| 情况 | 现象 | 处理 |
|---|---|---|
| 依赖缺失 | `找不到模板目录` / `读取模板失败` | 确认仓库 `templates/` 四份模板齐全；或用 `--templates` 指向正确目录 |
| 滤镜不可用 | 不适用：本技能不调用 FFmpeg 滤镜 | 仅记录 `tool_versions.ffmpeg`；即使 ffmpeg 缺失也能生成目录与文档，值记为 null |
| 路径不存在 | `目标路径已存在且不是目录` / 父目录不可写 | 换 `--root` 指向可写目录；确认路径拼写 |
| 参数越界 | `--duration 越界：0（允许 1–7200 秒）`、`--width 越界`、`--crf 越界` 等 | 按报错区间调整：宽 64–7680、高 64–4320、帧率 1–240、CRF 0–51、响度 -70–0 LUFS、码率 100–200000 kbps |
| 平台/形态不支持 | `不支持的形态` / `不支持的平台` | 用 `--help` 列出的取值；新形态先提任务补映射，不要硬编 |
| 目标目录已存在 | `目标目录已存在且非空` | 换 `--dir-name`，或确认后加 `--force`（只覆盖同名文件） |
| 模板结构变化 | `模板结构变化：找不到表格行「…」` | 模板被改过；请维护者核对 `templates/`，或提 issue 说明改了什么 |
| 权限不足 | `Permission denied` | 换可写 `--root`；不要用 sudo 写项目目录 |
| 日期格式错误 | `--date 需要 YYYY-MM-DD 格式` | 用 `2026-11-03` 这类格式 |

## 自检

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness

# 1) 参数与帮助
python3 skills/video-project-init/scripts/init_project.py --help >/dev/null && echo HELP_OK

# 2) 干跑：不落盘
python3 skills/video-project-init/scripts/init_project.py \
  --name demo --form 口播知识 --platform 抖音 --root /tmp/skillw-doc --date 2026-11-03 --dry-run

# 3) 实跑并核对（先清理上次自检路径，仅测试目录）
rm -rf /tmp/skillw-doc/demo
python3 skills/video-project-init/scripts/init_project.py \
  --name demo --form 口播知识 --platform 抖音 --root /tmp/skillw-doc --date 2026-11-03
find /tmp/skillw-doc/demo -type d | wc -l
find /tmp/skillw-doc/demo -type f | wc -l
python3 -c "import json;m=json.load(open('/tmp/skillw-doc/demo/manifest.json'));print(m['project'], m['delivery_spec']['width'], m['delivery_spec']['loudness_lufs'])"

# 4) 重复生成应被拒绝，而不是静默覆盖
python3 skills/video-project-init/scripts/init_project.py \
  --name demo --form 口播知识 --platform 抖音 --root /tmp/skillw-doc --date 2026-11-03
```

[实测] 2026-11-03，本机 Python 3.9.6 / macOS M5，模板取自仓库 `templates/`：

| 用例 | 命令要点 | 结果 |
|---|---|---|
| 帮助 | `--help` | 退出码 0 |
| 干跑 | `--dry-run` | 列出 15 个目录、5 个文件，未写磁盘 |
| 实跑 | `--name demo --form 口播知识 --platform 抖音 --root /tmp/skillw-doc` | 创建 16 个目录（含项目根）、20 个文件（5 文档 + 15 个 .gitkeep） |
| manifest | 读取 `manifest.json` | platform=抖音、width=1080、loudness_lufs=-14、open_questions 4 项 |
| 重复运行 | 不加 `--force` | 退出码 2，提示「目标目录已存在且非空」 |
| 非法形态 | `--form unknown` | 退出码 2，列出可选形态 |
| 时长越界 | `--duration 0` | 退出码 2，提示允许 1–7200 秒 |

自检清单：

- [ ] 干跑列出的目录/文件与实跑结果一致
- [ ] `manifest.json` 的 `delivery_spec` 与 `05-交付/交付规格.md` 主规格逐项一致
- [ ] 生成的 Brief/分镜表/QC 清单内链接指向项目内文件（模板仓内链接已被改写）
- [ ] 重复运行不会静默覆盖；需要覆盖时明确用 `--force`
- [ ] 带 `待确认` 的字段（平台码率、交付日期、参考视频）已有人认领

## 参考

- 脚本：[scripts/init_project.py](scripts/init_project.py)
- 模板：[项目Brief](../../templates/项目Brief.md)、[分镜表](../../templates/分镜表.md)、[交付规格](../../templates/交付规格.md)、[QC清单](../../templates/QC清单.md)
- 后续渲染：[ffmpeg-render](../ffmpeg-render/SKILL.md)
- 本机环境基线：[knowledge/环境/environment-local.md](../../knowledge/环境/environment-local.md)
- 技能索引与目录规范：[skills/README.md](../../skills/README.md)
- 验收标准：[docs/质量门禁.md](../../docs/质量门禁.md)
