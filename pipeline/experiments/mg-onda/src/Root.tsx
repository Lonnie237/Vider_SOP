import React from "react";
import { AbsoluteFill, Composition, Sequence, interpolate, useCurrentFrame } from "remotion";
import { BarChart } from "./onda/bar-chart/BarChart";
import { BlurReveal } from "./onda/blur-reveal/BlurReveal";
import { CountUp } from "./onda/count-up/CountUp";
import { LineChart } from "./onda/line-chart/LineChart";
import { Spotlight } from "./onda/spotlight/Spotlight";

const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",sans-serif';
const C = { bg: "#101418", text: "#F2EFE6", muted: "#A8A49A", amber: "#F0A93B" };

const Label: React.FC<{ kicker: string; title: string }> = ({ kicker, title }) => (
  <div style={{ position: "absolute", left: 84, top: 64 }}>
    <div style={{ color: C.amber, fontFamily: "monospace", fontSize: 16, letterSpacing: 2 }}>{kicker}</div>
    <div style={{ color: C.text, fontFamily: FONT, fontSize: 44, fontWeight: 800, marginTop: 8 }}>{title}</div>
  </div>
);

const Scene1: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <BlurReveal text="让 AI 做 MG" delay={2} duration={18} color={C.text} fontSize={92} fontFamily={FONT} placement={{ x: 0.5, y: 0.34, anchor: "center" }} />
      <CountUp from={0} to={15} delay={20} duration={30} suffix=" 种" color={C.amber} fontSize={80} fontFamily={FONT} placement={{ x: 0.5, y: 0.62, anchor: "center" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 120, textAlign: "center", color: C.muted, fontFamily: FONT, fontSize: 22, opacity: interpolate(f, [30, 45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>Onda 组件实验 · 1920×1080</div>
    </AbsoluteFill>
  );
};

const Scene2: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Label kicker="DATA" title="数字滚动 / 条形图" />
    <div style={{ position: "absolute", left: 260, top: 280, width: 1400 }}>
      <BarChart data={[
        { label: "静态卡片", value: 92 },
        { label: "数字滚动", value: 64 },
        { label: "线/点动效", value: 38 },
        { label: "章节卡", value: 76 },
      ]} max={100} delay={2} duration={26} stagger={5} barHeight={34} gap={16} accentColor={C.amber} barColor="#C9C4B8" trackColor="rgba(242,239,230,0.16)" color={C.text} fontFamily={FONT} labelWidth={220} fontSize={22} />
    </div>
  </AbsoluteFill>
);

const Scene3: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Label kicker="TREND" title="折线画出 / 点落下" />
    <LineChart data={[12, 18, 15, 24, 22, 31, 38, 44]} delay={2} duration={60} color={C.amber} strokeWidth={4} width={1100} height={420} fill showDots placement={{ x: 0.5, y: 0.55, anchor: "center" }} />
  </AbsoluteFill>
);

const Scene4: React.FC = () => (
  <AbsoluteFill style={{ background: "#08080A" }}>
    <Spotlight x={0.5} y={0.5} radius={46} delay={2} duration={28} color={C.amber} softness={70} />
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", color: "#1A1208", fontFamily: FONT, fontSize: 64, fontWeight: 800, zIndex: 2 }}>
      Spotlight · 焦点揭示
    </AbsoluteFill>
  </AbsoluteFill>
);

export const OndaTest: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Sequence from={0} durationInFrames={75}><Scene1 /></Sequence>
    <Sequence from={75} durationInFrames={75}><Scene2 /></Sequence>
    <Sequence from={150} durationInFrames={75}><Scene3 /></Sequence>
    <Sequence from={225} durationInFrames={75}><Scene4 /></Sequence>
  </AbsoluteFill>
);

export const Root: React.FC = () => (
  <Composition id="OndaTest" component={OndaTest} durationInFrames={300} fps={30} width={1920} height={1080} />
);