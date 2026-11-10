# 初中数学第一课 · 负数与数轴（全片）

- 日期：2026-11-09
- 标题：0℃ 以下，也是温度
- 内容：S0 封面 → S1 开场 → S2 规定 → S3 0 → S4 数轴 → S5 两个负数 → S6 三个检查 → S7 小结+ quiz
- 状态：**基础 4:08 成片已跑通；MG 复合 v1 已加，90s 片段已重渲染；全片待重渲染/复核**
- 基础成片（本地）：../../runs/demo-math-first-lesson/math-first-lesson-full.mp4
- MG 复合 90s 片段（本地）：../../runs/demo-math-first-lesson/math-first-lesson-mg-excerpt.mp4
- MG 方法：[MG 注意力复合](../../../knowledge/方法论/mg-attention-composite.md)
- 字幕（本地）：../../runs/demo-math-first-lesson/math-first-lesson-full.srt
- 依据：脚本 v4 / 分镜 v1 / 版式卡 v1（../../../research/2026-11-05-初中数学第一课-*.md）

## 规格

- 时长：248.107s / 7443 帧（验收区间 245–265s，即 4:15±10s）✓
- 分辨率：1920×1080 / 30fps / h264 + aac
- 响度：-16.01 LUFS，true_peak -4.48 dB（两遍 loudnorm，TP=-1.5 / LRA=11）✓
- 字幕：104 条单行静态 cue，最长 15 字（≤16），0 重叠；cue 为 TTS 文本精确子串 ✓
- 黑帧检测：无真黑帧（pix_th=0.02）✓
- 预测停顿：S4 数轴、S5 比较、S6 检查均留停顿，答案在停顿后高亮，不提前泄露 ✓
- 无 BGM；首帧非空（封面标题 + 温度计在场）

## 声音 / 计费

- 音色：Qwen TTS longanlingxin_v3.1，speech_rate=0.75（约 3 字/秒，贴合初一）
- 12 次调用；input 815 / output 2175 / total 2990 tokens；API characters 1519
- 原始 -19.4 LUFS → 归一 -16.0 LUFS；见 TTS_BILLING_MATH_FULL.md

## MG 复合 v1（2026-11-10）

- 章节卡：每 Scene 开始 0.6s 全屏「编号 + 标题」；
- 镜头切分：6.5s 一次构图切换（近景/中景/全景）；
- 进度条 + 章节徽标 + 粉笔擦除线；
- 当前卡放大 1.03 + 琥珀光；
- 背景网格/尘埃分层缓慢漂移；
- 90s 片段实测 90.048s / 2701 帧 / -16.05 LUFS。
- 全片**尚未重渲染**，基础全片的旧 QC 不适用于 MG 版。

## QC（基础片）

- 脚本：tools/qc_full.py；报告：out/qc-full/report.json（全项通过）
- 抽帧：out/qc-full/contact.png（5×5，fps=1/12）+ 各场景关键帧目检
- blackdetect 校准：深色黑板底 #101418（luma≈0.075）是有意设计，非缺陷；
  用 pix_th=0.02 只检真黑，避免把「只有标题的过渡帧」误判为黑帧。

## 工程

- 入口：src/index.ts
- 合成：src/MathLesson.tsx（全片 S0–S7）；样片合成 src/MathSample.tsx 保留不动
- 时间线/字幕/锚点：src/timeline-full.json、src/cues-full.json、src/anchors-full.json
- 配音/字幕/锚点生成：tools/make_audio_full.py
- 渲染产物：out/full-raw.mp4、out/full.srt（交付副本在 runs/）

## 复现

    cd pipeline/remotion/junior-math-first-lesson
    python3 tools/make_audio_full.py
    CHROME="$HOME/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    npx remotion render src/index.ts MathLesson out/full-raw.mp4 --browser-executable="$CHROME" --video-bitrate=8M
    python3 tools/qc_full.py

---

## 附：S1–S4 样片（2026-11-06，冻结里程碑）

- 内容：S1 开场 → S2 规定 → S3 0 → S4 数轴；**74.58s 样片，不是完整课**
- 成片：../../runs/demo-math-first-lesson/sample-s1-s4.mp4
- 时长：74.58s / 2237 帧 / 1920×1080 / 30fps / -16.0 LUFS
- 旁白：longanlingxin_v3.1，speech_rate=1.05；43 条 cue；5 次调用 total 1248 tokens
- 合成：src/MathSample.tsx；数据：src/timeline.json、cues.json、anchors.json；生成 tools/make_audio.py
- 修复记录：[v2 P0 修复](../../../research/reviews/2026-11-06-math-sample-fixlog.md)
- E2E 评审（v1）：[2026-11-06-math-sample-e2e.md](../../../research/reviews/2026-11-06-math-sample-e2e.md)
- 样片验证了深色黑板视觉、温度计下降、双栏压暗、三格 0、数轴锚点放点/预测/答案、单行静态字幕、首帧非空。
- 全片在其锚点机制上扩展 S5–S7，并把语速从 ~4 字/秒降到 ~3 字/秒。

## 下一步

- 真实学生前测/后测（5–10 人），验证每学习目标 ≥4/5；
- 人耳抽听全片语速与停顿；按需微调 S5/S6 节奏。