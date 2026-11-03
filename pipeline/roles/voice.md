# 角色卡 · 配音（voice）

## 职责

把口播稿变成配音音轨与精确到句的时间轴；决定音色、语速、停顿。

## 输入

- `pipeline/runs/<项目>/_pipeline/brief.json`
- 音色候选：本机 `say -v '?' | grep zh_CN`（默认 Tingting）

## 动作

1. 跑 `python3 pipeline/stages/s2_tts.py --run-dir <项目>`（逐 beat 合成 + 拼接）。
2. 看 `_pipeline/voice.json` 的 `chars_per_sec` 是否在 4–7 区间；默认语速 1.45 倍（`brief.voice.rate_multiplier`），S2 自动校准 `say -r` 并记录 `rate_calibration`。
3. 换音色：`--voice`；改语速：`--rate-multiplier 1.2` 或 `--rate-wpm 240`；改完重跑 S2 起的所有阶段。

## 输出

- `01-素材/音频/voice.wav`（48 kHz 单声道，含 0.4s 前导与 0.8s 尾留白）
- `_pipeline/voice.json`（逐 beat 起止时间）

## 验收

- 时间轴与音频一致（后续字幕直接使用）。
- 无明显吞字、断句怪异；口播语速 4–6 字/秒。

## 常见失败

| 失败 | 处理 |
|---|---|
| 音色不存在 | `say -v '?'` 查可用音色，改 `--voice` |
| 单句过长导致一口气读不完 | 回编导拆句，不要靠加速硬压 |
| 时间轴与音轨错位 | 重跑 S2；不要手改 voice.json |

## 交接

→ 剪辑（editor）与声音（sound）：音轨与时间轴就绪。