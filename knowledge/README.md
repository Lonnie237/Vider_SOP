# knowledge/ · 知识库

> 收录「工具怎么用、方法为什么有效、流程怎么串」。每条独立成文件，frontmatter 可被脚本索引。

## 目录

| 目录 | 放什么 | 模板 |
|---|---|---|
| [开源库/](开源库/) | 单个库/工具的定位、能力、安装、最小示例、坑位 | [知识条目-开源库](../templates/知识条目-开源库.md) |
| [方法论/](方法论/) | 通用方法：钩子、叙事、节奏、字幕、声音、调色 | [知识条目-方法论](../templates/知识条目-方法论.md) |
| [工作流/](工作流/) | 跨环节流程：素材管理、转码交付、自动化、平台规格 | [知识条目-方法论](../templates/知识条目-方法论.md) |
| [环境/](环境/) | 本机/目标环境、依赖、性能基线 | [知识条目-方法论](../templates/知识条目-方法论.md) |

## 导航

- **按环节找**：S0 选题 → S1 脚本分镜 → S2 拍摄 → S3 素材 → S4/S5 剪辑 → S6 声音 → S7 字幕 → S8 调色 → S9 包装 → S10 交付 → S11 质检（见 [分类体系](../docs/知识分类体系.md)）。
- **按需求找**：先看 [开源库/capability-matrix.md](开源库/capability-matrix.md)，再看 [开源库/selection-guide.md](开源库/selection-guide.md)。
- **全量清单**：[INDEX.md](../INDEX.md)（自动生成，按状态与更新时间筛）。

## 当前覆盖（P1 已完成，2026-11-03）

| 类别 | 条目 |
|---|---|
| 开源库（11 条） | ffmpeg、moviepy、pyav、auto-editor、opentimelineio、remotion、editly、blender-vse、manim、whisperx、hyperframes；另有 [能力矩阵](开源库/capability-matrix.md)、[选型指南](开源库/selection-guide.md)（scenedetect 等仍只在矩阵） |
| 方法论（12 条） | 钩子与留存、叙事结构、节奏与卡点、字幕与信息密度、声音设计与混音、调色基础、纯代码视频风格库（11 种配方）、纯代码视频主题库（8 套配色）、剪辑决策方法、科普视频方法、单行字幕与持续动效、常用视频版式（20 种版面与处理方式） |
| 工作流（9 条） | 素材管理与代理剪辑、转码与交付、自动化流水线、平台规格与发布、能力矩阵、选型指南、纯代码视频管线、PPT/文档转视频、产品演示视频 |
| SOP（11 条） | 口播 / 混剪 / 切片 / Vlog / 教程 / 访谈 / 宣传片 / 数据动画 / 产品说明 / PPT 转视频 / 科普动画；路由见 [sop/README](../sop/README.md) |
| 环境（1 条） | 本机环境（macOS / Apple Silicon）基线，含 ffmpeg 能力边界与性能实测 |
| 调研 | [2026-11-03 开源视频编辑生态](../research/2026-11-03-开源视频编辑生态.md) |

## 新增一条知识

1. 复制对应模板到目标目录，文件名用英文 kebab-case（如 `knowledge/开源库/ffmpeg.md`）。
2. 填 frontmatter（`id: kb/<文件名>`），按模板写全必备节。
3. 事实标 `[事实]` / `[实测]` / `[推断]`，文末列来源。
4. 更新 [能力矩阵](开源库/capability-matrix.md)（工具类）与相关 SOP 的「关联条目」。
5. 跑 `python3 scripts/build_index.py` 与 `python3 scripts/validate.py`。

## 写作要求

见 [写作与标注规范](../docs/写作与标注规范.md) 与 [质量门禁](../docs/质量门禁.md)。一句话：**能照着干**。