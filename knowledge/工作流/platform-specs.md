---
id: kb/platform-specs
title: 平台规格与发布 · 一稿多版与上传前自检
type: 工作流
domain: [交付, 发布, 平台适配]
status: 可用
confidence: 中
tags: [平台规格, 抖音, 视频号, 小红书, B站, YouTube, 发布, 自检]
related: [kb/transcode-delivery, kb/asset-management, kb/automation-pipeline, kb/subtitle-density, kb/environment-local]
updated: 2026-11-03
owner: method-writer
---

# 平台规格与发布 · 一稿多版与上传前自检

> 平台参数属于易变事实：官方明确公布的标 [事实] 并附访问日期；只能从第三方整理或经验得到的标 [推断] / [待确认]，发布前以平台投稿页提示为准。本文所有数据截至 **2026-11-03**。

## 一句话定位

把同一支片子按平台限制导出成多版，并在上传前用脚本核对分辨率、时长、体积、编码、音频与命名。用在 S10–S11 交付与发布；判断标准是每版都通过 `spec_check.py`、上传后真机可播且未被强制二次压缩。

## 适用场景

- 适用：一稿多发（抖音 / 视频号 / 小红书 / B站 / YouTube）、客户多规格交付、栏目批量化发布。
- 不适用：平台独家定制内容（按平台原生格式从头做）；直播推流（码率与协议另有一套，不适用本文）。

## 流程设计

输入 → 平台矩阵 → 变体导出 → 自检 → 发布：

| 阶段 | 输入 | 处理 | 输出 |
|---|---|---|---|
| 定版 | 母版 / 交付版 | 选主画幅与平台清单 | 平台矩阵表 |
| 变体 | 母版 | 按画幅裁切、按平台压码率 | 每平台 1 个 MP4 |
| 音频 | 变体 | 响度归一（-14 / -16 LUFS） | 达标音轨 |
| 自检 | 变体 | ffprobe + spec_check.py | 自检报告 |
| 发布 | 变体 + 封面 + 文案 | 上传、填标题/话题/封面 | 发布记录 |

## 平台公开规则（截至 2026-11-03）

| 平台 | 画幅 / 分辨率 | 时长 | 体积 | 码率 / 编码 | 字幕 | 审核注意 |
|---|---|---|---|---|---|---|
| 视频号 [事实] | 宽高比 0.33–3.0，建议 16:9 或 9:16 | 手机 3s–60min；助手 3s–8h | 手机 ≤2GB；助手 ≤20GB | 建议 ≥10Mbps；H.264 / H.265；不支持 HDR | 烧录或平台自动 | 版权、敏感词、广告标识 |
| 小红书 [事实·第三方] | 9:16，1080×1920 | ≤15min | ≤500MB | MP4 / MOV | 烧录或平台自动 | 版权、导流限制、广告标识 |
| 抖音 [待确认] | 推荐 9:16，1080×1920 | 以投稿页提示为准 | 以投稿页提示为准 | 推荐 H.264，8–12Mbps | 烧录或平台自动 | 版权音乐、敏感词、资质（医疗/金融等） |
| B站 [待确认] | 推荐 16:9，1920×1080 | 以投稿页提示为准 | 以投稿页提示为准 | 推荐 H.264 High；4K 权益另计 | 烧录或外挂 | 版权、分区、时政 |
| YouTube [待确认] | 推荐 16:9，1080p / 2160p | 以官方页为准 | 以官方页为准 | 推荐 MP4 / H.264 High / AAC-LC | 烧录或外挂 SRT | Content ID 版权、广告友好、地区限制 |
| 客户交付 | 按合同 | 按合同 | 按合同 | 母版 ProRes + H.264 审阅版 | 按合同 | 保密、水印、授权 |

> 视频号数据来自官方「素材要求」页（见来源 1）。小红书数据来自第三方整理（来源 2），非官方后台，发布前以创作服务平台为准。抖音 / B站 / YouTube 的完整参数需登录后台或官方页确认，本次抓取受限，标 [待确认]；不要照搬第三方「万能参数」。

## 本仓推荐导出参数（工程默认值，[推断]）

| 平台 | 画幅 | 分辨率 | 帧率 | 视频 | 音频 | 响度 |
|---|---|---|---|---|---|---|
| 抖音 / 视频号 / 小红书 | 9:16 | 1080×1920 | 30（或 60） | H.264 High，CRF 20–22，8–12Mbps | AAC 192k 48k 立体声 | -14 LUFS，TP ≤ -1.5 dBTP |
| B站 / YouTube | 16:9 | 1920×1080 | 30 / 60 | H.264 High，CRF 19–20，12–16Mbps | AAC 192–256k 48k | 长视频 -16 LUFS |
| 客户母版 | 按合同 | 1080p / 4K | 同工程 | ProRes 422 HQ | PCM 24bit 48k | -16 LUFS |
| 封面图 | 9:16 / 3:4 | 1080×1920 / 1080×1440 | — | JPG / PNG | — | — |

## 可操作步骤

1. 定主画幅：以 16:9 为主版（便于 B站 / YouTube），9:16 用安全裁切生成；不要拉伸。产出：平台矩阵。
2. 按矩阵导出：调用 [转码与交付](transcode-delivery.md) 的命令，逐平台导 1 个文件；文件名带平台与日期。产出：平台版 MP4。
3. 响度统一：短视频 -14 LUFS、长视频 -16 LUFS，TP ≤ -1.5 dBTP；命令见 [声音设计](../方法论/sound-design.md)。产出：达标音轨。
4. 字幕：优先烧录（样式可控）；平台自动字幕只做兜底；烧录走 Pillow overlay 或 NLE。产出：字幕版本。
5. 自检：跑 `spec_check.py`，全部 PASS 才上传。产出：自检报告。
6. 发布：封面比例、标题 / 短标题、话题、简介按平台填；上传后手机真机看一遍。产出：发布记录。

自检脚本（[实测] 2026-11-03：对 1080×1920 / 30fps / 3s / 2.35MB / AAC 48k 立体声的样片输出 6 项 PASS）：

```bash
python3 spec_check.py 03_output/demo_9x16_douyin_v1_20261103.mp4
```

```python
import json, subprocess, sys

path = sys.argv[1]
out = subprocess.run(["ffprobe", "-v", "error",
    "-show_entries", "stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
    "-show_entries", "format=duration,size", "-of", "json", path],
    capture_output=True, text=True, check=True).stdout
d = json.loads(out)
v = [s for s in d["streams"] if s.get("width")][0]
a = [s for s in d["streams"] if s.get("sample_rate")][0]
dur = float(d["format"]["duration"]); size_mb = int(d["format"]["size"]) / 1024 / 1024
num, den = map(int, v["r_frame_rate"].split("/")); fps = num / den
checks = {
    "codec h264": v["codec_name"] == "h264",
    "1080x1920": (v["width"], v["height"]) == (1080, 1920),
    "fps<=30": fps <= 30.01,
    "duration<=60s": dur <= 60,
    "size<=500MB": size_mb <= 500,
    "audio 48k stereo": a.get("sample_rate") == "48000" and a.get("channels") == 2,
}
for k, ok in checks.items():
    print("PASS" if ok else "FAIL", k)
print("result:", "PASS" if all(checks.values()) else "FAIL")
```

## 参数与阈值

| 参数 | 推荐值 | 依据 | 备注 |
|---|---|---|---|
| 视频号宽高比 | 0.33–3.0 | [事实] 来源 1 | 超范围无法发表 |
| 视频号码率 | ≥ 10Mbps | [事实] 来源 1 | 在体积限制内越高越清晰 |
| 视频号体积 | 手机 ≤2GB；助手 ≤20GB | [事实] 来源 1 | 超限换入口或压缩 |
| 小红书视频 | 9:16，≤15min，≤500MB | [事实·第三方] 来源 2 | 以创作服务平台为准 |
| 小红书图文 | 3:4，1080×1440，≤18 张 | [事实·第三方] 来源 2 | 单篇统一比例 |
| 竖屏分辨率 | 1080×1920 | 本仓规范 | 4K 竖屏 2160×3840 可选 |
| 横屏分辨率 | 1920×1080 | 本仓规范 | 4K 走 3840×2160 |
| 帧率 | 30 / 60（与素材一致优先） | [推断] | 混合帧率先统一 |
| 视频码率 | 8–16Mbps（1080p） | [推断] | 低于 6Mbps 易被二压 |
| 音频 | AAC 192–256k，48kHz，立体声 | [推断] | 统一 48k |
| 响度 | 短视频 -14；长视频 -16 LUFS | 本仓规范 | TP ≤ -1.5 dBTP |
| 字幕安全区 | 竖屏底部 ≥320px；横屏底部 ≥120px | [推断] | 平台 UI 差异大，真机确认 |
| 视频号文案 | 描述 ≤1000 字；短标题 ≤16 字 | [事实] 来源 1 | 短标题在搜索/话题展示 |
| 封面比例 | 竖屏 9:16；B站/YouTube 16:9 | [推断] | 封面单独导，别用视频截帧 |
| 上传前体积 | ≤ 平台上限 80% | [推断] | 留二次处理余量 |

## 失败处理

| 失败 | 症状 | 处理 |
|---|---|---|
| 上传被拒 | 平台提示格式 / 体积 / 时长不符 | 按矩阵重导；视频号超 2GB 换助手端 |
| 上传后变糊 | 平台二次压缩 | 提高码率 / 分辨率；避免低码率高运动 |
| 视频号 HDR 上传失败 | 提示不支持 | 转 SDR Rec.709 再传（见 [调色基础](../方法论/color-grading.md)） |
| 封面上传失败 | 比例 / 体积不符 | 按平台封面比例单独导出 |
| 审核不通过 | 版权 / 敏感词 / 资质 | 换授权素材、改文案、补资质；保留申诉记录 |
| 竖屏裁切切头 | 人脸 / 主体出画 | 重新构图（不是拉伸），检查安全区 |
| 字幕被 UI 遮挡 | 底部按钮压字 | 底部安全区 ≥320px；抽真机帧核对 |

## 常见反例

| 反例 | 为什么不行 | 怎么改 |
|---|---|---|
| 16:9 直接拉伸成 9:16 | 人脸变形，观众一眼看出 | 中心裁切或重新构图 |
| 一版参数发所有平台 | 平台体积 / 码率 / 时长限制不同 | 一稿多版，逐平台自检 |
| 码率压到 3–4Mbps 求小 | 平台再压一次，糊成块 | 1080p 至少 8Mbps |
| 传 HDR 到不支持平台 | 视频号不支持 HDR，直接失败 | 转 SDR 再传 |
| 照搬第三方「万能参数」 | 平台规则已变 / 账号权限不同 | 以官方投稿页 + 自检脚本为准 |
| 忽略版权音乐 | 下架 / 限流 / 侵权 | 用授权曲库，保留授权记录 |
| 字幕贴底边 | 被平台按钮遮挡 | 用安全区参数，真机预览 |

## 验证方式

- 自检脚本：`python3 spec_check.py <file>` 全部 PASS（[实测] 2026-11-03：样片 6 项 PASS）。
- 参数复核：`ffprobe -show_entries stream=width,height,r_frame_rate,codec_name,sample_rate,channels -show_entries format=duration,size` 与矩阵逐项对比。
- 平台入口：视频号助手 / 创作服务平台上传页会显示当前账号允许的时长与体积。
- 真机：上传后用手机播放，确认 1080p 可播、字幕不被 UI 遮挡、封面不变形。
- 审核：发布后看审核状态与版权提示；被限流时回看素材授权与文案。
- 失败信号：上传页提示「分辨率过低」；播放默认 480p 且手动切不到 1080p；封面被裁掉标题。

## 关联条目

- 工作流：[转码与交付](transcode-delivery.md)、[素材管理与代理剪辑](asset-management.md)、[自动化流水线](automation-pipeline.md)
- 方法论：[字幕与信息密度](../方法论/subtitle-density.md)、[声音设计](../方法论/sound-design.md)、[调色基础](../方法论/color-grading.md)、[钩子与留存](../方法论/hooks-retention.md)
- 环境：[本机环境](../环境/environment-local.md)
- 落地 SOP：`sop/short-oral-knowledge`、`sop/short-montage-beat`、`sop/long-tutorial`、`sop/long-promo`

## 来源

1. [视频号助手 · 视频号发表的素材有什么要求？](https://findeross.weixin.qq.com/cgi-bin/mmfindernodelivecrmwebbroker-bin/helper-center/pages/DCbKPGzZkvVHcIr6)（访问 2026-11-03）：格式、宽高比、时长、体积、码率、编码、文案字数限制。
2. [小红书笔记配图与商品主图规范（2026）](https://www.biaojixia.com/specs/xiaohongshu?scenario=spec-xiaohongshu)（访问 2026-11-03）：第三方整理，非官方后台；笔记视频 9:16 / ≤15min / ≤500MB。
3. [YouTube 推荐的上传编码设置](https://support.google.com/youtube/answer/1722171)（访问 2026-11-03）：官方推荐编码页；本次抓取受网络限制，具体码率数值以页面为准 [待确认]。
4. [B站创作中心](https://member.bilibili.com/)（访问 2026-11-03）：登录态，投稿规格以投稿页提示为准 [待确认]。
5. [抖音创作服务平台](https://creator.douyin.com/)（访问 2026-11-03）：登录态，投稿规格以投稿页提示为准 [待确认]。
6. 本机实测（2026-11-03，ffmpeg 9.0.2，Python 3.9.6）：`spec_check.py` 对 1080×1920 / 30fps / 3s / 2.35MB / AAC 48k 立体声样片输出 6 项 PASS。
7. 内部：[本机环境](../环境/environment-local.md)（2026-11-03）。
