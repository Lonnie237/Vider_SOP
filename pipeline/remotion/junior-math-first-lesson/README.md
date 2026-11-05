# 初中数学第一课 · S1–S4 样片

- 日期：2026-11-05
- 内容：负数与数轴第一课，S1 开场 → S2 规定 → S3 0 → S4 数轴
- 状态：**第一版动态样片；只验证视觉/字幕/节奏，不是完整课**
- 成片（本地）：pipeline/runs/demo-math-first-lesson/sample-s1-s4.mp4
- 时长：61.65s / 1849 帧 / 1920×1080 / 30fps / -15.9 LUFS
- 旁白：Qwen TTS longanlingxin_v3.1，speech_rate=1.05；无 BGM
- 字幕：29 条单行静态 cue，无逐词高亮
- 声音：4 次调用，input 261 / output 776 / total 1037 tokens，API characters 444；见 TTS_BILLING_MATH_SAMPLE.md

## 这版验证了什么

1. 深色黑板 + 粉笔白 + 温度红蓝的视觉方向；
2. S1 温度计从 3℃ 降到 -3℃；
3. S2 两种「规定」并排，当前栏亮、另一栏压暗；
4. S3 0 个 / 0℃ / 0 米三格 + 大 0「分界」；
5. S4 数轴先画结构再放点，-3/-1 预测后给答案；
6. 单行静态字幕、无底部线、无逐词高亮；
7. 首帧不空：标题 + 温度计 + 第一句问题直接在场。

## 已知限制

- 这是 **61s 的 S1–S4 段**，不是 40s 预告，也不是完整 4:15；
- S3 的 0 个苹果/0℃ 图标是代码绘制的简洁版，后续可细化；
- 没有真实学生试播；字幕断句仍需按听感微调；
- TTS 计费只记了聚合值，未落逐次 raw JSON（生成脚本后续补）。

## 工程

- 入口：src/index.ts
- 合成：src/MathSample.tsx
- 时间线/字幕/锚点：src/timeline.json、src/cues.json、src/anchors.json
- 音频生成：tools/make_audio.py
- 线框生成：tools/make_wireframes.py
- 渲染：npx remotion render src/index.ts MathSample out/sample.mp4

## 复现

    cd pipeline/remotion/junior-math-first-lesson
    python3 tools/make_audio.py
    CHROME="$HOME/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    npx remotion render src/index.ts MathSample out/sample.mp4 --browser-executable="$CHROME"

## 下一步

- 按反馈改 S1/S2/S3/S4 的构图/节奏；
- 再做 S5–S7，拼 4:15 全片；
- 5–10 人前测/后测，验证每目标 ≥4/5。
