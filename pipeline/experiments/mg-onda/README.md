# Onda 组件实验（2026-11-11）

- 目的：验证 Onda（ondajs）能否作为当前 Remotion 产线的 MG 组件层
- 环境：macOS / Node 26 / Remotion 4.0.540 / React 19.2 / TypeScript
- 测试：10 秒 1920×1080，4 段：标题+数字、条形图、折线图、Spotlight
- 成片（本地）：pipeline/runs/experiments/mg-onda-test.mp4
- 结论：**可用，但只接 3–4 个组件，不整套引入；BarChart 需要固定宽度父容器。**

## 1. 安装

    npx --yes ondajs@0.9.2 add count-up bar-chart line-chart spotlight blur-reveal --components-out ./src/onda

- Onda 0.9.2，MIT；组件以源码写入 src/onda，不是黑盒依赖；
- peer 依赖：react 19 / remotion 4 / zod；
- 当前项目已有 remotion/react，zod 由 Onda 生成代码使用；不需要额外运行时。

## 2. 实测结果

| 组件 | 结果 | 坑 |
|---|---|---|
| CountUp | 通过 | 默认字体 Clash Display 未安装，必须传 fontFamily；placement 不传会和标题重叠 |
| BlurReveal | 通过 | 默认字体同样要覆盖 |
| LineChart | 通过 | 确定性 SVG pathLength；开箱即用，最适合数学/趋势 |
| Spotlight | 通过 | 是覆盖层；文字在下面会被冲淡，必须把文字放上层或改用深色字 |
| BarChart | 通过（修正后） | **父容器必须有明确宽度**，否则 80% 宽度塌成 0，只剩标签；包一层 1400px 容器后正常 |

## 3. 渲染

    CHROME="$HOME/Library/Caches/ms-playwright/chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    npx remotion render src/index.ts OndaTest out/onda-test.mp4 --browser-executable="$CHROME"

- 300 帧 / 10s / 1920×1080 / H.264；
- 无音频（纯组件测试）。

## 4. 建议

- 接入：CountUp、LineChart、BlurReveal、Spotlight（做焦点揭示）；
- 有条件接入：BarChart（必须固定宽度容器）；
- 不整套引入：70 个组件会带进过多风格和依赖；
- 下一步：把 CountUp 用于数学 S2 的 200/150，把 LineChart 用于数据页；把 Spotlight 用在 S3「0 是分界」。

## 5. 许可证

- Onda 组件为 MIT；复制进项目后按 MIT 保留版权与许可声明。
- 本实验不提交 src/onda（可重跑命令生成），只提交组合与记录。
