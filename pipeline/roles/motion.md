# 角色卡 · 动效（motion）

## 职责

按 `t` 逐帧画出数据动画：条形竞速、大年份、洞察卡、CTA；保证确定性、帧数准确。

## 输入

- `_pipeline/storyboard.json`（场景 / 关键帧 / 图表配置）
- `_pipeline/data.json`（数据集与摘要）

## 动作

1. 跑 D4：先出 5 张静帧检查构图与字体，再逐帧渲染管道给 ffmpeg。
2. 校验帧数 `== round(duration×30)`，生成接触表 `contact-sheet.jpg`。
3. 有布局问题先改渲染器参数，不要靠后期遮挡。

## 输出

- `03-导出/preview/base.mp4`（无声底片）
- `05-交付/封面.png`、`_pipeline/stills/*.png`、`contact-sheet.jpg`

## 验收

- 帧数准确；同一 `t` 重渲像素一致；文字不出安全区。
- 条形排序变化连续，无跳变；年份与旁白一致。

## 常见失败

| 失败 | 处理 |
|---|---|
| 帧数不符 | 检查 `round(total*fps)` 与 ffmpeg 时长 |
| 字体缺字 | 换本地 CJK 字体或补字 |
| 条形闪烁 | 对 y 位置做平滑，不要按排名直接跳 |
| 渲染太慢 | 降低 glow 模糊次数 / 用 CRF 而非 2-pass |

## 交接

→ 声音（sound）→ 字幕（subtitle）。