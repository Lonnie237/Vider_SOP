import React from "react";
import { AbsoluteFill, Audio, Composition, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline.json";
import cues from "./cues.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = { bg: "#F4FBF8", ink: "#0B1F1A", muted: "#60756E", mint: "#00C48C", white: "#FFFFFF", red: "#E5534B" };
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const fade = (f: number, d: number, dur = 8) => ({ opacity: interpolate(f, [d, d + dur], [0, 1], CAP), transform: "translateY(" + interpolate(f, [d, d + dur], [10, 0], CAP) + "px)" });
const cue = (s: string) => CUES.find((c) => c.text === s) || CUES[0];
const DATA = [
  ["美元/人民币", "6.7191", "24.00"],
  ["欧元/人民币", "7.4852", "219.00"],
  ["100日元/人民币", "4.2279", "76.00"],
  ["港元/人民币", "0.85643", "0.10"],
  ["英镑/人民币", "8.9500", "392.00"],
];

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 100, background: "linear-gradient(transparent, rgba(7,24,19,0.88))" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 22, display: "flex", justifyContent: "center" }}>
        <div style={{ opacity: o, padding: "10px 24px", borderRadius: 8, background: "rgba(7,24,19,0.92)", color: C.white, fontFamily: FONT, fontSize: 32, whiteSpace: "nowrap" }}>{c.text}</div>
      </div>
    </>
  );
};

const Header: React.FC = () => (
  <div style={{ position: "absolute", top: 42, left: 76, display: "flex", alignItems: "center", gap: 9 }}>
    <span style={{ width: 8, height: 8, borderRadius: 4, background: C.mint }} />
    <span style={{ color: C.ink, fontFamily: FONT, fontSize: 20, fontWeight: 800 }}>WorkBuddy</span>
    <span style={{ color: C.muted, fontFamily: FONT, fontSize: 19 }}>· 网站采集工程师</span>
  </div>
);

const Badge: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 42, right: 76, background: "rgba(7,24,19,0.84)", color: C.white, borderRadius: 6, padding: "7px 12px", fontFamily: MONO, fontSize: 13, letterSpacing: 1 }}>{children}</div>
);

const Overlay: React.FC<{ title: string; sub?: string; at: number }> = ({ title, sub, at }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [at, at + 8], [0, 1], CAP);
  const y = interpolate(f, [at, at + 8], [12, 0], CAP);
  return (
    <div style={{ position: "absolute", left: 76, bottom: 120, opacity: o, transform: "translateY(" + y + "px)", background: "rgba(255,255,255,0.94)", borderLeft: "4px solid " + C.mint, borderRadius: 8, padding: "12px 18px", boxShadow: "0 10px 30px rgba(10,40,30,0.12)" }}>
      <div style={{ color: C.ink, fontFamily: FONT, fontSize: 25, fontWeight: 800 }}>{title}</div>
      {sub ? <div style={{ color: C.muted, fontFamily: FONT, fontSize: 16, marginTop: 4 }}>{sub}</div> : null}
    </div>
  );
};

const PageShot: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: "hidden" }}>
      <img src={staticFile("chinamoney.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 20%", transform: "scale(" + interpolate(f, [0, 150], [1.02, 1.1], CAP) + ")" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg, rgba(244,251,248,0.96) 0%, rgba(244,251,248,0.72) 38%, rgba(244,251,248,0.1) 70%)" }} />
      {children}
    </AbsoluteFill>
  );
};

const DataTable: React.FC<{ title: string; sub: string; checks?: boolean }> = ({ title, sub, checks }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg, padding: "100px 80px 0", fontFamily: FONT }}>
      <Header />
      <div style={{ ...fade(f, 2), color: C.ink, fontSize: 48, fontWeight: 800 }}>{title}</div>
      <div style={{ ...fade(f, 10), color: C.muted, fontSize: 21, marginTop: 10 }}>{sub}</div>
      <div style={{ ...fade(f, 16), marginTop: 28, background: C.white, borderRadius: 14, padding: 26, boxShadow: "0 16px 44px rgba(10,40,30,0.12)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr 0.8fr", gap: 0 }}>
          {["货币对", "中间价", "涨跌"].map((x) => <div key={x} style={{ color: C.muted, fontSize: 17, padding: "8px 8px", borderBottom: "1px solid #E6F0EC" }}>{x}</div>)}
          {DATA.flatMap((r, i) => r.map((x, j) => (
            <div key={String(i) + j} style={{ color: j === 2 ? C.mint : C.ink, fontSize: 24, padding: "14px 8px", borderBottom: "1px solid #E6F0EC", fontFamily: j === 0 ? FONT : MONO }}>{x}</div>
          )))}
        </div>
        <div style={{ marginTop: 16, color: C.muted, fontSize: 15 }}>示例数据 · 2026-11-11 · 以官网为准</div>
      </div>
      {checks ? (
        <div style={{ ...fade(f, 24), marginTop: 22, display: "flex", gap: 18 }}>
          {["5/5 逐条对照", "日期+货币对去重", "失败会通报"].map((x) => <div key={x} style={{ background: C.white, borderRadius: 8, padding: "10px 16px", color: C.ink, fontSize: 18, fontWeight: 700, boxShadow: "0 8px 24px rgba(10,40,30,0.08)" }}>✓ {x}</div>)}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const ScheduleCard: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg, padding: "100px 80px 0", fontFamily: FONT }}>
      <Header />
      <div style={{ ...fade(f, 2), color: C.ink, fontSize: 48, fontWeight: 800 }}>每天 9:30<br />自动运行</div>
      <div style={{ ...fade(f, 14), marginTop: 34, background: C.white, borderRadius: 14, padding: 26, boxShadow: "0 16px 44px rgba(10,40,30,0.12)", maxWidth: 1100 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ color: C.ink, fontSize: 28, fontWeight: 800 }}>中国货币网人民币中间价每日采集</div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: C.mint, fontSize: 18, fontWeight: 700 }}><span style={{ width: 18, height: 18, borderRadius: 9, background: C.mint }} />已启用</div>
        </div>
        <div style={{ marginTop: 22, display: "flex", gap: 36, color: C.muted, fontSize: 22 }}>
          <span>重复：每天</span><span>时间：09:30</span><span>有效期：长期</span>
        </div>
        <div style={{ marginTop: 22, color: C.ink, fontSize: 20, lineHeight: 1.6 }}>只采公开数据；按日期 + 货币对增量去重；<br />失败时通知，不静默出空文件。</div>
      </div>
    </AbsoluteFill>
  );
};

const CTA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ink, color: C.white, fontFamily: FONT, padding: "70px 80px" }}>
      <div style={{ display: "flex", gap: 36, alignItems: "center", height: "100%" }}>
        <div style={{ flex: 1 }}>
          <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 16, letterSpacing: 2 }}>WORKBUDDY · 专家</div>
          <div style={{ ...fade(f, 8), fontSize: 52, fontWeight: 800, lineHeight: 1.2, marginTop: 14 }}>网站采集工程师</div>
          <div style={{ ...fade(f, 16), color: "rgba(255,255,255,0.72)", fontSize: 25, marginTop: 18 }}>把网址交给它，把数据还给你。</div>
          <div style={{ ...fade(f, 24), display: "inline-flex", marginTop: 26, background: C.mint, color: C.ink, borderRadius: 8, padding: "14px 22px", fontSize: 23, fontWeight: 800 }}>WorkBuddy 搜「网站采集工程师」</div>
          <div style={{ ...fade(f, 30), color: "rgba(255,255,255,0.55)", fontSize: 17, marginTop: 20 }}>微信扫码 · 查看详情</div>
        </div>
        <div style={{ width: 330, background: C.white, borderRadius: 14, padding: 12 }}>
          <img src={staticFile("qr.png")} alt="QR" style={{ width: "100%", borderRadius: 8, display: "block" }} />
          <div style={{ color: C.ink, textAlign: "center", fontSize: 16, padding: "8px 0 2px", fontWeight: 700 }}>微信扫码，查看详情</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const TaskClip: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <OffthreadVideo src={staticFile("clips/task.mp4")} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <Overlay title="把网址和字段交给它" sub="5 个货币对 · 日期/中间价/涨跌" at={0} />
    <Badge>真实录屏</Badge>
  </AbsoluteFill>
);

const ProcessClip: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <OffthreadVideo src={staticFile("clips/process.mp4")} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    <Overlay title="自动定位数据接口" sub="按日期去重 · 失败通报" at={0} />
    <Badge>真实录屏 · 加速 4×</Badge>
  </AbsoluteFill>
);

export const CleanPromo: React.FC = () => (
  <AbsoluteFill style={{ background: C.bg }}>
    <Sequence from={0} durationInFrames={150}><PageShot><Header /><div style={{ position: "absolute", left: 76, top: 150, maxWidth: 760 }}><div style={{ color: C.mint, fontFamily: MONO, fontSize: 17, letterSpacing: 2 }}>09:15 · 每日更新</div><div style={{ color: C.ink, fontSize: 54, fontWeight: 800, lineHeight: 1.18, marginTop: 12 }}>汇率中间价<br />又更新了</div><div style={{ color: C.muted, fontSize: 28, marginTop: 14 }}>你还在手动复制吗？</div></div></PageShot></Sequence>
    <Sequence from={150} durationInFrames={242}><TaskClip /></Sequence>
    <Sequence from={392} durationInFrames={152}><ProcessClip /></Sequence>
    <Sequence from={544} durationInFrames={216}><DataTable title="每天 9:30 自动出表" sub="增量去重 · 失败通报" /></Sequence>
    <Sequence from={760} durationInFrames={188}><DataTable title="交付前和官网逐条对照" sub="结果可验证" checks /></Sequence>
    <Sequence from={948} durationInFrames={122}><ScheduleCard /></Sequence>
    <Sequence from={1070} durationInFrames={150}><CTA /></Sequence>
    <Caption />
    <Audio src={staticFile("voice.wav")} />
  </AbsoluteFill>
);

export const CleanRoot: React.FC = () => (
  <Composition id="CollectorPromoClean" component={CleanPromo} durationInFrames={1220} fps={30} width={1920} height={1080} />
);
