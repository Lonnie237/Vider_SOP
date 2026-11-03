# 角色卡 · 声音（sound）

## 职责

把配音归一到平台响度，并确保音画同长、不爆音。

## 输入

- `01-素材/音频/voice.wav`
- `manifest.json` 的 `loudness_lufs`（短视频 -14）

## 动作

1. 跑 S4：两遍 `loudnorm` 归一到目标响度，真峰值 ≤ -1.5 dBTP。
2. 与底片合板，音频 AAC 48 kHz / 192 kbps。
3. 检查 `_pipeline/audio.json` 的 before/after 响度。

## 输出

- `01-素材/音频/voice_norm.wav`
- `03-导出/preview/base_av.mp4`

## 验收

- 实测响度与目标偏差 ≤ 1 LU；无削波；时长与视频一致。

## 常见失败

| 失败 | 处理 |
|---|---|
| 响度偏差大 | 检查是否二次归一（导出阶段也要 `--no-audio-normalize`） |
| 有爆音 | 降 TP 或加 `alimiter` |
| 音画不同长 | 用 `-shortest` 或补齐尾留白 |

## 交接

→ 字幕（subtitle）：音轨已定型，可直接烧录。