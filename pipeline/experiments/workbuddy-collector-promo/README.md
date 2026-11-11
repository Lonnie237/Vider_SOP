# WorkBuddy 网站采集工程师 · 45s 推广片

- 日期：2026-11-11
- 成片（本地）：pipeline/runs/demo-workbuddy-collector/collector-promo.mp4
- 源录屏：Desktop/录屏2026-11-11 11.18.30.mov（2936×1838 / 60fps / 8:14）
- 真实录屏 + Qwen TTS + 字幕 + 二维码 CTA
- 时长：40.68s / 1220 帧 / 1920×1080 / 30fps / -16.0 LUFS

## 剪辑结构

| 时间 | 画面 | 旁白 |
|---|---|---|
| 0–5s | 中国货币网人民币汇率中间价页面 | 每天早上九点十五，中间价更新；你还在手动复制吗 |
| 5–13s | 真实录屏：输入网址/5 个货币对/字段/9:30 | 五个货币对，复制粘贴对格式，漏一天就断 |
| 13–18s | 真实录屏：自动定位接口（4×） | 自动定位数据接口，按日期去重，失败通报 |
| 18–25s | 真实录屏：CSV 结果表 | 每天 9:30 自动出表 |
| 25–31s | 真实录屏：逐条对照/交付说明 | 交付前和官网逐条对照，结果可验证 |
| 31–35s | 真实录屏：定时任务设置 | 每天 9:30、去重、失败通报 |
| 35–40s | 专家页 + 二维码 | WorkBuddy 搜「网站采集工程师」，扫码打开 |

## 工程

- 入口：src/index.ts → src/RealRoot.tsx
- 合成：src/RealPromo.tsx
- 源录屏裁切：ffmpeg 生成 public/clips/task|process|result|verify|schedule.mp4
- 音频/字幕：tools/make_audio.py
- 渲染：npx remotion render src/index.ts CollectorPromoReal out/real-promo.mp4
- 原始录屏、裁切片段、二维码/页面截图不提交仓库；交付看本地 runs。

## 已知限制

- 不是 45.0s，是 40.7s；旁白更紧，适合信息流。
- 录屏中处理过程做了 4× 加速，保留“真实录屏”标识。
- 结果表是真实运行输出；演示数据为公开汇率数据。
- 还没有竖屏 15s 版本、封面图、朋友圈/小红书文案排版。
## Clean 版（3 轮修复后）

- 横屏：pipeline/runs/demo-workbuddy-collector/collector-promo-clean.mp4（40.7s / -16.2 LUFS）
- 竖屏：pipeline/runs/demo-workbuddy-collector/collector-vertical-clean.mp4（16.3s / -16.7 LUFS）
- 封面：pipeline/runs/demo-workbuddy-collector/collector-cover.png
- 隐私：无本地路径、无无关任务名
- 修复记录：research/2026-11-11-采集专家视频修复3轮.md
