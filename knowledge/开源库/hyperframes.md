---
id: kb/hyperframes
title: "HyperFrames · HTML 原生、Agent 优先的视频渲染框架"
type: 工具
domain: [动效, 包装, 自动化, 交付]
status: 可用
confidence: 高
license: "Apache-2.0"
repo: "https://github.com/heygen-com/hyperframes"
docs: "https://hyperframes.heygen.com/docs"
language: TypeScript / HTML
platform: [macOS, Linux, Windows, 浏览器]
tags: [HyperFrames, HTML视频, 逐帧渲染, GSAP, Agent Skill, 确定性, HeyGen]
related: [kb/remotion, kb/code-video-pipeline, kb/kepu-video-method, kb/ffmpeg]
updated: 2026-11-05
owner: lead
---

# HyperFrames · HTML 原生、Agent 优先的视频渲染框架

## 一句话定位

用 HTML/CSS/JS + 可 seek 动画时间线写视频，由无头 Chrome 逐帧截图、FFmpeg 编码成确定性 MP4；与 Remotion 并列的「代码视频」路线，但**不要求 React**，对 Agent 更友好。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| HTML 原生视频：GSAP/CSS/Lottie/Three.js/Anime.js | 复杂 React 组件生态（需 interop / 迁移） |
| 确定性渲染：同一输入同一帧 | 生成式视频/图像（不调用生成模型） |
| Agent 直接写 HTML 并 `lint→preview→render` | 复杂后期合成与多轨音频（需外部工具） |
| 450+ registry 区块、9 个官方技能 | 成熟度/生态仍小于 Remotion |
| 本地免费渲染、无需账号 | 需要 Node 22+、FFmpeg、Chrome |

## 核心能力

- **组合（composition）**：一个 HTML 文件即一条/一段视频；用可 seek 的时间线（GSAP 等）驱动。
- **确定性渲染**：headless Chrome 逐帧 seek，FFmpeg 编码；同一 HTML + 变量 → 同一 MP4。
- **CLI**：`npx hyperframes init/preview/render/lint/add/benchmark/skills`；`hyperframes.json` 管项目、`--variables` 管参数。
- **技能**：9 个（/hyperframes、/hyperframes-cli、/hyperframes-registry、/media-use 等），支持 Claude Code/Codex/Cursor 等。
- **Registry**：约 450 个可编辑区块（转场、标题、动效字、字幕、图表、地图、3D、运镜）。
- **迁移**：官方提供 Remotion→HyperFrames 的 API 映射与 interop 技能。

## 安装 / 获取

```bash
node -v                      # 需 >= 22
npx hyperframes@latest doctor
npx hyperframes init my-video && cd my-video
npx hyperframes preview
npx hyperframes render --output out.mp4
```

Agent 侧：`npx hyperframes skills update` 安装核心技能；或在 Claude Code 里 `claude plugin marketplace add heygen-com/hyperframes`。

## 最小可用示例

```html
<!-- index.html：一条 3s 标题动画（示意；以官方 init 模板为准） -->
<div id="stage" data-duration="3" style="width:1920px;height:1080px;background:#0e0e0d">
  <h1 id="title" style="color:#f5f0e8;font:900 120px/1.1 system-ui;padding:180px 120px">
    Hello HyperFrames
  </h1>
</div>
<script>
  // 用可 seek 的动画库（如 GSAP）把元素绑定到时间线
  const tl = gsap.timeline({ paused: true });
  tl.from("#title", { opacity: 0, y: 80, duration: 1.2, ease: "power3.out" });
  window.__timeline = tl;   // HyperFrames 渲染器按帧 seek
</script>
```

```bash
npx hyperframes lint
npx hyperframes preview
npx hyperframes render --output hello.mp4
```

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| HTML/JS 零 React 门槛，Agent 易生成 | 生态较新，复杂场景资料少于 Remotion |
| 确定性、本地免费、Apache-2.0 | 需 Node 22+、Chrome、FFmpeg；首次下载/安装 |
| Registry 区块多，起片快 | 复杂交互/状态（如 React hooks）需 interop |
| 技能体系完整，lint/preview/render 闭环 | 官方文档站偶尔访问慢；以仓库 README/docs 为准 |
| 与 Remotion 有迁移路径 | 4K/长片渲染性能取决于机器 |

## 适用 / 不适用

- 适用：科普/知识动画、产品介绍、数据图表动效、Agent 自动出片、HTML 原型转视频。
- 不适用：需要成熟 React 生态/复杂组件库、已有 Remotion 工程且迁移成本高、需要生成式素材。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：[科普动画短视频 SOP](../../sop/short-kepu-motion.md)
- 对照：[Remotion 条目](remotion.md)；方法：[科普视频方法](../方法论/kepu-video-method.md)、[纯代码视频管线](../工作流/code-video-pipeline.md)
- 渲染/编码：[ffmpeg](ffmpeg.md)

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-05 | 信息核验 | GitHub README / docs / 第三方技能仓库 | Apache-2.0；Node 22+；CLI 与 9 技能；未本机安装 |
| 2026-11-05 | 本机 Node 26 / ffmpeg 9.0.2 | 未安装 HyperFrames | [待确认] 首次渲染需下载 Chrome Headless Shell |

## 来源

1. [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（Apache-2.0，访问 2026-11-05）
2. [HyperFrames 文档](https://hyperframes.heygen.com/docs)（访问 2026-11-05）
3. [HyperFrames FAQ](https://hyperframes.heygen.com/faq)（访问 2026-11-05）
4. [dy-hashiqi/VibeDS-skill](https://github.com/dy-hashiqi/VibeDS-skill)（HyperFrames 科普技能示例，Apache-2.0）