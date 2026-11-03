# skills/ · Agent 技能包

> 技能 = **触发条件 + 可执行步骤 + 失败处理 + 自检**。用于把 SOP / 工作流固化给 Agent，避免每次临场发挥。

## 技能清单

| 技能 | 用途 | 依赖 | 状态 |
|---|---|---|---|
| [video-sop-selector](video-sop-selector/SKILL.md) | 按视频形态 / 平台 / 素材路由到正确 SOP | sop/、templates/ | 可用 |
| [video-project-init](video-project-init/SKILL.md) | 新建项目目录、Brief、分镜表、交付规格、manifest | templates/、python3 | 可用（已实测） |
| [ffmpeg-render](ffmpeg-render/SKILL.md) | 导出 / 转码 / 批量 / 竖屏适配 / 响度标准化 | ffmpeg 9.0.2、python3 | 可用（已实测） |
| [subtitle-pipeline](subtitle-pipeline/SKILL.md) | 断句校时 → SRT/ASS → 烧录 / 软封装 / 外挂 | ffmpeg + Pillow | 可用（已实测） |
| [qc-deliver](qc-deliver/SKILL.md) | 规格核验 + 响度 / 黑帧 / 命名检查，PASS/FAIL 阻断 | ffprobe、python3 | 可用（已实测） |

> 全量清单以 [INDEX.md](../INDEX.md) 的「技能」节为准（脚本自动扫描）。

## 目录规范

```text
skills/<name>/
├── SKILL.md            # 必需：frontmatter(name/description/version) + 正文
├── references/         # 可选：长文档、模板、参数表
└── scripts/            # 可选：可执行脚本（带 --help 与自检）
```

## SKILL.md 规范

1. frontmatter 必填 `name`（与目录名一致）、`description`（写清**何时触发**）、`version`。
2. 正文必备节：

```text
## 何时使用 / 不适用
## 输入（缺什么问什么）
## 步骤（可执行、含命令）
## 输出格式
## 失败处理
## 自检
## 参考
```

3. `description` 是路由依据：写「做什么 + 触发场景 + 边界」，不写营销词。
4. 命令必须能在本机直接跑（环境见 [本机环境](../knowledge/环境/environment-local.md)）；有前提要写明。
5. 不复制知识库大段内容，用相对链接引用。
6. 技能自身不存数据、不提交成片。

## 加载方式

- Agent 可直接读取 `SKILL.md` 并按步骤执行（本仓协作默认方式）。
- 接入 DSH 技能系统时，将 `skills/<name>/` 放入 DSH 技能目录后按名加载；目录位置以 DSH 配置为准。

## 新增技能

1. 确认有稳定复用的流程（至少被 2 条 SOP 用到）。
2. 建目录 + `SKILL.md`，按上面规范写。
3. 在清单登记；更新 [INDEX.md](../INDEX.md)。
4. 跑 `python3 scripts/validate.py`（校验 name/description/version 与目录名）。