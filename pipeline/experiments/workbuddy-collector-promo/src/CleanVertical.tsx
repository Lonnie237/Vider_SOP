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
const DATA = [["美元/人民币", "6.7191", "24.00"], ["欧元/人民币", "7.4852", "219.00"], ["100日元/人民币", "4.2279", "76.00"], ["港元/人民币", "0.85643", "0.10"], ["英镑/人民币", "8.9500", "392.00"]];

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <div style={{ position: "absolute", left: 30, right: 30, bottom: 48, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "10px 20px", borderRadius: 8, background: "rgba(7,24,19,0.90)", color: C.white, fontFamily: FONT, fontSize: 31, whiteSpace: "nowrap" }}>{c.text}</div>
    </div>
  );
};

const Header: React.FC = () => (
  <div style={{ position: "absolute", top: 46, left: 50, display: "flex", alignItems: "center", gap: 9 }}>
    <span style={{ width: 8, height: 8, borderRadius: 4, background: C.mint }} />
    <span style={{ color: C.ink, fontFamily: FONT, fontSize: 21, fontWeight: 800 }}>WorkBuddy</span>
    <span style={{ color: C.muted, fontFamily: FONT, fontSize: 19 }}>· 网站采集工程师</span>
  </div>
);

const Page: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: "hidden" }}>
      <img src={staticFile("chinamoney.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center top", transform: "scale(" + interpolate(f, [0, 100], [1.02, 1.08], CAP) + ")" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(7,24,19,0.82) 0%, rgba(7,24,19,0.15) 46%, rgba(7,24,19,0.9) 100%)" }} />
      <Header />
      <div style={{ position: "absolute", left: 50, right: 50, top: 300 }}>
        <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 17, letterSpacing: 2 }}>09:15 · 每日更新</div>
        <div style={{ ...fade(f, 7), color: C.white, fontSize: 64, fontWeight: 800, lineHeight: 1.18, marginTop: 12 }}>汇率中间价<br />又更新了</div>
        <div style={{ ...fade(f, 16), color: "rgba(255,255,255,0.76)", fontSize: 31, marginTop: 16 }}>你还在手动复制吗？</div>
      </div>
    </AbsoluteFill>
  );
};

const Task: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Header />
    <div style={{ position: "absolute", left: 50, top: 150, color: C.ink, fontSize: 46, fontWeight: 800 }}>把网址和字段<br />交给它</div>
    <div style={{ position: "absolute", left: 40, top: 380, width: 1000, borderRadius: 14, overflow: "hidden", background: C.white, boxShadow: "0 18px 50px rgba(10,40,30,0.16)" }}>
      <OffthreadVideo src={staticFile("clips/task-prompt.mp4")} muted style={{ width: "100%", height: 562, objectFit: "cover" }} />
    </div>
    <div style={{ position: "absolute", left: 50, top: 1010, color: C.muted, fontSize: 24 }}>5 个货币对 · 日期/中间价/涨跌</div>
    <div style={{ position: "absolute", left: 50, right: 50, top: 1100, display: "flex", gap: 12 }}>
      {["5 个货币对", "每天 09:30", "失败通报"].map((x) => <div key={x} style={{ flex: 1, background: C.white, borderRadius: 10, padding: "18px 12px", textAlign: "center", color: C.ink, fontSize: 20, fontWeight: 700, boxShadow: "0 8px 24px rgba(10,40,30,0.08)" }}>{x}</div>)}
    </div>
  </AbsoluteFill>
);

const Table: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg, padding: "150px 50px 0" }}>
    <Header />
    <div style={{ color: C.ink, fontSize: 46, fontWeight: 800, lineHeight: 1.2 }}>每天 9:30<br />自动出表</div>
    <div style={{ marginTop: 28, background: C.white, borderRadius: 14, padding: 22, boxShadow: "0 16px 44px rgba(10,40,30,0.12)" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 0.8fr" }}>
        {["货币对", "中间价", "涨跌"].map((x) => <div key={x} style={{ color: C.muted, fontSize: 17, padding: "8px 6px", borderBottom: "1px solid #E6F0EC" }}>{x}</div>)}
        {DATA.flatMap((r, i) => r.map((x, j) => <div key={String(i) + j} style={{ color: j === 2 ? C.mint : C.ink, fontSize: 24, padding: "14px 6px", borderBottom: "1px solid #E6F0EC", fontFamily: j === 0 ? FONT : MONO }}>{x}</div>))}
      </div>
      <div style={{ marginTop: 14, color: C.muted, fontSize: 15 }}>示例数据 · 2026-11-11 · 以官网为准</div>
    </div>
    <div style={{ marginTop: 22, color: C.muted, fontSize: 22 }}>增量去重 · 失败通报 · 官网逐条对照</div>
  </AbsoluteFill>
);

const Schedule: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg, padding: "150px 50px 0" }}>
    <Header />
    <div style={{ color: C.ink, fontSize: 46, fontWeight: 800, lineHeight: 1.2 }}>每天 9:30<br />自动运行</div>
    <div style={{ marginTop: 32, background: C.white, borderRadius: 14, padding: 26, boxShadow: "0 16px 44px rgba(10,40,30,0.12)" }}>
      <div style={{ color: C.ink, fontSize: 26, fontWeight: 800, lineHeight: 1.35 }}>中国货币网人民币<br />中间价每日采集</div>
      <div style={{ marginTop: 16, display: "flex", gap: 22, color: C.muted, fontSize: 20, flexWrap: "wrap" }}><span>每天</span><span>09:30</span><span>长期有效</span></div>
      <div style={{ marginTop: 18, color: C.ink, fontSize: 20, lineHeight: 1.6 }}>按日期 + 货币对去重<br />失败时通知，不静默出空文件</div>
    </div>
  </AbsoluteFill>
);

const CTA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ink, padding: "80px 54px", color: C.white }}>
      <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 16, letterSpacing: 2 }}>WORKBUDDY · 专家</div>
      <div style={{ ...fade(f, 7), fontSize: 52, fontWeight: 800, lineHeight: 1.2, marginTop: 14 }}>网站采集工程师</div>
      <div style={{ ...fade(f, 14), color: "rgba(255,255,255,0.72)", fontSize: 24, marginTop: 16 }}>把网址交给它，把数据还给你。</div>
      <div style={{ ...fade(f, 22), display: "inline-flex", marginTop: 24, background: C.mint, color: C.ink, borderRadius: 8, padding: "13px 20px", fontSize: 22, fontWeight: 800 }}>WorkBuddy 搜「网站采集工程师」</div>
      <div style={{ ...fade(f, 28), position: "absolute", left: 54, right: 54, bottom: 110, background: C.white, borderRadius: 14, padding: 12 }}>
        <img src={staticFile("qr.png")} style={{ width: "100%", borderRadius: 8, display: "block" }} />
        <div style={{ color: C.ink, textAlign: "center", fontSize: 17, fontWeight: 700, padding: "8px 0 2px" }}>微信扫码，查看详情</div>
      </div>
    </AbsoluteFill>
  );
};

export const CleanVertical: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Sequence from={0} durationInFrames={99}><Page /></Sequence>
    <Sequence from={99} durationInFrames={132}><Task /></Sequence>
    <Sequence from={231} durationInFrames={126}><Table /></Sequence>
    <Sequence from={357} durationInFrames={60}><Schedule /></Sequence>
    <Sequence from={417} durationInFrames={70}><CTA /></Sequence>
    <Caption />
    <Audio src={staticFile("voice-vertical.wav")} />
  </AbsoluteFill>
);