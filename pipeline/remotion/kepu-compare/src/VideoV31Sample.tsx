import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timeline from "./timeline-v3-sample.json";
import cues from "./cues-v3-sample.json";
import wordsData from "./words-v3-sample.json";
import { Background } from "./Video";

const T: any = timeline;
const CUES: any[] = cues as any[];
const WORDS: any = wordsData as any;
const C = {
  bg: "#0A0E17", panel: "#111826", panel2: "#0C121D",
  line: "rgba(255,255,255,0.09)", text: "#F4F7FB", muted: "#8C97A8",
  tencent: "#2F7BFF", alibaba: "#FF6A00", amber: "#F0A93B",
  green: "#3DDC97", coral: "#FF6B61",
};
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const SceneStart = React.createContext(0);
const sec = (t: number) => Math.round(t * T.fps);
const beat = (id: string) => T.beats.find((x: any) => x.id === id);

const fade = (frame: number, delay: number, dur = 10) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [18, 0], CAP) + "px)",
});

const phraseTime = (beatId: string, phrase: string) => {
  const b = beat(beatId);
  if (!b) return 0;
  const words = (WORDS[beatId] && WORDS[beatId].words) || [];
  const norm = words.map((w: any) => w.text || "").join("");
  const p = norm.indexOf(phrase.replace(/ /g, ""));
  if (p < 0) return b.start + 0.25;
  let acc = 0;
  for (const w of words) {
    const len = (w.text || "").length || 1;
    if (p < acc + len) {
      const t = w.begin_time / 1000 + (p - acc) / len * ((w.end_time - w.begin_time) / 1000);
      return b.start + t;
    }
    acc += len;
  }
  return b.start + 0.25;
};

const Reveal: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; ghost?: boolean }> = ({ at, children, style, ghost }) => {
  const local = useCurrentFrame();
  const offset = React.useContext(SceneStart);
  const { fps } = useVideoConfig();
  const frame = local + offset;
  const start = Math.round((at - 0.12) * fps);
  const o = interpolate(frame, [start, start + 9], [ghost ? 0.16 : 0, 1], CAP);
  const y = interpolate(frame, [start, start + 9], [ghost ? 0 : 16, 0], CAP);
  return <div style={{ opacity: o, transform: "translateY(" + y + "px)", ...style }}>{children}</div>;
};

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.panel, border: "1px solid " + C.line, borderRadius: 4, boxShadow: "0 22px 60px rgba(0,0,0,0.32)", ...style }}>{children}</div>
);

const Badge: React.FC<{ letter: string; color: string }> = ({ letter, color }) => (
  <div style={{ width: 56, height: 56, borderRadius: 10, background: color, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, fontWeight: 800, flexShrink: 0 }}>{letter}</div>
);

const chipStyle = (color: string) => ({ display: "inline-block", padding: "8px 13px", marginRight: 9, marginBottom: 9, border: "1px solid " + color + "55", background: color + "12", color: C.text, fontSize: 20, borderRadius: 3 });

const Header: React.FC<{ frame: number }> = ({ frame }) => {
  const current = T.beats.find((x: any) => frame >= sec(x.start) - 3 && frame <= sec(x.end) + 8);
  const labels: Record<string, string> = { hook: "01 / 03 · 开场", define: "02 / 03 · 定位", context: "03 / 03 · 差异①" };
  return (
    <>
      <div style={{ position: "absolute", top: 0, left: 0, height: 3, width: interpolate(frame, [0, T.frames], [0, 1920], CAP), background: "linear-gradient(90deg, " + C.tencent + ", " + C.alibaba + ")" }} />
      <div style={{ position: "absolute", top: 44, left: 76, display: "flex", gap: 12, alignItems: "center" }}>
        <span style={{ width: 4, height: 24, background: C.amber }} />
        <span style={{ color: C.muted, fontFamily: MONO, fontSize: 18, letterSpacing: 1 }}>{current ? labels[current.section] : ""}</span>
      </div>
      <div style={{ position: "absolute", top: 46, right: 76, fontFamily: FONT, fontSize: 19, color: C.muted }}>
        <span style={{ color: C.tencent, fontWeight: 700 }}>WorkBuddy</span> × <span style={{ color: C.alibaba, fontWeight: 700 }}>Qoder</span>
        <span style={{ color: C.amber, marginLeft: 14, fontFamily: MONO, fontSize: 15 }}>V3.3 SAMPLE</span>
      </div>
    </>
  );
};

const WordCaption: React.FC<{ frame: number }> = ({ frame }) => {
  const cue = CUES.find((c) => frame >= sec(c.start) && frame <= sec(c.end));
  if (!cue) return null;
  const local = frame - sec(cue.start);
  const dur = sec(cue.end) - sec(cue.start);
  const o = Math.min(1, Math.min(local / 4, (dur - local) / 4));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 50, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "13px 28px", borderRadius: 6, background: "rgba(0,0,0,0.72)", border: "1px solid rgba(255,255,255,0.12)", color: C.text, fontFamily: FONT, fontSize: 38, lineHeight: 1.2, whiteSpace: "nowrap", fontWeight: 500 }}>
        {cue.text}
      </div>
    </div>
  );
};

const FocusBar: React.FC<{ frame: number }> = ({ frame }) => {
  const b = T.beats.find((x: any) => frame >= sec(x.start) - 2 && frame <= sec(x.end) + 6);
  const text: Record<string, string> = {
    hook: "一份文档 · 一个 bug · 两条工作流",
    define: "AI 工作台 = 拆任务 + 调工具 + 交付",
    context: "办公上下文 ↔ 工程上下文",
  };
  return (
    <div style={{ position: "absolute", left: 96, right: 96, top: 758, height: 58, display: "flex", alignItems: "center", borderTop: "1px solid " + C.line, borderBottom: "1px solid " + C.line }}>
      <span style={{ color: C.amber, fontFamily: MONO, fontSize: 15, letterSpacing: 1, width: 150 }}>FOCUS</span>
      <span style={{ color: C.muted, fontSize: 22, transition: "none" }}>{b ? text[b.section] : ""}</span>
    </div>
  );
};

const SceneTitle: React.FC<{ kicker: string; title: string; frame: number; instant?: boolean }> = ({ kicker, title, frame, instant }) => (
  <>
    <div style={{ ...(instant ? {} : fade(frame, 0, 8)), display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
      <span style={{ width: 6, height: 20, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 18, letterSpacing: 1 }}>{kicker}</span>
    </div>
    <div style={{ ...(instant ? {} : fade(frame, 2, 10)), color: C.text, fontSize: 50, fontWeight: 800 }}>{title}</div>
  </>
);

const S1: React.FC = () => {
  const frame = useCurrentFrame();
  const float = Math.sin(frame / 26) * 2;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 136, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle instant kicker="COLD OPEN · 周一 9:00" title="如果只装一个 AI 工作台，你选谁？" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 30 }}>
        <Reveal at={beat("b01").start + 0.15} style={{ flex: 1 }}>
          <Panel style={{ padding: 26, transform: "translateY(" + float + "px)" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 14 }}>
              {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
              <span style={{ color: C.muted, fontSize: 16, marginLeft: 10 }}>Q3 周报.doc</span>
            </div>
            <div style={{ color: C.text, fontSize: 30, fontWeight: 700, marginBottom: 16 }}>本周复盘</div>
            {[0.86, 0.74, 0.9, 0.62, 0.8].map((x, i) => <div key={i} style={{ height: 10, width: (x * 100) + "%", background: "rgba(255,255,255,0.13)", borderRadius: 3, marginBottom: 11 }} />)}
            <div style={{ marginTop: 18, color: C.tencent, fontSize: 19 }}>待办：写总结 · 贴数据 · 发老板</div>
          </Panel>
        </Reveal>
        <Reveal at={beat("b01").start + 0.25} style={{ flex: 1 }}>
          <Panel style={{ padding: 26, transform: "translateY(" + (-float) + "px)" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 14 }}>
              {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
              <span style={{ color: C.muted, fontSize: 16, marginLeft: 10 }}>terminal — bug #1284</span>
            </div>
            <div style={{ fontFamily: MONO, fontSize: 18, color: C.coral, marginBottom: 10 }}>FAIL checkout.test.ts</div>
            <div style={{ fontFamily: MONO, fontSize: 17, color: C.muted, lineHeight: 1.8 }}>Expected: 200<br />Received: 500<br />at checkout.ts:42<br />at runTest (node:test)</div>
            <div style={{ marginTop: 16, color: C.alibaba, fontSize: 19 }}>待办：复现 · 定位 · 提 PR</div>
          </Panel>
        </Reveal>
      </div>
      <div style={{ marginTop: 24, textAlign: "center", color: C.muted, fontSize: 25, opacity: 0.9 }}>一份文档，一个 bug。两条完全不同的工作流。</div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const frame = useCurrentFrame();
  const float = Math.sin(frame / 24) * 2;
  const parts = [
    { label: "拆任务", at: phraseTime("b03", "拆任务") },
    { label: "调工具", at: phraseTime("b03", "调工具") },
    { label: "交付结果", at: phraseTime("b03", "交给你") },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 136, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="DEFINITION · 一句话定义" title="都是 AI 工作台，区别在主场" frame={frame} />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, marginTop: 24, minHeight: 54 }}>
        {parts.map((p, i) => (
          <React.Fragment key={p.label}>
            <Reveal at={beat("b03").start + 0.2}>
              <div style={{ padding: "10px 18px", border: "1px solid " + C.amber + "66", background: C.amber + "12", color: C.text, fontSize: 24, borderRadius: 3 }}>{p.label}</div>
            </Reveal>
            {i < parts.length - 1 ? <span style={{ color: C.muted, fontSize: 24 }}>+</span> : null}
          </React.Fragment>
        ))}
        <span style={{ color: C.muted, fontSize: 24, margin: "0 4px" }}>=</span>
        <Reveal at={beat("b03").start + 0.25}><div style={{ padding: "10px 20px", background: C.text, color: C.bg, fontSize: 24, fontWeight: 800, borderRadius: 3 }}>AI 工作台</div></Reveal>
      </div>
      <div style={{ display: "flex", gap: 28, marginTop: 28 }}>
        <Reveal at={beat("b03").start + 0.3} style={{ flex: 1 }}>
          <Panel style={{ padding: 24, transform: "translateY(" + float + "px)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <Badge letter="W" color={C.tencent} />
              <div><div style={{ color: C.text, fontSize: 32, fontWeight: 800 }}>WorkBuddy</div><div style={{ color: C.muted, fontSize: 19, marginTop: 3 }}>腾讯 · 办公工作台</div></div>
            </div>
            <div style={{ marginTop: 16 }}>{["文档", "表格", "会议", "调研"].map((t) => <span key={t} style={chipStyle(C.tencent)}>{t}</span>)}</div>
          </Panel>
        </Reveal>
        <Reveal at={beat("b03").start + 0.35} style={{ flex: 1 }}>
          <Panel style={{ padding: 24, transform: "translateY(" + (-float) + "px)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <Badge letter="Q" color={C.alibaba} />
              <div><div style={{ color: C.text, fontSize: 32, fontWeight: 800 }}>Qoder</div><div style={{ color: C.muted, fontSize: 19, marginTop: 3 }}>阿里 · 编程工作台</div></div>
            </div>
            <div style={{ marginTop: 16 }}>{["代码", "仓库", "Agent", "Repo Wiki"].map((t) => <span key={t} style={chipStyle(C.alibaba)}>{t}</span>)}</div>
          </Panel>
        </Reveal>
      </div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const frame = useCurrentFrame();
  const left = [
    { t: "文档 / 表格", at: phraseTime("b04", "文档") },
    { t: "会议纪要", at: phraseTime("b04", "会议纪要") },
    { t: "腾讯文档", at: phraseTime("b04", "腾讯文档") },
    { t: "企业微信", at: phraseTime("b04", "企业微信") },
  ];
  const right = [
    { t: "代码 / 仓库", at: phraseTime("b04", "代码") },
    { t: "PR / 提交记录", at: phraseTime("b04", "P") },
    { t: "终端报错", at: phraseTime("b04", "终端") },
  ];
  const col = (title: string, color: string, items: any[], headAt: number) => (
    <Panel style={{ flex: 1, padding: 26, borderTop: "3px solid " + color, minHeight: 430 }}>
      <Reveal at={headAt}><div style={{ color, fontSize: 23, fontWeight: 700, marginBottom: 14 }}>{title}</div></Reveal>
      {items.map((it) => (
        <Reveal key={it.t} ghost at={it.at}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0", borderBottom: "1px solid " + C.line, color: C.text, fontSize: 24 }}><span style={{ width: 7, height: 7, background: color, borderRadius: 2 }} /><span style={{ color: "#F4F7FB" }}>{it.t}</span></div>
        </Reveal>
      ))}
      <div style={{ marginTop: 12, color: C.muted, fontSize: 18 }}>{color === C.tencent ? "办公上下文" : "工程上下文"}</div>
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 136, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="差异 01 · 上下文" title="它们读的东西不一样" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 24 }}>
        {col("WorkBuddy 读什么", C.tencent, left, beat("b04").start + 0.05)}
        {col("Qoder 读什么", C.alibaba, right, beat("b04").start + 0.05)}
      </div>
    </AbsoluteFill>
  );
};

export const KepuV31Sample: React.FC = () => {
  const frame = useCurrentFrame();
  const b01 = beat("b01");
  const b03 = beat("b03");
  const b04 = beat("b04");
  const scenes = [
    { from: 0, to: sec(b01.end + 0.05), node: <S1 /> },
    { from: sec(b01.end - 0.15), to: sec(b03.end + 0.05), node: <S2 /> },
    { from: sec(b03.end - 0.15), to: sec(T.duration), node: <S3 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice-v3-sample.wav")} />
      <Background />
      <Header frame={frame} />
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>
          <SceneStart.Provider value={s.from}>{s.node}</SceneStart.Provider>
        </Sequence>
      ))}
      <FocusBar frame={frame} />
      <WordCaption frame={frame} />
    </AbsoluteFill>
  );
};