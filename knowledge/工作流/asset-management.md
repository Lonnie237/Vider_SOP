---
id: kb/asset-management
title: 素材管理与代理剪辑 · 可找、可回滚、可批量
type: 工作流
domain: [素材管理, 剪辑, 备份]
status: 可用
confidence: 高
tags: [素材管理, 代理剪辑, 命名规范, 备份, 场记, 元数据]
related: [kb/transcode-delivery, kb/automation-pipeline, kb/platform-specs, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 素材管理与代理剪辑 · 可找、可回滚、可批量

> 目标：任何素材 30 秒内能找到、能回到原始文件、能批量处理。本机 24GB 内存 + Apple M5，4K 原素材直接剪会掉帧，代理剪辑是默认策略。

## 一句话定位

把拍摄 / 下载 / 录屏来的原始文件整理成「只读原素材 + 可重建代理 + 可追溯元数据」的结构，让剪辑、自动化、交付都基于同一套路径与命名。用在 S2–S3 素材入库与 S4 粗剪前；判断标准是文件名能自解释、代理数量与原素材一一对应、备份可校验。

## 适用场景

- 适用：多机位口播、Vlog、访谈、直播切片素材、混合手机 / 相机素材、批量混剪。
- 不适用：单文件、5 分钟内的临时剪辑（直接剪原文件更快）；纯云端协作项目（改用共享盘 + 云端代理）。

## 流程设计

输入 → 结构 → 命名 → 代理 → 校验 → 备份 → 输出：

| 阶段 | 输入 | 处理 | 输出 |
|---|---|---|---|
| 入库 | 相机卡 / 下载文件 | 拷贝到 `01_footage/`，原文件只读 | 原始素材 |
| 命名 | 原始文件名 | 按规范重命名（仅副本或导入时） | 可检索文件名 |
| 代理 | 原素材 | FFmpeg 转 540p H.264 或 ProRes Proxy | `02_proxy/` |
| 元数据 | 素材 + 场记 | ffprobe 清单 + 场记表 | `00_admin/inventory.csv`、场记表 |
| 校验 | 原素材 + 代理 | 数量、时长、checksum 比对 | 校验报告 |
| 备份 | 原素材 + 工程 | 3-2-1 策略 | 本地 + 离线 + 异地 |
| 输出 | 以上 | 交给粗剪 / 自动化 | 项目目录 |

目录结构（项目根目录，建议整个项目一个文件夹）：

```text
project/
├── 00_admin/       # 合同、脚本、场记表、授权、inventory.csv
├── 01_footage/     # 原始素材（只读；按机位/日期分）
│   ├── A_cam/
│   ├── B_cam/
│   └── audio/
├── 02_proxy/       # 代理文件，与原素材同名 + _proxy
├── 03_audio/       # 配音、BGM、音效
├── 04_graphics/    # 字幕、花字、LUT、logo、封面
├── 05_edit/        # NLE 工程 / 脚本 / 时间线
├── 06_exports/     # master/ 母版；platform/ 平台版
└── 07_qc/          # QC 截图、ffprobe 报告、发布记录
```

命名规范（文件用 ASCII，目录可用中文）：

| 对象 | 规则 | 示例 |
|---|---|---|
| 原素材 | `YYYYMMDD_项目_机位_序号.ext` | `20261103_demo_A001_0001.MP4` |
| 代理 | 原素材名 + `_proxy` | `20261103_demo_A001_0001_proxy.mp4` |
| 工程 | `项目_版本` | `demo_v3.prproj` |
| 交付 | `项目_画幅_平台_版本_日期` | `demo_9x16_douyin_v1_20261103.mp4` |
| 母版 | `项目_master_日期` | `demo_master_20261103.mov` |
| 禁止 | 空格、中文、`final`、`new`、连续 `v2_final` | — |

## 可操作步骤

1. 建目录：按上面结构一次性建好；把 `01_footage` 设为只读（Finder「简介 → 已锁定」或 `chmod -R a-w`，处理完再解锁）。
2. 入库重命名：优先在拷贝时用 `rsync` / 相机导入工具重命名；不要先剪再改名，否则工程会丢链接。产出：规范文件名。
3. 生成代理：按素材情况选 H.264 540p（通用）或 ProRes Proxy（NLE 需要 10-bit）；命令见下。产出：`02_proxy` 下的代理。
4. 元数据清单：`ffprobe` 批量导出 CSV，记录时长、分辨率、帧率、码率、大小；与场记表对齐。产出：`inventory.csv`。
5. 场记表：按「文件名 / 时间码 / 景别 / 内容 / 情绪 / 可用性 / 备注」填，导入 NLE 标记。产出：`shotlist.csv`。
6. 校验：文件数、总时长、checksum 三项对齐；代理缺失的单独列出重转。产出：`07_qc/asset-check.txt`。
7. 备份：3-2-1（3 份副本、2 种介质、1 份异地），原素材与工程都备；备份后跑 `shasum -a 256 -c`。产出：可恢复备份。

代理转码命令（[实测] 2026-11-03：1080p 10s 素材转 540p 用时 0.36s；2s ProRes Proxy 5.0MB vs ProRes HQ 19MB）：

```bash
# H.264 540p 代理（推荐：4K 素材 + 本机 24GB 内存）
ffmpeg -y -hide_banner -i 01_footage/A_cam/20261103_demo_A001_0001.MP4 -vf "scale=960:540:flags=bicubic,fps=30" -c:v libx264 -preset veryfast -crf 26 -g 30 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 48000 02_proxy/20261103_demo_A001_0001_proxy.mp4

# ProRes Proxy（NLE 需要 ProRes / 10-bit 时间线时）
ffmpeg -y -hide_banner -i 01_footage/A_cam/20261103_demo_A001_0001.MP4 -c:v prores_ks -profile:v 0 -pix_fmt yuv422p10le -c:a pcm_s16le 02_proxy/20261103_demo_A001_0001_proxy.mov
```

元数据清单（[实测] 2026-11-03：ffprobe 9.0.2 可批量输出；CSV 直接进表格）：

```bash
ffprobe -v error -show_entries format=filename,duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 01_footage/A_cam/*.MP4 > 00_admin/inventory.csv
```

校验与备份（[实测] 2026-11-03：shasum 可用；checksum 失败会返回非 0）：

```bash
shasum -a 256 01_footage/**/*.MP4 > 00_admin/footage.sha256
shasum -a 256 -c 00_admin/footage.sha256
rsync -a --info=progress2 01_footage/ /Volumes/BACKUP/project/01_footage/
```

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| 代理分辨率 | 540p（4K 素材）/ 720p（1080p 素材） | [推断] 解码压力与画质折中 | 竖屏按短边 540 |
| H.264 代理 | `-preset veryfast -crf 26 -g 30` | 快速、可拖拽 | crf 24–28 均可 |
| ProRes Proxy | `-profile:v 0 -pix_fmt yuv422p10le` | ProRes 规范 | 体积约为 HQ 的 1/4（实测） |
| 代理音频 | AAC 128k / PCM 16bit | [推断] | 对白可听即可 |
| 代理帧率 | 与原素材一致 | 防音画不同步 | 可变帧率先 `fps` 固定 |
| 禁止原素材改名 | 入库后不再改名 | 防工程丢链接 | 改名前先备份工程 |
| 项目目录深度 | ≤ 3 层 | 命令行友好 | 避免过深路径 |
| 磁盘预警 | 可用空间 < 10% 停止导入 | [推断] | `df -h` 检查 |
| 备份策略 | 3-2-1 | 行业通行 | 原素材 + 工程 + 导出 |
| 校验 | 数量 100% 对齐；时长差 ≤ 1 帧 | [推断] | 用 ffprobe 时长 |
| checksum | SHA-256 | 防静默损坏 | 备份后必跑 |

## 失败处理

| 失败 | 症状 | 处理 |
|---|---|---|
| 代理缺失 | 02_proxy 数量少于 01_footage | 按 inventory.csv 差集重转；不要手工补 |
| 帧率不一致 | 代理与源时长差 > 1 帧 | 代理统一 `fps=30`，可变帧率素材先转恒定帧率 |
| 磁盘不足 | 导入中断、rsync 报错 | 先清理 / 换盘；保留 `inventory.csv` 与已校验部分 |
| checksum 失败 | `shasum -c` 报 FAILED | 从备份重拷该文件，重新校验；不要继续剪辑 |
| 中文 / 空格路径 | 命令报错、脚本解析失败 | 源文件用 ASCII；命令中路径加引号 |
| NLE 不识别 ProRes | Windows 机器缺解码器 | 改用 H.264 代理，或统一装 ProRes 解码器 |
| 误改原素材 | 工程离线、颜色变化 | 原素材只读；从备份恢复后再统一改名 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 素材堆在桌面 / 下载文件夹 | 找不到、重名、无法备份 | 一项目一目录，按固定结构入库 |
| 4K 原素材直接剪 | 本机掉帧、时间线卡顿 | 先转 540p / ProRes Proxy 代理 |
| 代理覆盖原素材 | 画质不可逆丢失 | 代理单独目录，文件名加 `_proxy` |
| 只备份工程不备份素材 | 工程能开、素材离线 | 3-2-1 同时覆盖原素材与工程 |
| 文件名 `final_v2_真final` | 版本不可追溯 | `项目_平台_v1_日期`，版本递增 |
| 先用素材再补场记 | 找不到可用镜头，重看全片 | 入库即填场记与元数据 |

## 验证方式

- 数量：`ls 01_footage/**/*.MP4 | wc -l` 与 `ls 02_proxy/*_proxy* | wc -l` 一致。
- 时长：逐条 `ffprobe -v error -show_entries format=duration -of csv=p=0 file`，源与代理差 ≤ 1 帧。
- 完整性：`shasum -a 256 -c 00_admin/footage.sha256` 全部 OK。
- 元数据：`inventory.csv` 行数 = 素材数，分辨率 / 帧率无空值。
- 可拖拽：在 NLE 里连续拖 3 个代理上时间线，无卡顿。
- 失败信号：时间线出现「媒体离线」；代理播放花屏；备份盘文件数少于源。

## 关联条目

- 工作流：[转码与交付](transcode-delivery.md)、[自动化流水线](automation-pipeline.md)、[平台规格与发布](platform-specs.md)
- 方法论：[调色基础](../方法论/color-grading.md)（素材色彩一致性）
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-vlog`、`sop/long-interview-podcast`、`sop/short-oral-knowledge`

## 来源

1. [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)（访问 2026-11-03）：scale / fps / libx264 / prores_ks 参数。
2. 本机实测（2026-11-03，ffmpeg 9.0.2，macOS Apple Silicon）：1080p 10s → 540p 代理 0.36s；2s 1080p ProRes Proxy 5.0MB、ProRes 422 HQ 19MB；shasum / rsync 可用。
3. 本仓模板：[交付规格](../../templates/交付规格.md)、[QC 清单](../../templates/QC清单.md)（2026-11-03）。
4. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）：磁盘、内存与编解码器边界。
