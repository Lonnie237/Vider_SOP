# 初中数学第一课 · S1–S4 样片

- 日期：2026-11-06
- 内容：负数与数轴第一课，S1 开场 → S2 规定 → S3 0 → S4 数轴
- 状态：**v2 动态样片；只验证视觉/字幕/节奏，不是完整课**
- 成片（本地）：../../runs/demo-math-first-lesson/sample-s1-s4.mp4
- 时长：74.58s / 2237 帧 / 1920×1080 / 30fps / -16.0 LUFS
- 旁白：Qwen TTS longanlingxin_v3.1，speech_rate=1.05；无 BGM
- 字幕：43 条单行静态 cue，无逐词高亮；cue 为 TTS 文本精确子串
- 声音：5 次调用，input 328 / output 920 / total 1248 tokens，API characters 610；见 TTS_BILLING_MATH_SAMPLE.md
- 修复记录：[v2 P0 修复](../../../research/reviews/2026-11-06-math-sample-fixlog.md)
- E2E 评审（v1）：[2026-11-06-math-sample-e2e.md](../../../research/reviews/2026-11-06-math-sample-e2e.md)

## 这版验证了什么

1. 深色黑板 + 粉笔白 + 温度红蓝的视觉方向；
2. S1 温度计下降 + 问题卡按旁白出现；
3. S2 两种「规定」并排，当前栏亮、另一栏压暗；
4. S3 三格按锚点出现，大 0「分界」最后出现；
5. S4 先画线/刻度，再按锚点放点、预测、答案；
6. 单行静态字幕、无底部线、无逐词高亮；
7. 首帧不空：标题 + 温度计 + 第一句问题直接在场。

## 已知限制

- 这是 **74.6s 的 S1–S4 段**，不是 40s 预告，也不是完整 4:15；
- S3 开头约 1.4s 只有标题；S4 中段线/刻度较长；
- S3 的 0 个苹果/0℃ 图标是简洁版；
- 没有真实学生试播；语速约 4 字/秒，需人耳抽听；
- 只做了 Lead 复核，未做二轮独立 Agent 复审。

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
- 再用这套锚点机制做 S5–S7，拼全片；
- 5–10 人前测/后测，验证每目标 ≥4/5。