# kepu-compare · WorkBuddy vs Qoder 科普视频（Remotion）

60 秒 16:9 科普短视频示例：对比腾讯 WorkBuddy 与阿里 Qoder 的定位、原因与选择。

## 运行

```bash
cd pipeline/remotion/kepu-compare
npm install
# 旁白：Qwen TTS（需要 ../../../.secrets/dashscope_key 与 .venv-tts）
.venv-tts/bin/python tools/make_audio_qwen.py
# 离线替代：
python3 tools/make_audio.py          # edge-tts / say
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
| 时长 / 帧数 | 66.0s / 1978 帧 @30fps |
| 规格 | 1920×1080 / H.264 High / AAC 48kHz / -16.0 LUFS |
| 大小 / 码率 | 约 11.6 MB / 1.4 Mbps（深色图形内容自适应） |
| 环境 | Node 26、Remotion 4.0.540、Chrome for Testing（Playwright 缓存）、阿里云百炼 Qwen TTS（qwen-audio-3.1-tts-flash / longanhuan_v3.1） |
| 渲染 | Remotion render + ffmpeg 两遍 loudnorm（-16 LUFS）+ 8M 目标编码；无 BGM |
| TTS 用量 | input 292 / output 789 / total 1081 tokens（10 次调用，API 返回）；详见 [TTS_BILLING.md](TTS_BILLING.md) |
| 字幕 | React 内烧录；另出 `subtitles.srt` |

## 音色与语速（2026-11-05）

- 官方音色列表：[Qwen-Audio-TTS 音色列表](https://www.alibabacloud.com/help/zh/model-studio/qwen-audio-tts-voice-list)（音色必须匹配模型，不能跨模型混用）
- 当前视频使用的 `longanhuan_v3.1` 是「亲切活泼」女声，偏社交/生活；严肃科普建议换更稳的旁白音色。
- 试听包：`voice-samples/audition-qwen-voices.mp3`（A 龙安灵心 / B 龙安风悦 / C 于小云 / D 温怀清 / E 许玉远 / F 许南川 / G 安明远 / H 龙书）
- 语速试听：`voice-samples/audition-qwen-rate.mp3`（0.9 / 1.0 / 1.05 / 1.1 / 1.2，龙安灵心）
- `speech_rate` 范围 0.5–2.0，默认 1.0；科普建议 0.95–1.05，偏快用 1.1，偏慢用 0.9。
- 试听调用计费见 [TTS_AUDITION.md](TTS_AUDITION.md)；指定音色语速试听见 [TTS_RATE_AUDITION.md](TTS_RATE_AUDITION.md)。

## 设计

- 声音为轴：旁白逐句合成 → 时间轴 → 场景/字幕/动效对齐
- 事实台账：每个 claim 有来源；推断单独标注
- 16:9 / 1920×1080 / 30fps；深色底 + 腾讯蓝 / 阿里橙双色编码
- 字幕烧在 React 内（不依赖 ffmpeg 字幕滤镜）