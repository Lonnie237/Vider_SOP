---
id: kb/color-grading
title: 调色基础 · 一级校正、镜头匹配与 Rec.709 交付
type: 方法论
domain: [调色, 交付, 剪辑]
status: 可用
confidence: 中
tags: [调色, 一级校正, LUT, Rec.709, 示波器, 色彩管理]
related: [kb/transcode-delivery, kb/platform-specs, kb/subtitle-density, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 调色基础 · 一级校正、镜头匹配与 Rec.709 交付

> 顺序不能反：先做一级校正（primary correction）把画面调「对」，再做镜头匹配与二级，最后才套风格 LUT。交付默认 Rec.709 / SDR / yuv420p，并在文件里写对色彩标签。

## 一句话定位

让同一场戏的镜头不跳色、肤色自然、黑白位不丢细节，再用 LUT / 二级表达风格。用在 S8 调色与 S10 导出；判断标准是示波器范围合法、镜头间色温与亮度一致、文件色彩标签正确。

## 适用场景

- 适用：实拍口播、Vlog、访谈、宣传片、混合素材（手机 + 相机）的统一。
- 不适用：纯屏幕录制 / 动画（只需统一白点与亮度，不必套胶片 LUT）；HDR 交付（需另做 PQ / HLG 流程，不能套 SDR LUT）。

## 原理与判断标准

- 一级校正解决四件事：曝光（亮度）、白平衡（色温 / 色调）、对比（黑位 / 白位）、饱和度。目标是还原现场并让镜头间一致，而不是「好看」。
- 二级（secondary）只改局部：肤色、天空、品牌色、特定物体；风格 LUT 放在最后，作为整体色彩映射。
- 判断靠示波器，不靠眼睛记忆：
  - 波形图（waveform）：黑位不低于 0 IRE，白位不超过 100 IRE；广播安全按 Y 16–235（limited range）。
  - 矢量图（vectorscope）：肤色落在 10:00–11:00 方向附近，不过度偏红 / 偏黄。
  - 直方图：高光 / 阴影不并阶（大量像素堆在两端）。
- 什么算好：同场景切镜不跳色；肤色自然；暗部有细节；高光有层次；全片白点一致。
- 什么算坏：先套 LUT 再校正；全片一个 LUT 不看镜头；饱和拉满；只看手机屏；8-bit 素材大幅调色出现断层。

## 可操作步骤

1. 监看校准：显示器亮度 100–120 nit、白点 6500K、Rec.709 模式；关闭手机「原彩显示 / 护眼模式」再比对。产出：可信监看。
2. 一级校正：先曝光（看波形 / 直方图），再白平衡（灰卡或画面白点），最后对比与饱和。产出：中性画面。
3. 镜头匹配：同场景逐镜对齐亮度（YAVG）与肤色；色温差控制在 ≤ 300K。产出：不跳色的序列。
4. 二级：只对肤色 / 天空 / 品牌色做局部调整；遮罩跟随主体，避免边缘闪烁。产出：重点正确的画面。
5. 风格 LUT：最后套 `lut3d`，用 tetrahedral 插值；强度按需降低（见参数表）。产出：统一风格。
6. 输出与校验：写 Rec.709 标签，导出后抽帧与示波器复核。产出：`graded.mp4`。

一级校正命令示例（[实测] 2026-11-03：1080p 片段编码成功）：

```bash
ffmpeg -y -hide_banner -i input.mp4 -vf "eq=contrast=1.05:saturation=1.08:gamma=0.98,curves=all='0/0 0.5/0.52 1/1',colorbalance=rs=-0.02:bs=0.02,format=yuv420p" -c:v libx264 -preset medium -crf 18 -an graded.mp4
```

示波器数据（[实测] 2026-11-03）：`signalstats` 输出每帧的 YMIN / YAVG / YMAX / SATAVG / HUEAVG，可用来判断范围与偏色：

```bash
ffmpeg -hide_banner -i graded.mp4 -vf "signalstats,metadata=print" -frames:v 1 -f null - 2>&1 | grep -E "lavfi.signalstats.(YMIN|YAVG|YMAX|SATAVG|HUEAVG)" | head
```

LUT 应用（[实测] 2026-11-03：17³ 暖色 .cube 经 `lut3d` 编码成功）：

```bash
ffmpeg -y -hide_banner -i graded.mp4 -vf "lut3d=file=warm.cube:interp=tetrahedral,format=yuv420p" -c:v libx264 -preset medium -crf 18 -an lutted.mp4
```

Rec.709 交付与标签校验（[实测] 2026-11-03：只有加 `-x264-params` 后 ffprobe 才同时读到 primaries / transfer / space）：

```bash
ffmpeg -y -hide_banner -i lutted.mp4 -vf "format=yuv420p" -c:v libx264 -preset medium -crf 18 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" -an deliver.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=color_space,color_primaries,color_transfer,color_range -of json deliver.mp4
```

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| 交付色彩空间 | Rec.709 / SDR | 平台与播放器兼容性 | 非 HDR 项目默认 |
| 白点 | D65（6500K） | 广播监看惯例 | 全片统一 |
| 监看亮度 | 100–120 nit | [推断] | 太亮会误判曝光 |
| 黑位 / 白位 | Y 16 / Y 235（limited） | Rec.709 量化范围 | 留 2–5 IRE 余量 |
| 波形范围 | 0–100 IRE | 示波器定义 | 高光不贴顶 |
| 肤色矢量 | 10:00–11:00 方向 | 矢量图示波器惯例 | 偏红 / 偏黄一眼可见 |
| 饱和度调整 | ±10% 以内 | [推断] | 超过易失真 |
| 对比调整 | ±5%（曲线幅度 ≤ ±0.1） | [推断] | 8-bit 素材更保守 |
| 同场景色温差 | ≤ 300K | [推断] | 切镜不跳色 |
| LUT 强度 | 30%–50% | [推断] | 100% 常过饱和 |
| 插值方式 | `interp=tetrahedral` | LUT 常用插值 | 比 trilinear 更平滑 |
| 输出像素格式 | yuv420p（8-bit） | 平台兼容 | 10-bit 可留母版 |
| 输出标签 | bt709 / tv / yuv420p | 防播放器误判 | 用 x264-params 强制 VUI |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 先套 LUT 再做一级校正 | LUT 把错误曝光 / 白平衡一起放大 | 顺序固定：校正 → 匹配 → LUT |
| 全片一个 LUT 不看镜头 | 逆光镜头与室内镜头被压成同一色调 | 按场景分组，LUT 后用一级微调 |
| 饱和度拉满 | 肤色发橙、暗部溢出 | 饱和 ±10% 内，靠对比与色彩分离做「浓」 |
| 只看手机屏判断 | 手机自动增强对比与饱和度 | 用校准显示器 + 示波器，手机只做最终预览 |
| 8-bit 素材大幅调整 | 天空 / 暗部出现色带断层 | 减幅度、加噪点 / 抖动，或换 10-bit 素材 |
| 混用 tv / pc range | 画面发灰或死黑 | 输出统一 tv（limited），转换时明确范围 |
| HDR 素材直接当 SDR 调 | 高光裁切、颜色发灰 | 先做 HDR→SDR 色调映射，再进一级校正 |
| 输出不写色彩标签 | 播放器按猜测解释，颜色偏 | 加 `-color_primaries` 等标签并用 ffprobe 复核 |

## 验证方式

- 范围：`signalstats` 的 YMIN ≥ 16、YMAX ≤ 235（limited 素材），SATAVG 不异常（[实测] 2026-11-03：0xAAAAAA 灰块在 yuv420p 下 Y=162、SATAVG=0、HUEAVG=180，说明灰块中性）。
- 偏色：用矢量图看肤色方向；或用 `signalstats` 的 HUEAVG 对比同场景镜头，偏差大就重做白平衡。
- 一致性：同场景抽 3 帧（入 / 中 / 出）并排对比，切镜是否跳色。
- 标签：`ffprobe -show_entries stream=color_space,color_primaries,color_transfer,color_range` 四项齐全（[实测]：只用 `-colorspace/-color_primaries/-color_trc` 时 primaries/transfer 可能不写入，加 `-x264-params` 后齐全）。
- 多设备：校准显示器 + 手机 + 另一台电脑各看一遍。
- 失败信号：观众说「颜色怪 / 人脸发绿」；平台转码后更灰（标签或 range 错）；高光成片无细节。

## 关联条目

- 方法论：[字幕与信息密度](subtitle-density.md)
- 工作流：`kb/transcode-delivery`、`kb/platform-specs`（下一轮产出）
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-vlog`、`sop/long-promo`、`sop/long-tutorial`

## 来源

1. [FFmpeg lut3d 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#lut3d)（访问 2026-11-03）：.cube 支持与插值参数。
2. [FFmpeg signalstats 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#signalstats)（访问 2026-11-03）：YMIN / YAVG / YMAX / SATAVG / HUEAVG 定义。
3. [ITU-R BT.709 建议书](https://www.itu.int/rec/R-REC-BT.709)（访问 2026-11-03）：HDTV 色彩空间与量化范围。
4. 本机实测（2026-11-03，ffmpeg 9.0.2）：`eq` + `curves` + `colorbalance` 链编码成功；17³ .cube 经 `lut3d=interp=tetrahedral` 编码成功；0xAAAAAA 灰块 `signalstats` 输出 YMIN=YAVG=YMAX=162、SATAVG=0、HUEAVG=180；加 `-x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709"` 后 ffprobe 可读到四项色彩标签。
5. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）。
