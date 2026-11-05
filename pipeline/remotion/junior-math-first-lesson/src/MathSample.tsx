import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import timeline from "./timeline.json";
import cues from "./cues.json";
import anchors from "./anchors.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const A: any = anchors as any;
const C = {
  bg: "#101418", panel: "#1A2024", panel2: "#151B20",
  line: "rgba(242,239,230,0.12)", text: "#F2EFE6", muted: "#A8A49A",
  amber: "#F0A93B", red: "#FF6B61", blue: "#4D9FFF", green: "#3DDC97",
};
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const SceneStart = React.createContext(0);
const beat = (id: string) => T.beats.find((x: any) => x.id === id);

const fade = (frame: number, delay: number, dur = 12) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [16, 0], CAP) + "px)",
});

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.panel, border: "1px solid " + C.line, borderRadius: 4, ...style }}>{children}</div>
);

const Header: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 44, left: 76, display: "flex", alignItems: "center", gap: 12 }}>
      <span style={{ width: 4, height: 24, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 17, letterSpacing: 1 }}>初中数学第一课 · 样片</span>
    </div>
    <div style={{ position: "absolute", top: 46, right: 76, color: C.muted, fontFamily: FONT, fontSize: 19 }}>
      负数与数轴
    </div>
  </>
);

const Caption: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = CUES.find((c) => frame >= sec(c.start) && frame <= sec(c.end));
  if (!cue) return null;
  const local = frame - sec(cue.start);
  const dur = sec(cue.end) - sec(cue.start);
  const o = Math.min(1, Math.min(local / 4, (dur - local) / 4));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 52, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "13px 28px", borderRadius: 6, background: "rgba(0,0,0,0.66)", border: "1px solid rgba(242,239,230,0.12)", color: C.text, fontFamily: FONT, fontSize: 34, lineHeight: 1.2, whiteSpace: "nowrap" }}>{cue.text}</div>
    </div>
  );
};

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(242,239,230,0.04) 1px, transparent 1px),linear-gradient(90deg, rgba(242,239,230,0.04) 1px, transparent 1px)", backgroundSize: "96px 96px", transform: "translate(" + Math.sin(frame / 120) * 4 + "px," + Math.cos(frame / 140) * 3 + "px)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 300, background: "radial-gradient(800px 300px at 50% 100%, rgba(240,169,59,0.06), transparent 70%)" }} />
    </AbsoluteFill>
  );
};

const Title: React.FC<{ kicker: string; title: string; frame: number; instant?: boolean }> = ({ kicker, title, frame, instant }) => (
  <>
    <div style={{ ...(instant ? {} : fade(frame, 0, 9)), display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
      <span style={{ width: 6, height: 20, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 17, letterSpacing: 1 }}>{kicker}</span>
    </div>
    <div style={{ ...(instant ? {} : fade(frame, 2, 10)), color: C.text, fontSize: 50, fontWeight: 800 }}>{title}</div>
  </>
);

const S1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 }, delay: 2 });
  const drop = interpolate(frame, [30, 130], [0, 1], CAP);
  const mercuryH = 360 - drop * 300;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title instant kicker="COLD OPEN · 开场" title="0℃ 以下，也是温度" frame={frame} />
      <div style={{ display: "flex", gap: 36, marginTop: 30 }}>
        <Panel style={{ width: 560, padding: 28, opacity: 1 }}>
          <div style={{ color: C.muted, fontSize: 20, marginBottom: 16 }}>温度计</div>
          <div style={{ display: "flex", gap: 28, alignItems: "flex-end" }}>
            <div style={{ position: "relative", width: 54, height: 430 }}>
              <div style={{ position: "absolute", left: 14, top: 0, width: 26, height: 400, border: "2px solid " + C.text, borderRadius: 13 }} />
              <div style={{ position: "absolute", left: 20, bottom: 22, width: 14, height: mercuryH, background: C.red, borderRadius: 7 }} />
              <div style={{ position: "absolute", left: 2, bottom: 8, width: 50, height: 50, borderRadius: 25, background: C.red }} />
            </div>
            <div style={{ paddingBottom: 40 }}>
              {["3℃", "0℃", "-3℃"].map((x, i) => (
                <div key={x} style={{ color: i === 2 ? C.text : C.muted, fontSize: 30, margin: "64px 0", textAlign: "left" }}>{x}</div>
              ))}
            </div>
          </div>
        </Panel>
        <Panel style={{ flex: 1, padding: 32, opacity: 1 }}>
          <div style={{ color: C.muted, fontSize: 20, marginBottom: 20 }}>问题卡</div>
          {["天气预报：最低 -3℃", "读作：零下三摄氏度", "也可以读：负三摄氏度", "0℃ 是不是「没有温度」？"].map((x, i) => (
            <div key={x} style={{ ...(i === 0 ? { opacity: 1 } : fade(frame, 6 + i * 8)), color: i === 3 ? C.text : C.muted, fontSize: i === 3 ? 38 : 30, marginBottom: 22 }}>{x}</div>
          ))}
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const local = useCurrentFrame();
  const offset = React.useContext(SceneStart);
  const frame = local + offset;
  const rightOn = frame >= sec(A["规定支出为正"]) - 10;
  const leftOn = !rightOn;
  const card = (title: string, color: string, rows: [string, string][], active: boolean, side: "left" | "right") => (
    <Panel style={{ flex: 1, padding: 28, borderTop: "3px solid " + (active ? C.amber : color), opacity: active ? 1 : 0.5, transform: "translateY(" + (active ? -4 : 0) + "px)" }}>
      <div style={{ color: active ? C.amber : color, fontSize: 26, fontWeight: 700, marginBottom: 20 }}>{title}</div>
      {rows.map(([a, b]) => (
        <div key={a} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "16px 0", borderBottom: "1px solid " + C.line }}>
          <span style={{ color: C.muted, fontSize: 26 }}>{a}</span>
          <span style={{ color: C.text, fontFamily: MONO, fontSize: 44 }}>{b}</span>
        </div>
      ))}
      <div style={{ marginTop: 20, color: C.muted, fontSize: 20 }}>{side === "left" ? "规定收入为正" : "规定支出为正"}</div>
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="RULE · 规定" title="同一组量，两种规定，符号相反" frame={frame} />
      <div style={{ display: "flex", gap: 30, marginTop: 28 }}>
        {card("A · 规定收入为正", C.blue, [["收入 200", "+200"], ["支出 150", "-150"]], leftOn, "left")}
        {card("B · 规定支出为正", C.red, [["收入 200", "-200"], ["支出 150", "+150"]], rightOn, "right")}
      </div>
      <div style={{ ...fade(frame, 40), marginTop: 26, textAlign: "center", color: C.muted, fontSize: 24 }}>两种都行，但同一题只能选一种；+ 是正号，- 是负号</div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const frame = useCurrentFrame();
  const cards = [
    { t: "0 个苹果", s: "记数：没有", at: 4 },
    { t: "0℃", s: "温度：确定刻度", at: 14 },
    { t: "0 米海拔", s: "基准：海平面", at: 24 },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 120, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="ZERO · 0" title="0 个 / 0℃ / 0 米：三种 0，两种用法" frame={frame} />
      <div style={{ display: "flex", justifyContent: "center", marginTop: 14 }}>
        <div style={{ ...fade(frame, 2), textAlign: "center" }}>
          <div style={{ color: C.text, fontSize: 100, lineHeight: 1 }}>0</div>
          <div style={{ color: C.amber, fontSize: 24, marginTop: 4 }}>是分界</div>
        </div>
      </div>
      <div style={{ display: "flex", gap: 26, marginTop: 24 }}>
        {cards.map((c, i) => (
          <Panel key={c.t} style={{ flex: 1, padding: 24, opacity: fade(frame, c.at).opacity, transform: fade(frame, c.at).transform }}>
            <div style={{ color: C.text, fontSize: 30, fontWeight: 700 }}>{c.t}</div>
            <div style={{ color: C.muted, fontSize: 22, marginTop: 10 }}>{c.s}</div>
            {i === 0 ? (
              <div style={{ height: 100, marginTop: 18, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, border: "1px solid " + C.line, background: C.panel2 }}>
                <span style={{ color: C.muted, fontSize: 54, opacity: 0.55 }}>0</span>
                <span style={{ color: C.muted, fontSize: 22 }}>个</span>
              </div>
            ) : i === 1 ? (
              <div style={{ height: 100, marginTop: 18, display: "flex", alignItems: "center", justifyContent: "center", gap: 14, border: "1px solid " + C.line, background: C.panel2 }}>
                <div style={{ width: 18, height: 92, border: "2px solid " + C.muted, borderRadius: 9, position: "relative" }}>
                  <div style={{ position: "absolute", left: 4, bottom: 3, width: 6, height: 34, background: C.red, borderRadius: 3 }} />
                </div>
                <span style={{ color: C.muted, fontSize: 22 }}>确定刻度</span>
              </div>
            ) : (
              <div style={{ height: 100, marginTop: 18, position: "relative", border: "1px solid " + C.line, background: C.panel2, overflow: "hidden" }}>
                <div style={{ position: "absolute", left: 0, right: 0, top: 58, height: 2, background: C.muted }} />
                <div style={{ position: "absolute", left: 0, right: 0, top: 60, bottom: 0, background: "rgba(77,159,255,0.10)" }} />
                <span style={{ position: "absolute", left: 16, top: 30, color: C.muted, fontSize: 20 }}>海平面</span>
              </div>
            )}
          </Panel>
        ))}
      </div>
      <div style={{ ...fade(frame, 34), marginTop: 18, textAlign: "center", color: C.muted, fontSize: 24 }}>0 既不是正数，也不是负数</div>
    </AbsoluteFill>
  );
};

const S4: React.FC = () => {
  const local = useCurrentFrame();
  const offset = React.useContext(SceneStart);
  const frame = local + offset;
  const draw = interpolate(local, [4, 40], [0, 1], CAP);
  const answer = frame >= sec(A["-3 在 -1 左边"]) - 10;
  const x0 = 960, unit = 60;
  const pts = [{ n: "-3", x: x0 - 3 * unit }, { n: "-1", x: x0 - unit }, { n: "0", x: x0 }, { n: "+3", x: x0 + 3 * unit }];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="NUMBER LINE · 数轴" title="原点、正方向、单位长度；右边总比左边大" frame={frame} />
      <div style={{ position: "absolute", left: 160, right: 160, top: 580, height: 4, background: C.text, transformOrigin: "left", transform: "scaleX(" + draw + ")" }} />
      {draw > 0.95 ? <div style={{ position: "absolute", left: 1738, top: 568, color: C.text, fontSize: 34 }}>→</div> : null}
      {pts.map((p) => (
        <div key={p.n} style={{ position: "absolute", left: p.x - 9, top: 571, width: 18, height: 18, borderRadius: 9, background: C.text }} />
      ))}
      {pts.map((p) => (
        <div key={p.n + "l"} style={{ position: "absolute", left: p.x - 20, top: 620, color: C.text, fontFamily: MONO, fontSize: 26, width: 40, textAlign: "center" }}>{p.n}</div>
      ))}
      <div style={{ position: "absolute", left: 930, top: 665, color: C.muted, fontSize: 20 }}>原点</div>
      <div style={{ position: "absolute", left: 1570, top: 520, color: C.muted, fontSize: 20 }}>正方向</div>
      <div style={{ position: "absolute", left: 850, top: 720, display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 60, height: 3, background: C.amber }} />
        <span style={{ color: C.muted, fontSize: 20 }}>单位长度：1 格 = 1</span>
      </div>
      {answer ? (
        <div style={{ ...fade(frame, 0), position: "absolute", left: 700, top: 500, color: C.amber, fontSize: 42, fontWeight: 800 }}>-3 &lt; -1</div>
      ) : (
        <Panel style={{ position: "absolute", left: 1320, top: 220, width: 500, padding: 24 }}>
          <div style={{ color: C.muted, fontSize: 20 }}>先猜</div>
          <div style={{ color: C.text, fontSize: 34, marginTop: 10 }}>-3 和 -1，谁大？</div>
          <div style={{ color: C.muted, fontSize: 20, marginTop: 12 }}>停两秒，再看数轴</div>
        </Panel>
      )}
    </AbsoluteFill>
  );
};

export const MathSample: React.FC = () => {
  const frame = useCurrentFrame();
  const b01 = beat("b01");
  const b02 = beat("b02");
  const b03 = beat("b03");
  const scenes = [
    { from: 0, to: sec(b01.end + 0.05), node: <S1 /> },
    { from: sec(b01.end + 0.05), to: sec(b02.end + 0.05), node: <S2 /> },
    { from: sec(b02.end + 0.05), to: sec(b03.end + 0.05), node: <S3 /> },
    { from: sec(b03.end + 0.05), to: sec(T.duration), node: <S4 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice.wav")} />
      <Background />
      <Header />
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}><SceneStart.Provider value={s.from}>{s.node}</SceneStart.Provider></Sequence>
      ))}
      <Caption />
    </AbsoluteFill>
  );
};