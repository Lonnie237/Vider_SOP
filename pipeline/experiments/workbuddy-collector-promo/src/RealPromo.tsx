import React from "react";
import { AbsoluteFill, Audio, Composition, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline.json";
import cues from "./cues.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = { bg: "#F4FBF8", ink: "#0B1F1A", muted: "#60756E", mint: "#00C48C", white: "#FFFFFF", amber: "#F0A93B" };
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const fade = (f: number, d: number, dur = 10) => ({ opacity: interpolate(f, [d, d + dur], [0, 1], CAP), transform: "translateY(" + interpolate(f, [d, d + dur], [12, 0], CAP) + "px)" });

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 100, background: "linear-gradient(transparent, rgba(7,24,19,0.86))" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 22, display: "flex", justifyContent: "center" }}>
        <div style={{ opacity: o, padding: "10px 24px", borderRadius: 8, background: "rgba(7,24,19,0.90)", color: C.white, fontFamily: FONT, fontSize: 32, whiteSpace: "nowrap" }}>{c.text}</div>
      </div>
    </>
  );
};

const Badge: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 44, left: 76, display: "flex", alignItems: "center", gap: 9, background: "rgba(7,24,19,0.82)", color: C.white, borderRadius: 6, padding: "8px 13px", fontFamily: MONO, fontSize: 14, letterSpacing: 1 }}>{children}</div>
);

const Overlay: React.FC<{ title: string; sub?: string; at: number; style?: React.CSSProperties }> = ({ title, sub, at, style }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [at, at + 8], [0, 1], CAP);
  const y = interpolate(f, [at, at + 8], [12, 0], CAP);
  return (
    <div style={{ position: "absolute", left: 76, bottom: 120, opacity: o, transform: "translateY(" + y + "px)", background: "rgba(255,255,255,0.92)", borderLeft: "4px solid " + C.mint, borderRadius: 8, padding: "12px 18px", boxShadow: "0 10px 30px rgba(10,40,30,0.12)", ...style }}>
      <div style={{ color: C.ink, fontFamily: FONT, fontSize: 25, fontWeight: 800 }}>{title}</div>
      {sub ? <div style={{ color: C.muted, fontFamily: FONT, fontSize: 16, marginTop: 4 }}>{sub}</div> : null}
    </div>
  );
};

const Shot: React.FC<{ src: string; from: number; dur: number; children?: React.ReactNode }> = ({ src, from, dur, children }) => (
  <Sequence from={from} durationInFrames={dur}>
    <AbsoluteFill style={{ background: C.bg }}>
      <OffthreadVideo src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      {children}
    </AbsoluteFill>
  </Sequence>
);

const PageShot: React.FC<{ src: string; from: number; dur: number; children?: React.ReactNode; position?: string }> = ({ src, from, dur, children, position }) => (
  <Sequence from={from} durationInFrames={dur}>
    <AbsoluteFill style={{ background: C.bg }}>
      <img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: position || "center" }} />
      {children}
    </AbsoluteFill>
  </Sequence>
);

const CTA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ink, color: C.white, fontFamily: FONT, padding: "70px 80px" }}>
      <div style={{ display: "flex", gap: 36, alignItems: "center", height: "100%" }}>
        <div style={{ flex: 1 }}>
          <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 16, letterSpacing: 2 }}>WORKBUDDY · 专家</div>
          <div style={{ ...fade(f, 8), fontSize: 54, fontWeight: 800, lineHeight: 1.2, marginTop: 14 }}>网站采集工程师</div>
          <div style={{ ...fade(f, 16), color: "rgba(255,255,255,0.72)", fontSize: 25, marginTop: 18 }}>把网址交给它，把数据还给你。</div>
          <div style={{ ...fade(f, 24), display: "inline-flex", marginTop: 26, background: C.mint, color: C.ink, borderRadius: 8, padding: "14px 22px", fontSize: 23, fontWeight: 800 }}>WorkBuddy 搜「网站采集工程师」</div>
          <div style={{ ...fade(f, 30), color: "rgba(255,255,255,0.55)", fontSize: 17, marginTop: 20 }}>微信扫码 · 查看详情</div>
        </div>
        <div style={{ width: 300, background: C.white, borderRadius: 14, padding: 12 }}>
          <img src={staticFile("qr.png")} alt="QR" style={{ width: "100%", borderRadius: 8, display: "block" }} />
          <div style={{ color: C.ink, textAlign: "center", fontSize: 16, padding: "8px 0 2px", fontWeight: 700 }}>微信扫码，查看详情</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const RealPromo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <PageShot src="chinamoney.png" from={0} dur={150} position="center 20%">
        <Badge>09:15 · 人民币汇率中间价</Badge>
        <div style={{ position: "absolute", left: 76, top: 130, background: "rgba(255,255,255,0.94)", borderRadius: 10, padding: "20px 26px", boxShadow: "0 16px 46px rgba(10,40,30,0.14)" }}>
          <div style={{ color: C.ink, fontFamily: FONT, fontSize: 38, fontWeight: 800 }}>每天早上 9:15<br />中间价又更新了</div>
          <div style={{ color: C.muted, fontFamily: FONT, fontSize: 22, marginTop: 10 }}>你还在手动复制吗？</div>
        </div>
      </PageShot>
      <Shot src="clips/task.mp4" from={150} dur={242}>
        <Overlay title="把网址和字段交给它" sub="5 个货币对 · 日期/中间价/涨跌" at={0} />
      </Shot>
      <Shot src="clips/process.mp4" from={392} dur={152}>
        <Overlay title="自动定位数据接口" sub="按日期去重 · 失败通报" at={0} />
        <Badge>真实录屏 · 加速 4×</Badge>
      </Shot>
      <Shot src="clips/result.mp4" from={544} dur={216}>
        <Overlay title="每天 9:30 自动出表" sub="示例数据 · 2026-11-11" at={0} />
        <Badge>真实录屏</Badge>
      </Shot>
      <Shot src="clips/verify.mp4" from={760} dur={188}>
        <Overlay title="交付前和官网逐条对照" sub="结果可验证" at={0} />
        <Badge>真实录屏</Badge>
      </Shot>
      <Shot src="clips/schedule.mp4" from={948} dur={122}>
        <Overlay title="每天 9:30 · 去重 · 失败通报" sub="定时任务" at={0} />
        <Badge>真实录屏</Badge>
      </Shot>
      <Sequence from={1070} durationInFrames={150}><CTA /></Sequence>
      <Caption />
      <Audio src={staticFile("voice.wav")} />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="CollectorPromoReal" component={RealPromo} durationInFrames={T.frames} fps={T.fps} width={T.width} height={T.height} />
);