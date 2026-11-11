import React from "react";
import { AbsoluteFill, Audio, Composition, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline.json";
import cues from "./cues.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = { bg: "#F4FBF8", ink: "#0B1F1A", muted: "#60756E", mint: "#00C48C", mintSoft: "#D8F7EC", red: "#E5534B", amber: "#F0A93B", white: "#FFFFFF" };
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const fade = (f: number, d: number, dur = 10) => ({ opacity: interpolate(f, [d, d + dur], [0, 1], CAP), transform: "translateY(" + interpolate(f, [d, d + dur], [14, 0], CAP) + "px)" });
const cue = (s: string) => CUES.find((c) => c.text === s) || CUES[0];

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 44, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "12px 26px", borderRadius: 8, background: "rgba(7,24,19,0.84)", color: C.white, fontFamily: FONT, fontSize: 33, whiteSpace: "nowrap" }}>{c.text}</div>
    </div>
  );
};

const Browser: React.FC<{ src: string; alt: string; style?: React.CSSProperties; crop?: string }> = ({ src, alt, style, crop }) => (
  <div style={{ background: C.white, borderRadius: 14, boxShadow: "0 18px 60px rgba(10,40,30,0.14)", overflow: "hidden", ...style }}>
    <div style={{ height: 34, background: "#E7F3EE", display: "flex", alignItems: "center", gap: 7, padding: "0 14px" }}>
      {["#FF605C", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 8, height: 8, borderRadius: 4, background: x }} />)}
      <span style={{ marginLeft: 10, color: "#5C726B", fontFamily: MONO, fontSize: 12 }}>{alt}</span>
    </div>
    <img src={staticFile(src)} alt={alt} style={{ width: "100%", height: "calc(100% - 34px)", objectFit: "cover", objectPosition: crop || "center top", display: "block" }} />
  </div>
);

const Header: React.FC = () => (
  <div style={{ position: "absolute", top: 42, left: 76, display: "flex", alignItems: "center", gap: 10 }}>
    <span style={{ width: 8, height: 8, borderRadius: 4, background: C.mint }} />
    <span style={{ color: C.ink, fontFamily: FONT, fontSize: 20, fontWeight: 700 }}>WorkBuddy</span>
    <span style={{ color: C.muted, fontFamily: FONT, fontSize: 20 }}>· 网站采集工程师</span>
  </div>
);

const S1: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg, padding: "120px 90px 0" }}>
      <Header />
      <div style={{ display: "flex", gap: 54, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 18, letterSpacing: 2 }}>09:15 · 每日更新</div>
          <div style={{ ...fade(f, 6), color: C.ink, fontSize: 58, fontWeight: 800, lineHeight: 1.18, marginTop: 16 }}>人民币汇率中间价<br />又更新了</div>
          <div style={{ ...fade(f, 18), color: C.muted, fontSize: 32, marginTop: 22 }}>你还在手动复制吗？</div>
        </div>
        <div style={{ width: 760, height: 520, background: C.white, borderRadius: 18, boxShadow: "0 22px 70px rgba(10,40,30,0.13)", padding: 26 }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: C.muted, fontFamily: MONO, fontSize: 13 }}><span>汇率中间价.xlsx</span><span>09:15</span></div>
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 0.9fr", gap: 0, marginTop: 20 }}>
            {["货币对", "中间价", "涨跌", "美元/人民币", "6.7191", "24.00", "欧元/人民币", "7.4852", "219.00", "100日元/人民币", "4.2279", "76.00", "港元/人民币", "0.85643", "0.10", "英镑/人民币", "8.9500", "392.00"].map((x, i) => (
              <div key={i} style={{ padding: "14px 8px", borderBottom: "1px solid #E6F0EC", color: i < 3 ? C.muted : C.ink, fontSize: 20, fontWeight: i < 3 ? 600 : 500, fontFamily: i % 3 === 0 ? FONT : MONO }}>{x}</div>
            ))}
          </div>
          <div style={{ marginTop: 24, color: C.muted, fontSize: 16 }}>示例数据 · 2026-11-11</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg, padding: "110px 70px 0" }}>
      <Header />
      <div style={{ display: "flex", gap: 30, alignItems: "flex-start" }}>
        <div style={{ width: 520 }}>
          <div style={{ ...fade(f, 2), color: C.ink, fontSize: 48, fontWeight: 800, lineHeight: 1.2 }}>五个货币对<br />复制、粘贴、对格式</div>
          <div style={{ ...fade(f, 14), marginTop: 26, color: C.red, fontSize: 27, fontWeight: 700 }}>漏一天，表就断了。</div>
          <div style={{ ...fade(f, 22), marginTop: 30, color: C.muted, fontSize: 22 }}>网页改版、字段变化，还要重新对一遍。</div>
        </div>
        <Browser src="chinamoney.png" alt="chinamoney.com.cn · 人民币汇率中间价" style={{ width: 1250, height: 760 }} crop="center 30%" />
      </div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg, padding: "100px 76px 0" }}>
      <Header />
      <div style={{ display: "flex", gap: 34, alignItems: "flex-start" }}>
        <Browser src="expert-page.png" alt="WorkBuddy · 网站采集工程师" style={{ width: 570, height: 720 }} crop="center top" />
        <div style={{ flex: 1, paddingTop: 24 }}>
          <div style={{ ...fade(f, 2), color: C.ink, fontSize: 48, fontWeight: 800, lineHeight: 1.2 }}>把网址和字段<br />交给它</div>
          {[
            ["01", "给网址", "公开页面 / 数据页"],
            ["02", "选字段", "日期、货币对、中间价、涨跌"],
            ["03", "设时间", "每天 9:30，按日期去重"],
          ].map(([n, t, s], i) => (
            <div key={n} style={{ ...fade(f, 14 + i * 12), display: "flex", gap: 18, alignItems: "center", marginTop: 26, background: C.white, borderRadius: 12, padding: "18px 22px", boxShadow: "0 10px 30px rgba(10,40,30,0.08)" }}>
              <span style={{ color: C.mint, fontFamily: MONO, fontSize: 20 }}>{n}</span>
              <div><div style={{ color: C.ink, fontSize: 26, fontWeight: 700 }}>{t}</div><div style={{ color: C.muted, fontSize: 18, marginTop: 4 }}>{s}</div></div>
            </div>
          ))}
          <div style={{ ...fade(f, 50), marginTop: 18, color: C.muted, fontSize: 16 }}>流程示意 · 此段将替换为真实录屏</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const S4: React.FC = () => {
  const f = useCurrentFrame();
  const rows = [["美元/人民币", "6.7191", "24.00"], ["欧元/人民币", "7.4852", "219.00"], ["100日元/人民币", "4.2279", "76.00"], ["港元/人民币", "0.85643", "0.10"], ["英镑/人民币", "8.9500", "392.00"]];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg, padding: "110px 76px 0" }}>
      <Header />
      <div style={{ display: "flex", gap: 40, alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ ...fade(f, 2), color: C.ink, fontSize: 46, fontWeight: 800, lineHeight: 1.2 }}>每天 9:30<br />自动出表</div>
          <div style={{ ...fade(f, 12), marginTop: 18, color: C.muted, fontSize: 21 }}>增量去重 · 失败通报 · 交付前逐条对照</div>
          <div style={{ ...fade(f, 20), marginTop: 26, background: C.white, borderRadius: 14, padding: 24, boxShadow: "0 14px 40px rgba(10,40,30,0.10)" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr 0.8fr", gap: 0 }}>
              {["货币对", "中间价", "涨跌"].map((x) => <div key={x} style={{ color: C.muted, fontSize: 16, padding: "8px 6px", borderBottom: "1px solid #E6F0EC" }}>{x}</div>)}
              {rows.flatMap((r, i) => r.map((x, j) => <div key={String(i) + j} style={{ color: j === 2 ? C.mint : C.ink, fontSize: 20, padding: "12px 6px", borderBottom: "1px solid #E6F0EC", fontFamily: j === 0 ? FONT : MONO }}>{x}</div>))}
            </div>
            <div style={{ marginTop: 16, color: C.muted, fontSize: 15 }}>示例数据 · 2026-11-11 / 以官网为准</div>
          </div>
        </div>
        <Browser src="chinamoney.png" alt="官网逐条对照" style={{ width: 780, height: 700 }} crop="center 38%" />
      </div>
    </AbsoluteFill>
  );
};

const S5: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.bg, padding: "140px 90px 0" }}>
      <Header />
      <div style={{ ...fade(f, 2), color: C.ink, fontSize: 48, fontWeight: 800 }}>不只是汇率</div>
      <div style={{ display: "flex", gap: 18, marginTop: 36 }}>
        {["汇率中间价", "行情数据", "竞品价格", "每日资讯"].map((x, i) => (
          <div key={x} style={{ ...fade(f, 10 + i * 6), flex: 1, background: i === 0 ? C.ink : C.white, color: i === 0 ? C.white : C.ink, borderRadius: 12, padding: "34px 22px", textAlign: "center", fontSize: 28, fontWeight: 700, boxShadow: "0 12px 34px rgba(10,40,30,0.08)" }}>{x}</div>
        ))}
      </div>
      <div style={{ ...fade(f, 36), marginTop: 28, color: C.muted, fontSize: 24 }}>都能变成一张自动更新的表。</div>
    </AbsoluteFill>
  );
};

const S6: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, background: C.ink, padding: "100px 80px 0", color: C.white }}>
      <div style={{ display: "flex", gap: 40, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <div style={{ ...fade(f, 2), color: C.mint, fontFamily: MONO, fontSize: 17, letterSpacing: 2 }}>WORKBUDDY · 专家</div>
          <div style={{ ...fade(f, 8), fontSize: 54, fontWeight: 800, lineHeight: 1.2, marginTop: 16 }}>网站采集工程师</div>
          <div style={{ ...fade(f, 18), color: "rgba(255,255,255,0.72)", fontSize: 26, marginTop: 20 }}>把网址交给它，把数据还给你。</div>
          <div style={{ ...fade(f, 26), display: "inline-flex", marginTop: 32, background: C.mint, color: C.ink, borderRadius: 8, padding: "16px 24px", fontSize: 24, fontWeight: 800 }}>WorkBuddy 搜「网站采集工程师」</div>
          <div style={{ ...fade(f, 34), color: "rgba(255,255,255,0.55)", fontSize: 18, marginTop: 22 }}>微信扫码 · 打开详情</div>
        </div>
        <div style={{ width: 320, background: C.white, borderRadius: 16, padding: 14, transform: "scale(" + interpolate(f, [24, 40], [0.94, 1], CAP) + ")" }}>
          <img src={staticFile("qr.png")} alt="QR" style={{ width: "100%", borderRadius: 8, display: "block" }} />
          <div style={{ color: C.ink, textAlign: "center", fontSize: 17, padding: "8px 0 2px", fontWeight: 700 }}>微信扫码，查看详情</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Promo: React.FC = () => {
  const scenes = [
    { from: 0, to: sec(cue("你还在手动复制吗").end), node: <S1 /> },
    { from: sec(cue("你还在手动复制吗").end), to: sec(cue("漏一天就断").end), node: <S2 /> },
    { from: sec(cue("漏一天就断").end), to: sec(cue("失败通报").end), node: <S3 /> },
    { from: sec(cue("失败通报").end), to: sec(cue("结果可验证").end), node: <S4 /> },
    { from: sec(cue("结果可验证").end), to: sec(cue("都能变成一张自动更新的表").end), node: <S5 /> },
    { from: sec(cue("都能变成一张自动更新的表").end), to: T.frames, node: <S6 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>{s.node}</Sequence>
      ))}
      <Caption />
      <Audio src={staticFile("voice.wav")} />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="CollectorPromo" component={Promo} durationInFrames={T.frames} fps={T.fps} width={T.width} height={T.height} />
);