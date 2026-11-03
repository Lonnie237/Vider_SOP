---
name: qc-deliver
description: "当视频成片导出后、上传或交付客户前需要自动验收时使用：用 ffprobe 核验分辨率/帧率/编码/时长/码率/音频声道与采样率，用 loudnorm 实测响度、blackdetect 查黑帧，并检查文件大小与命名规范；读取项目 manifest.json 或 05-交付/交付规格.md，输出 PASS/FAIL 表并以非零退出码阻断不合格交付。适合人工验收与 CI。"
version: 0.1.0
---

# qc-deliver · 交付前自动质检

> 交付前最后一道自动门禁：规格、响度、黑帧、文件大小、命名逐项给 PASS/FAIL；任何一项 FAIL 退出码为 1，可直接接进脚本/CI。

## 何时使用

- 成片导出完成，上传平台或交付客户前做最后核验。
- 客户/平台有明确交付规格（分辨率、帧率、编码、码率、响度、文件大小）。
- 批量交付：对每个成片跑一遍，用退出码判断是否放行。
- 想用机器代替「拿眼睛扫一遍 ffprobe 输出」。
- 需要留一份可存档的质检记录（`--json`）。

## 不适用

- 画面内容审片（构图、表演、错别字、隐私信息）：必须人工看，本脚本只能查黑帧等机器指标。
- 调色、降噪、混音修复：本脚本只报告问题，不做修复。
- 平台审核规则/版权/敏感词：以平台官方规则为准，本脚本不覆盖。
- 没有交付规格的临时视频：请先用 [video-project-init](../video-project-init/SKILL.md) 生成规格，或直接给 `--width/--fps/--duration` 等参数。
- 多文件汇总报表：本脚本一次检查一个文件；批量请用 shell 循环调用。

## 输入（缺什么问什么）

| 输入 | 必填 | 说明 |
|---|---|---|
| 待检视频 | 是 | `--input`；本机文件，支持 ffprobe 能读的封装 |
| 交付规格 | 是（或给覆盖参数） | `--project <项目目录>`（读 `manifest.json` 或 `05-交付/交付规格.md`）或 `--spec <文件>` |
| 覆盖参数 | 否 | `--width --height --fps --video-codec --video-bitrate --audio-codec --sample-rate --channels --audio-bitrate --duration --loudness --max-size-mb --naming-regex` |
| 容差 | 否 | 帧率 ±0.1、时长 ±0.5s、码率 ±35%、响度 ±1.0 LU；可用参数调整 |
| 跳过项 | 否 | `--skip-loudness` / `--skip-blackdetect`（赶时间时先跑规格，交付前必须补跑） |

规格来源优先级：命令行覆盖 > `--spec` > `--project`。没有规格时脚本直接报错退出，不会「静默全 PASS」。

## 步骤

1. 准备交付规格。三种来源任选其一：

```bash
# A. 项目内已有 manifest.json（推荐，video-project-init 生成）
python3 skills/qc-deliver/scripts/qc.py --input out.mp4 --project /tmp/skillw-doc/demo

# B. 直接读 05-交付/交付规格.md（解析表格中的分辨率/帧率/码率/编码/音频/命名）
python3 skills/qc-deliver/scripts/qc.py \
  --input out.mp4 --spec '/tmp/skillw-doc/demo/05-交付/交付规格.md'

# C. 手写最小规格 JSON（适合客户单条需求）
cat > spec.json <<'EOF'
{
  "width": 1280, "height": 720, "fps": 30,
  "video_codec": "h264", "video_bitrate_kbps": 2800,
  "audio_codec": "aac", "audio_sample_rate": 48000,
  "audio_channels": 2, "audio_bitrate_kbps": 192,
  "duration_target_s": 4, "loudness_lufs": -14,
  "max_size_mb": 20, "naming": "demo-<version>-<date>.mp4"
}
EOF
```

2. 跑完整质检（规格 → 响度 → 黑帧 → 大小 → 命名）：

```bash
python3 skills/qc-deliver/scripts/qc.py \
  --input /tmp/skillw-sub/demo-v1-2026-11-03.mp4 \
  --spec /tmp/skillw-sub/spec.json
```

3. 按 FAIL 项修复后重跑（不要靠改规格「绕过」）：

| FAIL 项 | 常见原因 | 修复 |
|---|---|---|
| 分辨率 / 帧率 | 导出参数与规格不一致 | 用 `ffmpeg-render` 按 `manifest.json` 重导 |
| 视频码率 | 码率偏离目标超过容差 | 调整 `-b:v/--video-bitrate`；或确认平台是否真要求固定码率 |
| 音频编码/采样率/声道 | 源音频或导出参数不对 | `-ar 48000 -ac 2 -c:a aac` 重导 |
| 响度 I / 真峰值 | 未做 loudnorm 或目标不同 | `ffmpeg-render --mode loudnorm` 或导出时加 `-af loudnorm` |
| 黑帧 | 片头片尾黑场、素材断档 | 确认是否可接受；片头片尾可 `--allow-black-edges 1.0` |
| 文件大小 | 码率过高/时长过长 | 降码率或分段；先问清平台上限 |
| 命名规范 | 用了 `final`、带空格、缺版本号 | 改名或给 `--naming-regex` |

4. 需要放宽容差或跳过耗时段时（只在确认原因后使用）：

```bash
# 片头留 1 秒黑场是设计，不算 FAIL
python3 skills/qc-deliver/scripts/qc.py --input out.mp4 --project . --allow-black-edges 1.0

# 平台对码率是区间，放宽到 ±50%
python3 skills/qc-deliver/scripts/qc.py --input out.mp4 --project . --bitrate-tolerance 0.5

# 快速迭代时先跳过响度/黑帧；交付前必须去掉这两个参数重跑
python3 skills/qc-deliver/scripts/qc.py --input out.mp4 --project . --skip-loudness --skip-blackdetect
```

5. 接进脚本/CI（退出码 0 = 全过，1 = 有 FAIL，2 = 输入/规格错误）：

```bash
if python3 skills/qc-deliver/scripts/qc.py --input out.mp4 --spec spec.json --json > qc-report.json; then
  echo "QC PASS，可以交付"
else
  echo "QC FAIL，查看 qc-report.json"
  exit 1
fi
```

## 输出格式

- 终端表格（实测样例，节选）：

```text
交付质检：/private/tmp/skillw-sub/demo-v1-2026-11-03.mp4（1.43 MB）
检查项        期望                                  实测                     结果  备注
文件存在      可读文件                              demo-v1-2026-11-03.mp4   PASS
分辨率        1280x720                              1280x720                 PASS
帧率          30fps                                 30fps                    PASS
响度 I        -14 LUFS                              -14 LUFS                 PASS
黑帧          0 段（>=0.5s）                        0 段                     PASS
命名规范      ^demo\-v\d+\-\d{4}-\d{2}-\d{2}\.mp4$  demo-v1-2026-11-03.mp4   PASS

结果：PASS（19 PASS / 0 FAIL / 0 WARN / 0 SKIP）
```

- `--json` 输出结构化报告：`{"input", "spec_source", "status": "PASS|FAIL", "size_mb", "summary": {"PASS", "FAIL", "WARN", "SKIP"}, "checks": [{"name","expected","actual","status","note"}]}`，stdout 只有 JSON，便于管道消费。
- 退出码：`0` 无 FAIL；`1` 至少一项 FAIL；`2` 文件/规格/参数错误（stderr 以「错误：」开头）。

## 失败处理

| 情况 | 现象 | 处理 |
|---|---|---|
| 依赖缺失（FFmpeg） | `找不到 ffmpeg/ffprobe` | 安装 FFmpeg（macOS：`brew install ffmpeg`）；ffprobe 用于读规格，loudnorm/blackdetect 用于实测 |
| 滤镜不可用（loudnorm） | 响度行显示「测量失败」 | 先 `ffmpeg -hide_banner -filters \| grep loudnorm`；缺则 `--skip-loudness` 并在交付记录里注明人工复核 |
| 滤镜不可用（blackdetect） | 黑帧行异常/报错 | 先 `ffmpeg -hide_banner -filters \| grep blackdetect`；缺则 `--skip-blackdetect`，人工抽帧检查 |
| 路径不存在 | `输入文件不存在` / `--spec 指向的文件不存在` | 核对路径；项目没初始化先跑 [video-project-init](../video-project-init/SKILL.md) |
| 参数越界 | `--duration-tolerance 越界` / `--bitrate-tolerance 越界` / `--black-duration 必须 > 0` | 时长容差 0.5–10s、码率容差 0–1、黑帧时长 > 0；响度容差按需调整 |
| 未提供规格 | `没有交付规格`，退出码 2 | 用 `--project/--spec`，或给 `--width/--fps/--duration` 等覆盖参数 |
| 无音轨 | 音频编码/采样率/声道/响度 FAIL | 若成片本应有声，先补音轨重导；若确定静音交付，规格里别要求音频，并去掉响度要求 |
| 黑帧误报 | 片头/片尾黑场被判 FAIL | 确认是设计后加 `--allow-black-edges 1.0`（按实际秒数） |
| 码率读不到 | 视频码率行 SKIP | 部分封装不写 stream bit_rate；改用 `format.bit_rate` 估算或人工核对 |
| 命名误报 | 命名规范 FAIL | 按项目规范改名，或 `--naming-regex` 给准确正则；manifest 的 naming 占位符会自动转正则 |
| 平台参数不一致 | 规格里的码率/时长与平台不符 | 本仓默认档标注 `[待确认]`；以平台官方说明为准，先改交付规格再重跑 |

## 自检

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness

# 1) 帮助
python3 skills/qc-deliver/scripts/qc.py --help >/dev/null && echo HELP_OK

# 2) 合格片：应全 PASS、退出码 0
python3 skills/qc-deliver/scripts/qc.py \
  --input /tmp/skillw-sub/demo-v1-2026-11-03.mp4 \
  --spec /tmp/skillw-sub/spec.json

# 3) JSON 报告：stdout 只有 JSON，退出码不变
python3 skills/qc-deliver/scripts/qc.py \
  --input /tmp/skillw-sub/demo-v1-2026-11-03.mp4 \
  --spec /tmp/skillw-sub/spec.json --json

# 4) 不合格片：故意给错规格，应 FAIL 且退出码 1
python3 skills/qc-deliver/scripts/qc.py \
  --input /tmp/skillw-sub/bad-name.mp4 \
  --spec /tmp/skillw-sub/spec.json --width 1920 --height 1080

# 5) 直接读 05-交付/交付规格.md（Markdown 表格解析；demo-v2 为 1080×1920 样片）
python3 skills/qc-deliver/scripts/qc.py \
  --input /tmp/skillw-sub/demo-v2-2026-11-03.mp4 \
  --spec '/tmp/skillw-doc/demo/05-交付/交付规格.md' --duration 4
```

[实测] 2026-11-03，本机 ffmpeg/ffprobe 9.0.2、Python 3.9.6，测试素材为 `testsrc2` + sine 生成的 1280×720/30fps/4s 视频，以及一段 4s 全黑视频作为反例：

| 用例 | 结果 | 结论 |
|---|---|---|
| 合格片 + spec.json | 19 PASS / 0 FAIL / 0 WARN / 0 SKIP，退出码 0 | 规格、响度、黑帧、命名全部通过 |
| `--json` | status=PASS，summary.PASS=19，退出码 0 | JSON 可被脚本消费 |
| 反例（全黑视频、错规格） | 13 PASS / 6 FAIL，退出码 1 | FAIL 项：分辨率、视频码率、声道、响度、黑帧、命名，逐项有期望/实测 |
| 读 05-交付/交付规格.md | 17 PASS / 0 FAIL / 2 SKIP，退出码 0 | Markdown 表格解析出 1080×1920/30fps/h264/aac/48kHz/-14 LUFS，命名规范也匹配 |
| 输入不存在 | 退出码 2，提示「输入文件不存在」 | 错误早失败，不产出假报告 |
| 未提供规格 | 退出码 2，提示用 --spec/--project 或覆盖参数 | 不会「无规格全 PASS」 |

自检清单：

- [ ] 规格来源正确（manifest / 05-交付/交付规格.md / 手写 JSON），且与项目实际要求一致
- [ ] FAIL 数量为 0 才允许交付；不要靠 `--skip-loudness` / `--skip-blackdetect` 掩盖问题
- [ ] 黑帧/响度检查在交付前完整跑过一次
- [ ] `--json` 报告已存档（客户交付/复盘可追溯）
- [ ] 命名正则与项目命名规范一致
- [ ] 平台码率、时长等易变参数已按官方说明核对（本仓默认档标 `[待确认]`）

## 参考

- 脚本：[qc.py](scripts/qc.py)
- 项目初始化与 manifest：[video-project-init](../video-project-init/SKILL.md)
- 导出/转码/响度标准化：[ffmpeg-render](../ffmpeg-render/SKILL.md)
- 字幕与烧录：[subtitle-pipeline](../subtitle-pipeline/SKILL.md)
- 交付规格模板：[templates/交付规格.md](../../templates/交付规格.md)
- 本机 FFmpeg 能力基线：[knowledge/环境/environment-local.md](../../knowledge/环境/environment-local.md)
- 验收标准：[docs/质量门禁.md](../../docs/质量门禁.md)
