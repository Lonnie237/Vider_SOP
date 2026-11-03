---
name: subtitle-pipeline
description: "当已有转写文本或 SRT，需要断句、校时（CPS 校验）、生成 SRT/ASS，并把字幕烧录进视频、封装软字幕或输出外挂 SRT 时使用。先探测 FFmpeg 滤镜：本机 ffmpeg 9.0.2 未编译 libass/freetype 时，自动改用 Pillow 渲染透明 PNG + overlay 按时间区间合成；有 libass 时直接走 subtitles 滤镜。"
version: 0.1.0
---

# subtitle-pipeline · 字幕生成与烧录

> 本机硬约束：`ffmpeg 9.0.2` 未编译 libass/freetype，`subtitles` / `ass` / `drawtext` 滤镜全部不可用。技能先探测能力，再决定「libass 烧录」还是「Pillow PNG + overlay」；不允许直接假设滤镜可用。

## 何时使用

- 已有转写文本（纯文本）或 SRT，需要断句、分配时间轴、检查 CPS 后生成字幕文件。
- 要把 SRT 烧录进视频（平台自动字幕靠不住、或需要固定样式）。
- 要把字幕封装为软字幕（mov_text）或输出外挂 SRT 交给平台/客户。
- 需要校准整条时间轴（整体偏移、缩放）。
- 需要确认本机能不能烧字幕、走哪条路径（能力探测）。

## 不适用

- 语音识别转写：本机没有 whisper 等转写工具，本技能不负责「音频 → 文本」，只处理已有文本/SRT。
- 卡拉 OK 逐字动画、复杂描边动效、多语言双语排版：当前脚本只做整句分段与静态样式。
- 需要 libass 高级特效（`\an` 定位、旋转、逐字）：本机不可用；请在带 libass 的 FFmpeg 或 NLE 里做。
- 视频剪辑、调色、混音：用 ffmpeg-render 或 NLE。
- 自动翻译字幕：需要外部翻译工具，本技能只处理中文/已翻译文本。

## 输入（缺什么问什么）

| 输入 | 必填 | 说明 |
|---|---|---|
| 字幕源 | 是 | 纯文本（一行一句）或 SRT；纯文本每行可选 `[00:00:01.000-00:00:02.500] 台词` |
| 目标时长 | 纯文本自动分配时必填 | 成片总时长（秒）；不填则只能按条估算，无法对齐画面 |
| 视频文件 | 烧录/封装时必填 | 用于取分辨率、帧率、时长；本技能不改画面内容 |
| 模式 | 否 | `burn`（烧录，默认）/ `mux`（软字幕）/ `external`（外挂） |
| 样式 | 否 | 字体、字号、位置（bottom/center/top）、描边、半透明底框 |
| CPS 上限 | 否 | 默认 9 字/秒；超过给警告，不静默放过 |
| 输出路径 | 是 | 已存在时需 `--force` |

术语：CPS（characters per second，每秒字数），用于判断字幕是否来不及看；断句（segmentation）按标点与显示宽度切分。

## 步骤

1. 先探测能力，决定烧录路径（每条新机器必做）：

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness
python3 skills/subtitle-pipeline/scripts/subtitle.py probe
```

本机预期输出（2026-11-03 实测）：

```text
ffmpeg 9.0.2 / ffprobe 9.0.2 / Pillow 11.3.0
  filter subtitles  不可用
  filter ass        不可用
  filter drawtext   不可用
  filter overlay    可用
推荐烧录方式：pillow
```

2. 准备字幕源。纯文本一行一句，也可在行首写时间区间；整段不带时间则由 `--duration` 自动分配：

```text
[00:00:00.300-00:00:01.500] 大家好，今天讲代理剪辑
[00:00:01.700-00:00:03.200] 代理剪辑用低码率素材换流畅度
[00:00:03.400-00:00:04.000] 导出前切回原始素材
```

3. 断句 + 校时，生成 SRT（或 ASS）：

```bash
# 纯文本 → SRT：按 12 秒总时长、默认 4.5 字/秒估算
python3 skills/subtitle-pipeline/scripts/subtitle.py build \
  --input /tmp/skillw-sub/script.txt --duration 12 --out /tmp/skillw-sub/subs.srt

# SRT → ASS（供带 libass 的 FFmpeg / 播放器；本机只生成文件，不烧录）
python3 skills/subtitle-pipeline/scripts/subtitle.py build \
  --input /tmp/skillw-sub/subs.srt --out /tmp/skillw-sub/subs.ass \
  --ass-width 1280 --ass-height 720
```

如果出现 `CPS > 上限` 告警：加总时长、删字、或调 `--chars-per-sec` / `--max-width` 重新生成；不要带着告警直接烧录。

4. 校验字幕（重叠、CPS、行宽、单条时长）：

```bash
python3 skills/subtitle-pipeline/scripts/subtitle.py validate \
  --input /tmp/skillw-sub/subs.srt --cps-limit 9
```

退出码 0 表示没有结构性错误；warning 需人工判断。时间轴整体偏移/缩放用 `retime`：

```bash
python3 skills/subtitle-pipeline/scripts/subtitle.py retime \
  --input subs.srt --out subs-shift.srt --offset 0.4
```

5. 烧录 / 软封装 / 外挂三选一（先 `--dry-run` 看命令）：

```bash
# 烧录：自动探测——本机无 libass 时走 Pillow PNG + overlay fallback
python3 skills/subtitle-pipeline/scripts/burn.py \
  --input /tmp/skillw-sub/source.mp4 --srt /tmp/skillw-sub/subs.srt \
  --output /tmp/skillw-sub/burned.mp4 --dry-run

# 软字幕（mov_text，不依赖 libass，适合 B 站/剪辑软件二次编辑）
python3 skills/subtitle-pipeline/scripts/burn.py \
  --input source.mp4 --srt subs.srt --output muxed.mp4 --mode mux

# 外挂：视频流复制 + 同目录输出 .srt
python3 skills/subtitle-pipeline/scripts/burn.py \
  --input source.mp4 --srt subs.srt --output external.mp4 --mode external
```

去掉 `--dry-run` 才会执行。Pillow fallback 会为每条字幕生成 1 张全画幅透明 PNG，再用 `overlay=enable='between(t,开始,结束)'` 按时间叠加；加 `--keep-png <目录>` 可保留 PNG 检查排版。

6. libass 分支：若 `probe` 显示 `subtitles` 可用，`burn.py` 会自动改走 `-vf subtitles=...`；也可用 `--engine libass` 强制。本机强制会明确报错并提示改回 Pillow，不会静默失败。

7. 抽检输出：

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate \
  -show_entries format=duration -of compact burned.mp4
# 抽一帧确认字幕真的画上去了（配合 Pillow 数底部亮像素）
ffmpeg -hide_banner -y -ss 1.0 -i burned.mp4 -frames:v 1 frame.png
```

## 输出格式

- `subtitle.py build` 输出字幕文件 + 摘要：`生成 SRT：3 条，12.00s，最大 CPS 4.4 → subs.srt`；`--json` 输出 `{detected, format, cues, chars, span_s, max_cps, warnings, errors}`。
- `subtitle.py validate` 输出 `校验 xxx.srt：N 条 | error N | warning N | 最大 CPS x`，逐条列 ERROR/WARN。
- `burn.py` 输出：能力探测行、字幕条数与视频参数、实际 ffmpeg 命令、输出文件大小；`--json` 输出 `{mode, engine, cues, video, libass_available, output, size_mb}`。
- 产物：`.srt`（UTF-8）、`.ass`（UTF-8，含样式头）、`burned.mp4`、`muxed.mp4`（含 mov_text 字幕流）、`external.mp4 + external.srt`，以及可选 `--keep-png` 目录下的 `cue_0001.png`。
- 退出码：`0` 成功；`1` 校验发现结构性错误（重叠等）；`2` 参数/文件/环境错误（stderr 以「错误：」开头）。

## 失败处理

| 情况 | 现象 | 处理 |
|---|---|---|
| 依赖缺失（FFmpeg） | `找不到 ffmpeg/ffprobe` | 安装 FFmpeg（macOS：`brew install ffmpeg`）；烧录/封装必需，纯文本处理不需要 |
| 依赖缺失（Pillow） | `本机没有 Pillow，且 FFmpeg 没有 libass，无法烧录` | 装 Pillow（建议独立 venv）；或改用 `--mode mux` / `--mode external`，不烧录 |
| 滤镜不可用（libass） | `subtitles/ass` 探测不可用 | 属本机正常情况：自动走 Pillow fallback；不要手写 `subtitles=` 滤镜 |
| 滤镜不可用（overlay） | 极简构建可能连 overlay 都没有 | 用 `--mode mux` / `--mode external`；或换完整构建 FFmpeg |
| 路径不存在 | `输入视频不存在` / `字幕文件不存在` / `字体不存在` | 核对路径；字体用 `--font` 显式指定 |
| 参数越界 | `--max-width-ratio 越界` / `--bg-opacity 越界` / `--crf 越界` | 按报错区间调整：宽度比 0.1–1.0、不透明度 0–1、CRF 0–51、字号 8–400 |
| SRT 格式错误 | `SRT 时间行无法解析` / `end <= start` | 修 SRT；或用 `build` 从纯文本重新生成 |
| 时间重叠 / CPS 过高 | `validate` 输出 WARN/ERROR | 用 `retime` 平移/缩放，或 `build` 调 `--duration/--chars-per-sec/--max-width` 重排 |
| 输出已存在 | `输出文件已存在` | 换输出名或加 `--force` |
| 源不是 UTF-8 | `字幕不是 UTF-8` / `输入不是 UTF-8` | 先转码：`iconv -f GBK -t UTF-8 in.srt > out.srt` |
| 短字幕被平台遮挡 | 字幕落在底部安全区外 | 加大 `--margin-v`（竖屏建议 ≥ 画面高 10%），或改 `--position center` |

## 自检

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness

# 1) 能力探测（必须显示 overlay 可用；subtitles 不可用属预期）
python3 skills/subtitle-pipeline/scripts/subtitle.py probe

# 2) 文本 → SRT（12 秒；应无 CPS 告警）
python3 skills/subtitle-pipeline/scripts/subtitle.py build \
  --input /tmp/skillw-sub/script.txt --duration 12 --out /tmp/skillw-sub/subs.srt

# 3) 校验；SRT → ASS
python3 skills/subtitle-pipeline/scripts/subtitle.py validate --input /tmp/skillw-sub/demo.srt
python3 skills/subtitle-pipeline/scripts/subtitle.py build \
  --input /tmp/skillw-sub/demo.srt --out /tmp/skillw-sub/demo.ass \
  --ass-width 1280 --ass-height 720

# 4) 烧录 fallback + 抽帧验证（先清理旧输出）
rm -f /tmp/skillw-sub/burned.mp4
python3 skills/subtitle-pipeline/scripts/burn.py \
  --input /tmp/skillw-sub/black.mp4 --srt /tmp/skillw-sub/demo.srt \
  --output /tmp/skillw-sub/burned.mp4 --keep-png /tmp/skillw-sub/png
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate \
  -show_entries format=duration -of compact /tmp/skillw-sub/burned.mp4
ffmpeg -hide_banner -y -ss 1.0 -i /tmp/skillw-sub/burned.mp4 -frames:v 1 /tmp/skillw-sub/frame.png
python3 -c "from PIL import Image; im=Image.open('/tmp/skillw-sub/frame.png').convert('RGB'); w,h=im.size; px=im.load(); print('bottom_white_pixels=', sum(1 for y in range(int(h*0.7),h) for x in range(w) if sum(px[x,y])>600))"

# 5) 软字幕与外挂（先清理旧输出）
rm -f /tmp/skillw-sub/muxed.mp4
python3 skills/subtitle-pipeline/scripts/burn.py \
  --input /tmp/skillw-sub/source.mp4 --srt /tmp/skillw-sub/demo.srt \
  --output /tmp/skillw-sub/muxed.mp4 --mode mux
ffprobe -v error -show_entries stream=codec_type,codec_name -of compact /tmp/skillw-sub/muxed.mp4
```

[实测] 2026-11-03，本机 ffmpeg/ffprobe 9.0.2、Python 3.9.6、Pillow 11.3.0，测试素材为 `testsrc2` / 纯黑画面 1280×720/30fps/4s + sine 48kHz + 3 条中文 SRT：

| 用例 | 命令要点 | 结果 |
|---|---|---|
| 能力探测 | `subtitle.py probe` | subtitles/ass/drawtext 不可用，overlay 可用；推荐 pillow |
| 文本 → SRT（12s） | `build --duration 12` | 3 条、12.00s、最大 CPS 4.4、0 告警 |
| 文本 → SRT（4s，过短） | `build --duration 4` | 3 条、最大 CPS 13.3，输出 3 条 CPS 告警（校验生效） |
| SRT 校验 | `validate demo.srt` | 3 条、0 error、4 warning、最大 CPS 15.0，退出码 0 |
| SRT → ASS | `build ... --out demo.ass --ass-width 1280 --ass-height 720` | 3 条 Dialogue，样式头 PlayRes 1280×720 |
| 烧录（fallback） | `burn.py --input black.mp4 ... --keep-png png` | 自动选 Pillow；3 张透明 PNG；输出 1280×720/30fps/4.0s/0.1MB |
| 烧录结果抽帧 | `-ss 1.0 -frames:v 1` + Pillow 计数 | 底部 30% 区域 1964 个亮像素 → 字幕确实渲染 |
| 软字幕 | `--mode mux` | ffprobe 出现 `mov_text` 字幕流 |
| 外挂 | `--mode external` | 输出 external.mp4 + external.srt（203 字节） |
| 强制 libass | `--engine libass` | 退出码 2，明确提示「未编译 libass，改走 Pillow fallback」 |

自检清单：

- [ ] `probe` 显示 overlay 可用；subtitles 不可用时不硬写滤镜命令
- [ ] `build` 无 CPS/行宽告警，或已人工确认可接受
- [ ] `validate` error = 0
- [ ] 烧录后抽帧能看到字幕，且不挡脸、不出安全区
- [ ] `mux` 后 ffprobe 有 subtitle 流；`external` 后 .srt 与视频同目录
- [ ] 输出时长与源视频一致（Pillow fallback 用 `-t 源时长` 兜底）
- [ ] 若换用带 libass 的 FFmpeg，重跑 probe 确认自动切到 subtitles 滤镜并抽帧验证（本机缺 libass，该分支未实测）

## 参考

- 脚本：[subtitle.py](scripts/subtitle.py)（断句/校时/校验/ASS）、[burn.py](scripts/burn.py)（烧录/封装/外挂）
- 导出与转码前置：[ffmpeg-render](../ffmpeg-render/SKILL.md)
- 交付前质检：[qc-deliver](../qc-deliver/SKILL.md)
- 本机滤镜能力基线：[knowledge/环境/environment-local.md](../../knowledge/环境/environment-local.md)
- 交付规格模板：[templates/交付规格.md](../../templates/交付规格.md)
- 验收标准：[docs/质量门禁.md](../../docs/质量门禁.md)
