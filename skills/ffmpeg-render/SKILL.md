---
name: ffmpeg-render
description: "当需要把素材导出为平台成片、转码换封装或编码、批量处理一批视频、把横屏素材适配为竖屏（模糊背景/裁剪/加边），或把音频响度统一到指定 LUFS 时使用。读取项目 manifest.json 或 05-交付/交付规格.md 中的分辨率、帧率、码率、响度，生成并执行 FFmpeg 命令；支持 --dry-run 先看命令。本机 ffmpeg 9.0.2 无 libass，不负责字幕烧录（见 subtitle-pipeline）。"
version: 0.1.0
---

# ffmpeg-render · 标准导出与批量转码

> 把「导出」从手敲命令变成可复核、可批量、可复现的动作：参数来自项目交付规格，而不是每次凭感觉填。

## 何时使用

- 项目已有 `manifest.json` 或 `05-交付/交付规格.md`，要按其中的分辨率、帧率、码率、响度导出。
- 同一套参数要批量处理一批文件。
- 横屏素材要发竖屏平台，需要模糊背景（blur）、裁剪（crop）或加边（pad）。
- 画面不动，只把音频响度统一到目标 LUFS（loudness）。
- 想先看 FFmpeg 命令再决定是否执行（先 `--dry-run` 再执行是推荐流程）。

## 不适用

- 烧录字幕、生成字幕：用 subtitle-pipeline 技能；本机 ffmpeg 9.0.2 未编译 libass/freetype，`subtitles` / `ass` / `drawtext` 滤镜不可用。
- 多轨剪辑、转场、调色、混音：在 NLE（非线性编辑软件）里完成，再交给本技能导出。
- 平台上传、发布、封面制作：本技能只产出本地文件。
- 需要逐帧人工审片：本技能只做转码与规格转换，质量判断交给 qc-deliver 技能。

## 输入（缺什么问什么）

| 输入 | 必填 | 说明 |
|---|---|---|
| 输入文件 | 是 | 单个视频文件；`batch` 模式传目录 |
| 输出路径 | 是（`batch` 除外） | 目标文件；已存在时需 `--force` |
| 交付规格 | 否 | `--project <项目目录>` 或 `--spec <manifest.json 或 交付规格.md>`；不传则保留源分辨率/帧率，视频 6000 kbps、响度 -14 LUFS |
| 模式 | 否 | `export`（默认）/ `transcode` / `batch` / `vertical` / `loudnorm` |
| 覆盖参数 | 否 | `--width` `--height` `--fps` `--video-bitrate` `--crf` `--loudness` `--fit` 等 |
| 目标平台 | 否 | 只用于核对；实际参数以交付规格文件为准 |

规格解析优先级：命令行覆盖 > `--spec` > `--project` > 内置默认值。`--project` 先找 `manifest.json`，再找 `05-交付/交付规格.md`。

## 步骤

1. 确认源文件与目标项目（没有项目先跑 video-project-init）：

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate \
  -show_entries format=duration -of json /path/to/source.mp4
```

2. 先干跑，只看命令不执行：

```bash
python3 skills/ffmpeg-render/scripts/render.py \
  --project /path/to/项目目录 \
  --input /path/to/source.mp4 \
  --output /path/to/out.mp4 \
  --dry-run
```

3. 核对命令中的四处关键参数：`scale=宽:高`（分辨率）、`fps=`（帧率）、`-b:v`（码率）、`loudnorm=I=`（响度）。与 `05-交付/交付规格.md` 不一致时，用命令行覆盖或改规格后重跑。

4. 确认无误后去掉 `--dry-run` 执行：

```bash
python3 skills/ffmpeg-render/scripts/render.py \
  --project /path/to/项目目录 \
  --input /path/to/source.mp4 \
  --output /path/to/out.mp4
```

5. 抽检输出（分辨率/帧率/编码/音频/时长）：

```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels \
  -show_entries format=duration,size,bit_rate -of json /path/to/out.mp4
```

6. 其他模式按场景选：

| 场景 | 命令要点 |
|---|---|
| 转码（换编码/封装，保持源分辨率） | `--mode transcode`；只有显式给 `--width/--height/--fps` 才缩放 |
| 批量导出 | `--input 素材目录 --mode batch --output-dir 输出目录`，输出名 `<原名>-render.mp4` |
| 竖屏适配 | `--mode vertical --fit blur`（背景模糊）/ `crop`（裁切）/ `pad`（加黑边）；未给尺寸时默认 1080×1920 |
| 响度标准化 | `--mode loudnorm`；视频流直接复制（`-c:v copy`），只重编码音频 |
| 只要 CRF 质量档 | 加 `--crf 20`，命令改用 CRF，不再用固定码率 |

竖屏与批量示例（可直接复制）：

```bash
# 竖屏：背景模糊，主体完整保留（适合横屏素材转抖音/视频号）
python3 skills/ffmpeg-render/scripts/render.py \
  --input /path/to/source.mp4 --mode vertical --fit blur \
  --width 1080 --height 1920 --output /path/to/vertical.mp4

# 批量：按项目交付规格处理目录下所有常见视频
python3 skills/ffmpeg-render/scripts/render.py \
  --project /path/to/项目目录 --input /path/to/素材目录 \
  --mode batch --output-dir /path/to/导出目录
```

## 输出格式

- 终端先打印实际命令，再打印输出摘要：

```text
[执行] /opt/homebrew/bin/ffmpeg -hide_banner -y -i source.mp4 -vf 'scale=1080:1920,...' ...
  → /tmp/skillw-test/export.mp4 | 1080x1920 | 30 fps | 4.0s | 2.1 MB
```

- 加 `--json` 时，在摘要后追加机器可读结果：`{"spec_source": ..., "results": [{"input": ..., "output": ...}]}`。
- 输出文件默认 H.264 + AAC 48 kHz 立体声、`+faststart`（边下边播）。
- 退出码：`0` 成功；`2` 输入/参数/执行错误（错误信息写到 stderr，以「错误：」开头）。

## 失败处理

| 情况 | 现象 | 处理 |
|---|---|---|
| 依赖缺失 | `找不到 ffmpeg` / `找不到 ffprobe` | 安装 FFmpeg（macOS：`brew install ffmpeg`），`ffmpeg -version` 确认；本机基线 9.0.2 见 [本机环境](../../knowledge/环境/environment-local.md) |
| 滤镜不可用 | 命令报 `No such filter: 'loudnorm'/'boxblur'/'overlay'` | 先 `ffmpeg -filters \| grep -E 'loudnorm\|boxblur\|overlay'`；缺 loudnorm 加 `--no-audio-normalize`；缺 boxblur/overlay 改 `--fit pad` |
| 路径不存在 | `输入文件不存在` / `--project 下没找到 manifest.json...` | 核对路径；项目没初始化先跑 [video-project-init](../video-project-init/SKILL.md) |
| 参数越界 | `--width 越界：10（允许 64–7680）` 等 | 按提示区间调整；码率 100–200000 kbps、CRF 0–51、响度 -70–0 LUFS |
| 输出已存在 | `输出文件已存在` | 换文件名或加 `--force`（batch 默认跳过已存在文件） |
| 输入无音轨 | 不报错；自动加 `-an` | 需要声音先补音轨；`loudnorm` 模式会明确报「输入没有音轨」 |
| 编码失败 | ffmpeg 退出码非 0，打印 stderr 末 8 行 | 换 `--preset veryfast` 或 `--codec libx265`；确认磁盘空间与源文件可解码 |
| 超时 | `命令超时（3600s）` | 长片调大 `--timeout`，或先切 30s 样片验证参数 |

## 自检

```bash
cd /Users/Lonnie/Documents/deepseek-harness/vider_harness

# 1) 入口能解释参数
python3 skills/ffmpeg-render/scripts/render.py --help >/dev/null && echo HELP_OK

# 2) 干跑：只打印命令，不产生文件
python3 skills/ffmpeg-render/scripts/render.py \
  --project /tmp/skillw-doc/demo --input /tmp/skillw-test/source.mp4 \
  --output /tmp/skillw-doc/out.mp4 --dry-run

# 3) 实跑一条，再用 ffprobe 核对（先清理上次自检输出）
rm -f /tmp/skillw-doc/out.mp4
python3 skills/ffmpeg-render/scripts/render.py \
  --project /tmp/skillw-doc/demo --input /tmp/skillw-test/source.mp4 \
  --output /tmp/skillw-doc/out.mp4
```

[实测] 2026-11-03，本机 ffmpeg/ffprobe 9.0.2（Homebrew，macOS M5），测试源用 `testsrc2` 生成 1280×720 / 30fps / 4s，音轨 sine 48 kHz：

| 用例 | 命令要点 | 结果 |
|---|---|---|
| 帮助 | `--help` | 退出码 0 |
| 单条导出 | `--project /tmp/skillw-doc/demo` | 1080×1920、30 fps、4.0s、2.1 MB，耗时 0.69s |
| 竖屏模糊 | `--mode vertical --fit blur` | 1080×1920、4.0s、2.3 MB |
| 竖屏裁剪 | `--mode vertical --fit crop` | 1080×1920、4.0s、2.6 MB |
| 响度标准化 | `--mode loudnorm` | 1280×720、4.0s，视频流复制 |
| 批量 | `--mode batch`（2 个文件） | 2 个 `*-render.mp4`，均 1080×1920 |
| 转码 | `--mode transcode` | 保持源 1280×720 |
| 无音轨输入 | 640×360 无音轨源 | 自动 `-an`，输出正常 |
| 错误路径 | 输入不存在 / 输出已存在 / `--width 10` | 退出码 2，错误信息明确 |

自检清单：

- [ ] `--dry-run` 输出的 `scale` / `fps` / `-b:v` / `loudnorm` 与交付规格一致
- [ ] 实跑后 `ffprobe` 的分辨率、帧率、时长、音频参数符合预期
- [ ] 批量模式输出数量 = 输入数量（已存在文件会明确提示跳过）
- [ ] 失败时先看 stderr 末 8 行，不用猜

## 参考

- 脚本：[scripts/render.py](scripts/render.py)
- 项目初始化：[video-project-init](../video-project-init/SKILL.md)
- 交付规格模板：[templates/交付规格.md](../../templates/交付规格.md)
- 本机 FFmpeg 能力与性能基线：[knowledge/环境/environment-local.md](../../knowledge/环境/environment-local.md)
- 技能索引：[skills/README.md](../../skills/README.md)
- 验收标准：[docs/质量门禁.md](../../docs/质量门禁.md)
