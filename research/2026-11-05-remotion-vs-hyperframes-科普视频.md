# Remotion vs HyperFrames · 科普视频技术栈调研

- 日期：2026-11-05
- 调研人：lead
- 目标：搞清楚「大多数人做科普类视频用 Remotion / HyperFrames」这句话背后的技术栈、生态与可复用方法，提炼进本仓 SOP/SKILL。
- 访问日期：2026-11-05（所有外部信息）

## 1. 两个框架是什么

| 维度 | Remotion | HyperFrames |
|---|---|---|
| 定位 | 用 React 组件写视频（programmatic video） | 用 HTML/CSS/JS 写视频，Agent 优先 |
| 归属 | Remotion GmbH | HeyGen 开源（Apache-2.0） |
| 渲染 | React 树 → 逐帧；Node/Lambda/客户端 | 无头 Chrome 逐帧 seek + FFmpeg 编码 |
| 动画 | useCurrentFrame/interpolate/spring；CSS/Three.js 等 | 可 seek 的动画时间线（GSAP/CSS/Lottie/Three.js/Anime.js） |
| 确定性 | 同一输入同一输出 | 同一输入同一输出（seek each frame） |
| 入口 | `npx create-video@latest`；Remotion Studio | `npx hyperframes init/preview/render/lint`；Studio 桌面端 |
| Agent 支持 | 官方 Agent Skills + 模板 | 9 个技能（/hyperframes、/hyperframes-cli、/hyperframes-registry、/media-use 等）+ 450 个 registry 区块 |
| 许可 | 特殊许可：个人/小团队免费，4 人以上公司需商业许可 | Apache-2.0，本地渲染免费、无需账号 |
| 生态 | 极大（1200+ 页文档、模板、Lambda、社区） | 较新但增长快；含 Remotion→HyperFrames 迁移技能与 API 映射 |

结论：**Remotion 是「React 程序化视频」的事实标准；HyperFrames 是「HTML 原生 + Agent 优先」的后来者**，用 Agent 写视频时更轻，且不要求 React。

## 2. 科普视频生态扫描（Remotion 系）

| 仓库 | 定位 | 可复用点 | 许可 |
|---|---|---|---|
| [sixwei2025/psych-kepu-video-skill](https://github.com/sixwei2025/psych-kepu-video-skill) | 心理科普短视频 Skill | **整条片子由一份 JSON 脚本驱动**；16:9/45s；首帧封面；render.sh + qc.sh | MIT |
| [liangdabiao/video-skills-toolkit](https://github.com/liangdabiao/video-skills-toolkit) | 6 类 Remotion 模板集 | 口播/公众号文章/几何数学/纸片分层/手绘故事/音频转字幕；**声音为轴、字幕为唯一基准** | 见仓库 |
| [ShiyouQi888/2D-kepu-donghua-Skill](https://github.com/ShiyouQi888/2D-kepu-donghua-Skill) | 2D 科普动画完整方法 | 4 套模板、5 个确认点、30s 样片验收、自动 QC、交付目录规范 | 见仓库 |
| [howznguyen/shorts-kit](https://github.com/howznguyen/shorts-kit) | 竖屏短科普生产套件 | fact ledger、20+ 故事流、word-timed 字幕、安全区、9 技能 | 见仓库 |
| [vincentwei1021/anything2explainer](https://github.com/vincentwei1021/anything2explainer) | 主题→科普讲解视频 | Remotion 代码绘制、配音、4'54" 示例、44 句/1490 字 | 见仓库 |
| [dy-hashiqi/VibeDS-skill](https://github.com/dy-hashiqi/VibeDS-skill) | HyperFrames 16:9 科普技能 | HTML+GSAP 分镜、lint→preview→render 闭环、40s 熵增示例 | Apache-2.0 |

## 3. 共性方法（真正值得吸收的部分）

1. **声音是轴，字幕是唯一基准**：逐字稿 → TTS → 字幕（带时间戳）→ 画面/动画/音效全部对齐字幕；不要先画画面再配音。
2. **脚本/JSON 单一数据源**：整条片由 script.json / timeline 驱动；画面、字幕、音效共享同一时间常数。
3. **事实台账（fact ledger）**：科普内容先把 claim 核对来源，再写进脚本；shorts-kit 用 linter 强制。
4. **模板/主题先选后做**：4 套视觉模板（2D 科普）、4 套大字卡版式、11 风格/8 主题（code-video-showcase）；先锁定再写代码，避免中途换皮。
5. **5 个确认点**：模板 → 时长/语言 → 口播文案 → 配音 → 30s 样片；确认后才全量开发。
6. **QC 规则化**：文字溢出、越界、卡片裁切、静止过久、末拍停留、字幕安全区；自动检查 + 人工抽帧。
7. **低清 proof → 高清出片**：先低分辨率验证节奏，再高画质渲染。
8. **交付即工程**：research/、script/、timeline、分镜、src/shots、qc/、renders、交付说明一起交。

## 4. 我们怎么吸收（落地计划）

- 知识：[HyperFrames 条目](../knowledge/开源库/hyperframes.md)、[科普视频方法](../knowledge/方法论/kepu-video-method.md)；补写 [Remotion 条目](../knowledge/开源库/remotion.md) 的生态节。
- 流程：新增 [科普动画短视频 SOP](../sop/short-kepu-motion.md)，把「声音为轴 + 事实台账 + 30s 样片 + QC」写成阶段与门禁。
- 技术路线：
  - 需要 React/复杂交互/大批量：Remotion。
  - 需要 HTML/JS/GSAP、Agent 直接写、少依赖：HyperFrames。
  - 我们的数据动画目前用 Pillow/ffmpeg；未来可加 Remotion/HyperFrames 渲染器，把「模板/主题」真正接进流水线。
- 暂不做：不引入生成式视频/图像模型；不复制仓库代码；许可存疑的仓库只参考方法。

## 5. 待确认 / 风险

- [待确认] video-skills-toolkit / 2D-kepu / shorts-kit / anything2explainer 的 LICENSE 未逐一确认，复用前需核对。
- [待确认] HyperFrames 与 Remotion 的迁移成本（Remotion→HF 有官方技能与 API map，但 useState 等需 interop）。
- [待确认] 本机 Node 26 / Chrome Headless 是否可直接跑 HyperFrames；Remotion 4.0.540 曾在本机渲染成功。

## 来源

1. [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（Apache-2.0，访问 2026-11-05）
2. [remotion-dev/remotion](https://github.com/remotion-dev/remotion)（Remotion License，访问 2026-11-05）
3. 科普 Skill 仓库：psych-kepu、video-skills-toolkit、2D-kepu-donghua、shorts-kit、anything2explainer、VibeDS-skill（访问 2026-11-05）
4. 本仓：[来源台账](来源台账.md)
