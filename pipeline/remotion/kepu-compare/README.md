# kepu-compare · WorkBuddy vs Qoder 科普视频（Remotion）

60 秒 16:9 科普短视频示例：对比腾讯 WorkBuddy 与阿里 Qoder 的定位、原因与选择。

## 运行

```bash
cd pipeline/remotion/kepu-compare
npm install
python3 tools/make_audio.py          # 生成旁白与 src/timeline.json
npx remotion studio                  # 预览
npx remotion render src/index.ts KepuCompare out/video.mp4 \
  --codec=h264 --crf=18 \
  --browser-executable="$HOME/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
```

## 结构

- `src/Video.tsx`：7 个场景（开场/定位/WorkBuddy/Qoder/为什么/怎么选/结尾）+ 字幕 + 进度条
- `src/timeline.json`：逐句旁白时间轴（由 tools/make_audio.py 生成）
- `public/voice.wav`：旁白音频（生成物，gitignore）
- `FACTS.md`：事实台账与来源

## 实测结果（2026-11-05，本机）

| 项 | 结果 |
|---|---|
| 成片 | `out/final.mp4`（工作副本：`pipeline/runs/demo-kepu-compare/workbuddy-vs-qoder.mp4`） |
| 时长 / 帧数 | 54.5s / 1633 帧 @30fps |
| 规格 | 1920×1080 / H.264 High / AAC 48kHz / -13.9 LUFS |
| 大小 / 码率 | 约 10.3 MB / 1.5 Mbps（深色图形内容自适应） |
| 环境 | Node 26、Remotion 4.0.540、Chrome for Testing（Playwright 缓存） |
| 渲染 | 一次 Remotion render + 一次 ffmpeg 交付编码（8M 目标，实际内容自适应） |
| 字幕 | React 内烧录；另出 `subtitles.srt` |

## 设计

- 声音为轴：旁白逐句合成 → 时间轴 → 场景/字幕/动效对齐
- 事实台账：每个 claim 有来源；推断单独标注
- 16:9 / 1920×1080 / 30fps；深色底 + 腾讯蓝 / 阿里橙双色编码
- 字幕烧在 React 内（不依赖 ffmpeg 字幕滤镜）