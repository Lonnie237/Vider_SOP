---
id: kb/remotion
title: "Remotion · 用 React 代码渲染视频"
type: 库
domain: [字幕, 动效, 交付, 自动化]
status: 可用
confidence: 中
license: "Remotion License（非 OSI 开源许可；个人与 ≤3 人公司免费，4 人及以上需 Company License）"
repo: "https://github.com/remotion-dev/remotion"
docs: "https://www.remotion.dev/docs/"
language: TypeScript
platform: [macOS, Linux, Windows, 云端]
tags: [remotion, react, 数据动画, 模板视频, 动效, 渲染]
related: [kb/ffmpeg, kb/manim, kb/environment-local]
updated: 2026-11-03
owner: lib-scout
---

# Remotion · 用 React 代码渲染视频

## 一句话定位

用 React 组件描述每一帧，再由无头浏览器逐帧截图、编码成视频。服务 S7 字幕与图文、S9 动效与包装、S10 导出；尤其适合数据可视化动画、UI 演示视频、批量模板视频（一条数据 = 一个成片），不适合实拍素材剪辑。

## 能解决什么 / 不解决什么

| 能 | 不能 |
|---|---|
| 数据驱动动画：读 JSON / CSV，每行数据渲染一版 | 实拍素材的多轨剪辑与调色 |
| 复用前端能力：CSS / SVG / WebGL / 图表库 | 对时间线的帧精确外部编辑（渲染即固化） |
| 批量模板：换文案 / 换数据 / 换配色批量出片 | 高帧率长视频的低成本渲染 |

## 核心能力

- Composition：`<Composition id durationInFrames fps width height />` 声明式定义一条视频。
- 帧驱动动画：`useCurrentFrame()` + `interpolate()` / `spring()`，逐帧计算样式。
- 音视频素材：`<Video> <Audio> <Img>` 组件，可裁剪、变速、循环。
- 字幕与图文：直接用 React 排版中文/多语字幕，无需 ASS。
- CLI 渲染：`remotion render` 输出 mp4 / webm / 图片序列 / GIF，可并行渲染。

## 安装 / 获取

```bash
mkdir remotion-demo && cd remotion-demo
pnpm init
pnpm add remotion@4.0.540 @remotion/cli@4.0.540 react@19 react-dom@19
pnpm exec remotion --version      # 预期 4.0.540
```

前提：Node 18+（本机 Node 26.12.0 / pnpm 12.6.0 已满足）；首次渲染会下载 Chrome Headless Shell。也可用官方脚手架 `pnpm create video@latest` 生成完整模板（交互式）。

## 最小可用示例

```tsx
// src/Hello.tsx
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";

export const Hello = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{backgroundColor: "#111", justifyContent: "center", alignItems: "center"}}>
      <h1 style={{color: "white", opacity, fontSize: 96}}>Hello Video</h1>
    </AbsoluteFill>
  );
};
```

```tsx
// src/Root.tsx —— 注册 composition
import {Composition} from "remotion";
import {Hello} from "./Hello";

export const Root = () => (
  <Composition id="Hello" component={Hello} durationInFrames={90} fps={30} width={1920} height={1080} />
);
```

```tsx
// src/index.ts —— 入口
import {registerRoot} from "remotion";
import {Root} from "./Root";
registerRoot(Root);
```

```bash
# 渲染：3 秒 1080p30，H.264
pnpm exec remotion render Hello out/hello.mp4 --codec=h264
# 与系统 FFmpeg 衔接：响度标准化 + faststart 再交付
ffmpeg -i out/hello.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4
```

预期结果：`out/hello.mp4` 为 3 秒 1920×1080 视频，白字淡入；`final.mp4` 响度约 -14 LUFS。

## 优缺点与坑位

| 优点 | 坑位 |
|---|---|
| 前端技能直接复用，数据动画效率高 | 逐帧浏览器渲染，长视频耗时线性上升 |
| 代码即模板，天然适合批量与 CI | 需要下载 Chrome Headless Shell，离线环境易失败 |
| 排版能力远超 FFmpeg drawtext | 非 OSI 许可，公司规模决定是否付费 |

1. **首次渲染下载浏览器失败**。现象：`Failed to launch browser`、下载超时或内网 403。原因：Remotion 依赖 Chrome Headless Shell 逐帧截图，首次运行自动下载。规避：先在联网机器渲染一次缓存浏览器；或指定 `--browser-executable` 指向本机 Chrome/Chromium。
2. **渲染耗时随帧数线性增长**。现象：3 分钟 1080p30 视频渲染十几分钟起步。原因：每帧一次页面渲染与截图，帧数 = 时长 × fps。规避：降低 fps（如 30→24）、用 `--concurrency` 提高并行（默认按 CPU 核数）、长视频分段渲染后用 FFmpeg `concat` 拼接。
3. **许可不是开源许可**。现象：4 人以上公司直接商用存在合规风险。原因：Remotion License 规定个人、非营利与 ≤3 人公司免费，4 人及以上需购买 Company License。规避：商用前按团队人数确认，或改用 Blender VSE / `kb/ffmpeg` 方案。截至 2026-11-03。
4. **把 Remotion 当成剪辑器**。现象：想用 Remotion 对实拍素材做多轨剪辑、调色、音频修复，发现组件能力不够。原因：它是「按帧渲染页面」，不是 NLE。规避：实拍剪辑交给 NLE / FFmpeg，Remotion 只负责包装层（字幕、图表、片头尾），最后与正片合成。

## 适用 / 不适用

- 适用：数据可视化动画、UI / 产品演示、批量模板视频（换数据出片）、片头片尾与字幕包装、CI 自动出片。
- 不适用：实拍长视频剪辑与调色（用 NLE / `kb/ffmpeg`）；需要 ASS 字幕与广播级封装（用 `kb/ffmpeg` + libass）；三维动画（用 Blender）。

## 与本仓 SOP / 其他条目的关系

- 服务 SOP：数据动画类与宣传片类 SOP 的 S9 动效包装、S7 图文字幕；批量模板出片环节。
- 关联条目：`kb/ffmpeg`（响度 / 封装 / 拼接衔接）、[本机环境基线](../环境/environment-local.md)（Node / pnpm 版本）。

## 实测记录

| 日期 | 环境 | 命令 / 工程 | 结果 |
|---|---|---|---|
| 2026-11-03 | macOS 27.2 / M5 / Node 26.12.0 / pnpm 12.6.0 | 本仓队友以 Remotion 4.0.540 跑通渲染流程 | 渲染成功；本文作者未复跑，故整体标 `可用`（Node / pnpm 版本 [实测]） |

## 来源

1. [Remotion GitHub 仓库](https://github.com/remotion-dev/remotion)（访问 2026-11-03）：TypeScript；最新 release `v4.0.540`（2026-11-02）
2. [Remotion 官方文档](https://www.remotion.dev/docs/)（访问 2026-11-03）：Composition、useCurrentFrame、CLI
3. [Remotion 许可与定价](https://www.remotion.dev/docs/license)、[License FAQ](https://www.remotion.dev/docs/license/faq)（访问 2026-11-03）：个人 / ≤3 人公司免费，4 人及以上需 Company License
4. 本机实测：`node -v`、`pnpm -v`（2026-11-03）
