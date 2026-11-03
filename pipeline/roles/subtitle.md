# 角色卡 · 字幕（subtitle）

## 职责

把口播文本变成可读字幕，校验 CPS / 行宽 / 时间轴，并烧录进画面。

## 输入

- `_pipeline/voice.json`（逐 beat 时间）
- `03-导出/preview/base_av.mp4`

## 动作

1. 跑 S5：按 beat 时间切分字幕（每屏 ≤ 16 字），生成 `04-字幕/srt/voice.srt`。
2. 用 `subtitle.py validate` 校验；有告警就改断句。
3. 用 `burn.py` 烧录（本机无 libass，自动走 Pillow overlay）。

## 输出

- `04-字幕/srt/voice.srt`
- `03-导出/preview/subbed.mp4`

## 验收

- 无重叠、无超长行；字幕不出底部安全区；错别字为零。

## 常见失败

| 失败 | 处理 |
|---|---|
| 字幕与语音不同步 | 回 S2 检查时间轴，不要手改 SRT 了事 |
| 单行太长 | 缩短 cue 或减字号（≤ 58px） |
| 烧录报错 | 先跑 `subtitle.py probe`；缺 libass 时用 Pillow 方案 |

## 交接

→ 剪辑（editor）导出、质检（qc）验收。