import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline-vertical.json";
import cues from "./cues-vertical.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = { bg: "#F4FBF8", ink: "#0B1F1A", muted: "#60756E", mint: "#00C48C", white: "#FFFFFF" };
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const fade = (f: number, d: number, dur = 8) => ({ opacity: interpolate(f, [d, d + dur], [0, 1], CAP), transform: "translateY(" + interpolate(f, [d, d + dur], [10, 0], CAP) + "px)" });

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 100, display: "flex", justifyContent: "center", padding: "0 40px" }}>
      <div style={{ opacity: o, padding: "11px 22px", borderRadius: 8, background: "rgba(7,24,19,0.88)", color: C.white, fontFamily: FONT, fontSize: 32, whiteSpace: "nowrap" }}>{c.text}</div>
    </div>
  );
};

const Header: React.FC = () => (
  <div style={{ position: "absolute", top: 46, left: 54, display: "flex", alignItems: "center", gap: 9 }}>
    <span style={{ width: 8, height: 8, borderRadius: 4, background: C.mint }} />
    <span style={{ color: C.ink, fontFamily: FONT, fontSize: 21, fontWeight: 800 }}>WorkBuddy</span>
    <span style={{ color: C.muted, fontFamily: FONT, fontSize: 19 }}>· 网站采集工程师</span>
  </div>
);

const VideoPanel: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  <div style={{ position: "absolute", left: 40, width: 1000, background: C.white, borderRadius: 14, overflow: "hidden", boxShadow: "0 20px 60px rgba(10,40,30,0.16)", ...style }}>
    <div style={{ height: 30, background: "#E7F3EE", display: "flex", alignItems: "center", gap: 6, padding: "0 12px" }}>
      {["#FF605C", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 7, height: 7, borderRadius: 4, background: x }} />)}
      <span style={{ marginLeft: 8, color: "#5C726B", fontFamily: MONO, fontSize: 11 }}>WorkBuddy · 真实录屏</span>
    </div>
    <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: 525, objectFit: "cover" }} />
  </div>
);

const S1: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <img src={staticFile("chinamoney.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center top" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(7,24,19,0.72) 0%, rgba(7,24,19,0.25) 45%, rgba(7,24,19,0.75) 100%)" }} />
      <Header />
      <div style={{ position: "absolute", left: 54, right: 54, top: 300 }}>
        <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 18, letterSpacing: 2 }}>09:15 · 每日更新</div>
        <div style={{ ...fade(f, 8), color: C.white, fontSize: 58, fontWeight: 800, lineHeight: 1.2, marginTop: 12 }}>汇率中间价<br />又更新了</div>
        <div style={{ ...fade(f, 18), color: "rgba(255,255,255,0.76)", fontSize: 30, marginTop: 16 }}>你还在手动复制吗？</div>
      </div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Header />
      <div style={{ ...fade(f, 2), position: "absolute", left: 54, top: 150, color: C.ink, fontSize: 42, fontWeight: 800 }}>把网址和字段<br />交给它</div>
      <VideoPanel src="clips/task.mp4" style={{ top: 560 }} />
      <div style={{ ...fade(f, 18), position: "absolute", left: 54, top: 1190, color: C.muted, fontSize: 24 }}>5 个货币对 · 日期/中间价/涨跌</div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Header />
      <div style={{ ...fade(f, 2), position: "absolute", left: 54, top: 150, color: C.ink, fontSize: 42, fontWeight: 800 }}>每天 9:30<br />自动出表</div>
      <VideoPanel src="clips/result.mp4" style={{ top: 560 }} />
      <div style={{ ...fade(f, 14), position: "absolute", left: 54, top: 1190, color: C.muted, fontSize: 24 }}>每天 9:30 · 去重 · 失败通报</div>
    </AbsoluteFill>
  );
};

const S4: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ink, padding: "80px 54px" }}>
      <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 16, letterSpacing: 2 }}>WORKBUDDY · 专家</div>
      <div style={{ ...fade(f, 8), color: C.white, fontSize: 52, fontWeight: 800, lineHeight: 1.2, marginTop: 14 }}>网站采集工程师</div>
      <div style={{ ...fade(f, 16), color: "rgba(255,255,255,0.72)", fontSize: 24, marginTop: 16 }}>把网址交给它，把数据还给你。</div>
      <div style={{ ...fade(f, 24), display: "inline-flex", marginTop: 26, background: C.mint, color: C.ink, borderRadius: 8, padding: "13px 20px", fontSize: 22, fontWeight: 800 }}>WorkBuddy 搜「网站采集工程师」</div>
      <div style={{ ...fade(f, 30), position: "absolute", left: 54, right: 54, bottom: 120, background: C.white, borderRadius: 14, padding: 12 }}>
        <img src={staticFile("qr.png")} alt="QR" style={{ width: "100%", borderRadius: 8, display: "block" }} />
        <div style={{ color: C.ink, textAlign: "center", fontSize: 17, fontWeight: 700, padding: "8px 0 2px" }}>微信扫码，查看详情</div>
      </div>
      <div style={{ ...fade(f, 38), position: "absolute", left: 54, right: 54, bottom: 64, color: "rgba(255,255,255,0.55)", fontSize: 17, textAlign: "center" }}>WorkBuddy · AI 搞定工作</div>
    </AbsoluteFill>
  );
};

export const VerticalPromo: React.FC = () => {
  const scenes = [
    { from: 0, to: sec(3.3), node: <S1 /> },
    { from: sec(3.3), to: sec(7.6), node: <S2 /> },
    { from: sec(7.6), to: sec(12.0), node: <S3 /> },
    { from: sec(12.0), to: T.frames, node: <S4 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {scenes.map((s, i) => <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>{s.node}</Sequence>)}
      <Caption />
      <Audio src={staticFile("voice-vertical.wav")} />
    </AbsoluteFill>
  );
};