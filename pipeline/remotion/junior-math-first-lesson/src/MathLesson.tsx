import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline-full.json";
import cues from "./cues-full.json";
import anchors from "./anchors-full.json";

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
const beat = (id: string) => T.beats.find((x: any) => x.id === id);
const endOf = (scene: string) => T.beats.filter((b: any) => b.scene === scene).pop().end;
const SceneStart = React.createContext(0);
const useGlobalFrame = () => useCurrentFrame() + React.useContext(SceneStart);
const reveal = (frame: number, at: number, dur = 9) => ({
  opacity: interpolate(frame, [sec(at), sec(at) + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [sec(at), sec(at) + dur], [12, 0], CAP) + "px)",
});
const fade = (frame: number, delay: number, dur = 10) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [14, 0], CAP) + "px)",
});

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.panel, border: "1px solid " + C.line, borderRadius: 4, ...style }}>{children}</div>
);

const Header: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 44, left: 96, display: "flex", alignItems: "center", gap: 12 }}>
      <span style={{ width: 4, height: 24, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 17, letterSpacing: 1 }}>初中数学第一课</span>
    </div>
    <div style={{ position: "absolute", top: 46, right: 96, color: C.muted, fontFamily: FONT, fontSize: 19 }}>负数与数轴</div>
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
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(242,239,230,0.035) 1px, transparent 1px),linear-gradient(90deg, rgba(242,239,230,0.035) 1px, transparent 1px)", backgroundSize: "96px 96px", transform: "translate(" + Math.sin(frame / 140) * 8 + "px," + Math.cos(frame / 160) * 6 + "px)" }} />
      <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 18% 28%, rgba(242,239,230,0.13) 0 1px, transparent 2px),radial-gradient(circle at 72% 62%, rgba(242,239,230,0.10) 0 1px, transparent 2px),radial-gradient(circle at 44% 80%, rgba(240,169,59,0.12) 0 1px, transparent 2px)", backgroundSize: "320px 280px, 420px 360px, 520px 440px", backgroundPosition: (Math.sin(frame / 220) * 20) + "px " + (Math.cos(frame / 260) * 16) + "px, " + (Math.cos(frame / 240) * 14) + "px " + (Math.sin(frame / 300) * 12) + "px, " + (Math.sin(frame / 280) * 10) + "px " + (Math.cos(frame / 320) * 8) + "px", opacity: 0.55 }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 380, background: "radial-gradient(900px 320px at 50% 100%, rgba(240,169,59,0.08), transparent 70%)" }} />
    </AbsoluteFill>
  );
};

const Title: React.FC<{ kicker: string; title: string; frame: number }> = ({ kicker, title, frame }) => (
  <>
    <div style={{ ...fade(frame, -10, 6), display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
      <span style={{ width: 6, height: 20, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 17, letterSpacing: 1 }}>{kicker}</span>
    </div>
    <div style={{ ...fade(frame, -10, 6), color: C.text, fontSize: 50, fontWeight: 800 }}>{title}</div>
  </>
);

const Thermometer: React.FC<{ height: number; drop: number }> = ({ height, drop }) => (
  <div style={{ position: "relative", width: 54, height }}>
    <div style={{ position: "absolute", left: 14, top: 0, width: 26, height: height - 30, border: "2px solid " + C.text, borderRadius: 13 }} />
    <div style={{ position: "absolute", left: 20, bottom: 22, width: 14, height: drop, background: C.red, borderRadius: 7 }} />
    <div style={{ position: "absolute", left: 2, bottom: 8, width: 50, height: 50, borderRadius: 25, background: C.red }} />
  </div>
);

const S0: React.FC = () => {
  const local = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center" }}>
        <div style={{ ...fade(local, 0, 9), display: "flex", alignItems: "center", justifyContent: "center", gap: 12, marginBottom: 28 }}>
          <span style={{ width: 8, height: 26, background: C.amber }} />
          <span style={{ color: C.muted, fontFamily: MONO, fontSize: 24, letterSpacing: 2 }}>初中数学第一课</span>
        </div>
        <div style={{ ...fade(local, 2, 9), color: C.text, fontSize: 100, fontWeight: 800, letterSpacing: 2 }}>0℃ 以下，也是温度</div>
        <div style={{ ...fade(local, 8, 9), color: C.muted, fontSize: 38, marginTop: 30 }}>负数与数轴</div>
      </div>
      <div style={{ position: "absolute", right: 220, top: 280, opacity: 0.9 }}>
        <Thermometer height={430} drop={150} />
      </div>
    </AbsoluteFill>
  );
};

const S1: React.FC = () => {
  const local = useCurrentFrame();
  const frame = useGlobalFrame();
  const drop = interpolate(local, [8, 70], [360, 60], CAP);
  const below = drop < 210;
  const lines = [
    { t: "天气预报：最低 -3℃", at: 0 },
    { t: "这个数写作：-3", at: A["这个数写作负三"] },
    { t: "读作：零下三摄氏度", at: A["读作零下三摄氏度"] },
    { t: "也可以读：负三摄氏度", at: A["也可以读负三摄氏度"] },
    { t: "0℃ 是不是「没有温度」？", at: A["零摄氏度又是不是没有温度"] },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="COLD OPEN · 开场" title="为什么数学里要写成 -3？" frame={frame} />
      <div style={{ display: "flex", gap: 36, marginTop: 30 }}>
        <Panel style={{ width: 560, padding: 28 }}>
          <div style={{ color: C.muted, fontSize: 20, marginBottom: 16 }}>温度计</div>
          <div style={{ display: "flex", gap: 28, alignItems: "flex-end" }}>
            <Thermometer height={430} drop={drop} />
            <div style={{ paddingBottom: 40 }}>
              {["3℃", "0℃", "-3℃"].map((x, i) => (
                <div key={x} style={{ color: i === 2 ? (below ? C.red : C.muted) : (i === 1 ? C.amber : C.muted), fontSize: 30, margin: "64px 0", fontWeight: i === 2 && below ? 700 : 400 }}>{x}</div>
              ))}
            </div>
          </div>
        </Panel>
        <Panel style={{ flex: 1, padding: 32 }}>
          <div style={{ color: C.muted, fontSize: 20, marginBottom: 20 }}>问题卡</div>
          {lines.map((x, i) => (
            <div key={x.t} style={{ ...(i === 0 ? { opacity: 1 } : reveal(frame, x.at)), color: i === 4 ? C.text : C.muted, fontSize: i === 4 ? 38 : 30, marginBottom: 22, fontWeight: i === 4 ? 700 : 400 }}>{x.t}</div>
          ))}
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const frame = useGlobalFrame();
  const declared = frame >= sec(A["规定收入为正"]) - 4;
  const right = frame >= sec(A["规定支出为正"]) - 4;
  const settled = frame >= sec(A["两种规定都行"]) - 4;
  const plusSign = frame >= sec(A["正二百前面的符号是正号"]) - 4;
  const minusSign = frame >= sec(A["负一百五十前面的符号是负号"]) - 4;
  const card = (title: string, color: string, rows: [string, string][], active: boolean, dim: number) => (
    <Panel style={{ flex: 1, padding: 28, borderTop: "3px solid " + (active ? C.amber : color), opacity: dim, transform: "translateY(" + (active ? -4 : 0) + "px) scale(" + (active ? 1.03 : 0.985) + ")", boxShadow: active ? "0 0 28px rgba(240,169,59,0.12)" : "none" }}>
      <div style={{ color: active ? C.amber : color, fontSize: 26, fontWeight: 700, marginBottom: 18 }}>{title}</div>
      {rows.map(([a, b]) => (
        <div key={a} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "16px 0", borderBottom: "1px solid " + C.line }}>
          <span style={{ color: C.muted, fontSize: 26 }}>{a}</span>
          <span style={{ color: C.text, fontFamily: MONO, fontSize: 44 }}>{b}</span>
        </div>
      ))}
    </Panel>
  );
  const leftDim = settled ? 0.95 : (right ? 0.65 : (declared ? 1 : 0.7));
  const rightDim = settled ? 0.95 : (right ? 1 : 0.65);
  const note = minusSign ? "「-」是负号，不是减法" : plusSign ? "「+」是正号，不是加法" : "两种规定都行，但同一题只能选一种";
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="RULE · 规定" title="同一组量，两种规定，符号相反" frame={frame} />
      <div style={{ display: "flex", gap: 30, marginTop: 28 }}>
        {card("A · 规定收入为正", C.blue, [["收入 200", "+200"], ["支出 150", "-150"]], declared && !right, leftDim)}
        {card("B · 规定支出为正", C.red, [["收入 200", "-200"], ["支出 150", "+150"]], right, rightDim)}
      </div>
      <div style={{ ...(settled ? fade(frame, 0, 6) : { opacity: 0 }), marginTop: 26, textAlign: "center", color: plusSign || minusSign ? C.amber : C.muted, fontSize: 26, fontWeight: plusSign || minusSign ? 700 : 400 }}>{note}</div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const frame = useGlobalFrame();
  const twoUses = frame >= sec(A["所以零有两种用法"]) - 2;
  const zeroOn = frame >= sec(A["零既不是正数"]) - 2;
  const finishOn = frame >= sec(A["它是正负数的分界"]) - 2;
  const cards = [
    { t: "0 个苹果", s: "记数：没有", at: A["零个苹果"] },
    { t: "0℃", s: "温度：确定刻度", at: A["零摄氏度不是没有温度"] },
    { t: "0 米海拔", s: "基准：海平面", at: A["零米海拔"] },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 120, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="ZERO · 0" title="0 个 / 0℃ / 0 米：三种 0，两种用法" frame={frame} />
      {zeroOn ? (
        <div style={{ display: "flex", justifyContent: "center", marginTop: 12, opacity: interpolate(frame, [sec(A["零既不是正数"]) - 2, sec(A["零既不是正数"]) + 7], [0, 1], CAP) }}>
          <div style={{ textAlign: "center", transform: "scale(" + interpolate(frame, [sec(A["零既不是正数"]) - 2, sec(A["零既不是正数"]) + 10, sec(A["零既不是正数"]) + 18], [0.8, 1.2, 1.0], CAP) + ")" }}>
            <div style={{ color: C.text, fontSize: 96, lineHeight: 1 }}>0</div>
            <div style={{ color: C.amber, fontSize: 24, marginTop: 2 }}>是分界</div>
            {finishOn ? <div style={{ position: "absolute", left: -20, top: -8, width: 136, height: 136, border: "2px solid " + C.amber, borderRadius: "50%", opacity: 0.65 }} /> : null}
          </div>
        </div>
      ) : null}
      <div style={{ display: "flex", gap: 26, marginTop: zeroOn ? 8 : 24 }}>
        {cards.map((c, i) => (
          <Panel key={c.t} style={{ flex: 1, padding: 24, opacity: interpolate(frame, [sec(c.at), sec(c.at) + 9], [0, 1], CAP), transform: "translateY(" + interpolate(frame, [sec(c.at), sec(c.at) + 9], [12, 0], CAP) + "px)" }}>
            <div style={{ color: C.text, fontSize: 30, fontWeight: 700 }}>{c.t}</div>
            <div style={{ color: C.muted, fontSize: 22, marginTop: 10 }}>{c.s}</div>
            {i === 0 ? (
              <div style={{ height: 100, marginTop: 18, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, border: "1px solid " + C.line, background: C.panel2 }}>
                <span style={{ color: C.muted, fontSize: 54, opacity: 0.55 }}>0</span><span style={{ color: C.muted, fontSize: 22 }}>个</span>
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
      <div style={{ marginTop: 18, textAlign: "center", color: zeroOn ? C.muted : C.amber, fontSize: 24, opacity: twoUses ? 1 : 0 }}>
        {zeroOn ? "0 既不是正数，也不是负数" : "记数时表示「没有」；作刻度或基准时，是一个确定的点"}
      </div>
    </AbsoluteFill>
  );
};

const S4: React.FC = () => {
  const local = useCurrentFrame();
  const frame = useGlobalFrame();
  const draw = interpolate(local, [4, 22], [0, 1], CAP);
  const origin = frame >= sec(A["原点就是零"]) - 2;
  const arrow = frame >= sec(A["正方向画箭头"]) - 2;
  const unit = frame >= sec(A["单位长度就是一格代表多少"]) - 2;
  const plus = frame >= sec(A["正三在原点右边"]);
  const minus3 = frame >= sec(A["负三在左边"]);
  const minus1 = frame >= sec(A["负三和负一"]);
  const rule = frame >= sec(A["右边的数总比左边大"]) - 2;
  const answer = frame >= sec(A["负三在负一左边"]);
  const x0 = 960, unitPx = 60;
  const pts = [
    { n: "-3", x: x0 - 3 * unitPx, on: minus3, hot: answer },
    { n: "-1", x: x0 - unitPx, on: minus1, hot: answer },
    { n: "0", x: x0, on: origin, hot: false },
    { n: "+3", x: x0 + 3 * unitPx, on: plus, hot: false },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="NUMBER LINE · 数轴" title="数轴：原点、正方向、单位长度" frame={frame} />
      <div style={{ position: "absolute", left: 160, right: 160, top: 580, height: 4, background: C.text, transformOrigin: "left", transform: "scaleX(" + draw + ")" }} />
      {arrow ? <div style={{ position: "absolute", left: 1738, top: 568, color: C.text, fontSize: 34 }}>→</div> : null}
      {unit ? Array.from({ length: 21 }).map((_, i) => {
        const x = x0 + (i - 10) * unitPx;
        const on = interpolate(local, [0, 1], [0, 1], CAP); // ticks fade with anchor
        return <div key={"t" + i} style={{ position: "absolute", left: x - 1, top: 610, width: 2, height: 20, background: C.muted, opacity: 0.55 * on }} />;
      }) : null}
      {pts.map((p) => p.on ? <div key={p.n} style={{ position: "absolute", left: p.x - 11, top: 569, width: 22, height: 22, borderRadius: 11, background: p.hot ? C.amber : C.text }} /> : null)}
      {pts.map((p) => p.on ? <div key={p.n + "l"} style={{ position: "absolute", left: p.x - 24, top: 620, color: p.hot ? C.amber : C.text, fontFamily: MONO, fontSize: 26, width: 48, textAlign: "center" }}>{p.n}</div> : null)}
      {origin ? <div style={{ position: "absolute", left: 930, top: 665, color: C.muted, fontSize: 20 }}>原点</div> : null}
      {arrow ? <div style={{ position: "absolute", left: 1570, top: 520, color: C.muted, fontSize: 20 }}>正方向</div> : null}
      {unit ? (
        <div style={{ position: "absolute", left: 850, top: 720, display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 60, height: 3, background: C.amber }} /><span style={{ color: C.muted, fontSize: 20 }}>单位长度：1 格 = 1，每格等长</span>
        </div>
      ) : null}
      {rule && !answer ? <div style={{ position: "absolute", left: 680, top: 500, color: C.muted, fontSize: 28 }}>右边的数总比左边大</div> : null}
      {!answer && minus1 ? (
        <Panel style={{ position: "absolute", left: 1320, top: 220, width: 500, padding: 24 }}>
          <div style={{ color: C.muted, fontSize: 20 }}>先猜</div>
          <div style={{ color: C.text, fontSize: 34, marginTop: 10 }}>-3 和 -1，谁大？</div>
          <div style={{ color: C.muted, fontSize: 20, marginTop: 12 }}>停两秒，再看数轴</div>
        </Panel>
      ) : null}
      {answer ? (
        <div style={{ position: "absolute", left: 700, top: 500, display: "flex", alignItems: "center", gap: 12, color: C.amber, fontSize: 28 }}>
          <span>-3</span><span style={{ width: 110, height: 2, background: C.amber }} /><span>-1</span>
          <span style={{ fontSize: 20, color: C.muted, marginLeft: 10 }}>越往左越小</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const S5: React.FC = () => {
  const local = useCurrentFrame();
  const frame = useGlobalFrame();
  const draw = interpolate(local, [2, 18], [0, 1], CAP);
  const points = frame >= sec(A["负一百和负一"]) - 2;
  const answer = frame >= sec(A["负一百在负一左边"]);
  const rule = frame >= sec(A["负号后面的数越大"]) - 2;
  const x = (v: number) => 1660 + v * 15;
  const link = answer ? interpolate(frame, [sec(A["负一百在负一左边"]), sec(A["负一百在负一左边"]) + 15], [0, 1], CAP) : 0;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="COMPARE · 比较" title="-100 和 -1，谁大？" frame={frame} />
      {answer ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center", ...fade(frame, sec(A["负一百在负一左边"]), 8) }}>
          <span style={{ color: C.amber, fontFamily: MONO, fontSize: 72, fontWeight: 700 }}>-100 &lt; -1</span>
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 140, right: 140, top: 600, height: 4, background: C.text, transformOrigin: "left", transform: "scaleX(" + draw + ")" }} />
      {draw > 0.95 ? <div style={{ position: "absolute", left: 1758, top: 588, color: C.text, fontSize: 34 }}>→</div> : null}
      {draw > 0.9 ? Array.from({ length: 11 }).map((_, i) => {
        const v = -100 + i * 10;
        return <div key={"t" + i} style={{ position: "absolute", left: x(v) - 1, top: 630, width: 2, height: 18, background: C.muted, opacity: 0.5 }} />;
      }) : null}
      {draw > 0.9 ? <div style={{ position: "absolute", left: x(0) - 12, top: 656, color: C.muted, fontFamily: MONO, fontSize: 24, width: 24, textAlign: "center" }}>0</div> : null}
      {points ? (
        <>
          <div style={{ position: "absolute", left: x(-100) - 12, top: 588, width: 24, height: 24, borderRadius: 12, background: answer ? C.amber : C.text }} />
          <div style={{ position: "absolute", left: x(-100) - 60, top: 656, width: 120, textAlign: "center", color: answer ? C.amber : C.text, fontFamily: MONO, fontSize: 30 }}>-100</div>
          <div style={{ position: "absolute", left: x(-1) - 12, top: 588, width: 24, height: 24, borderRadius: 12, background: answer ? C.amber : C.text }} />
          <div style={{ position: "absolute", left: x(-1) - 40, top: 536, width: 80, textAlign: "center", color: answer ? C.amber : C.text, fontFamily: MONO, fontSize: 30 }}>-1</div>
        </>
      ) : null}
      {link > 0 ? <div style={{ position: "absolute", left: x(-100), top: 560, width: (x(-1) - x(-100)) * link, height: 3, background: C.amber }} /> : null}
      {!answer && points ? (
        <Panel style={{ position: "absolute", left: 700, top: 260, width: 520, padding: 24, textAlign: "center" }}>
          <div style={{ color: C.muted, fontSize: 20 }}>先猜</div>
          <div style={{ color: C.text, fontSize: 34, marginTop: 10 }}>-100 和 -1，谁大？</div>
        </Panel>
      ) : null}
      {rule ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 740, textAlign: "center", ...fade(frame, sec(A["负号后面的数越大"]) - 2, 8) }}>
          <span style={{ color: C.text, fontSize: 30 }}>负号后的数越大</span>
          <span style={{ color: C.amber, fontSize: 30 }}> → 位置越靠左 → 值反而越小</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const S6: React.FC = () => {
  const frame = useGlobalFrame();
  const stage = frame < sec(beat("b6a").end) ? 1 : frame < sec(beat("b6b").end) ? 2 : 3;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      {stage === 1 ? <S6a frame={frame} /> : stage === 2 ? <S6b frame={frame} /> : <S6c frame={frame} />}
    </AbsoluteFill>
  );
};

const S6a: React.FC<{ frame: number }> = ({ frame }) => {
  const left = frame >= sec(A["一个表示没有"]) - 2;
  const right = frame >= sec(A["一个是确定温度"]) - 2;
  return (
    <>
      <Title kicker="CHECK 1 / 3 · 三个坑" title="0 个苹果 和 0℃，意义一样吗？" frame={frame} />
      <div style={{ display: "flex", gap: 40, marginTop: 60, justifyContent: "center" }}>
        <Panel style={{ width: 620, padding: 36, textAlign: "center" }}>
          <div style={{ color: C.text, fontSize: 64, fontWeight: 800 }}>0 个苹果</div>
          <div style={{ marginTop: 26, fontSize: 30, color: left ? C.amber : C.muted, fontWeight: left ? 700 : 400 }}>{left ? "表示「没有」" : "？"}</div>
        </Panel>
        <Panel style={{ width: 620, padding: 36, textAlign: "center" }}>
          <div style={{ color: C.text, fontSize: 64, fontWeight: 800 }}>0℃</div>
          <div style={{ marginTop: 26, fontSize: 30, color: right ? C.amber : C.muted, fontWeight: right ? 700 : 400 }}>{right ? "确定的温度" : "？"}</div>
        </Panel>
      </div>
    </>
  );
};

const S6b: React.FC<{ frame: number }> = ({ frame }) => {
  const left = frame >= sec(A["负三前面的符号是负号"]) - 2;
  const right = frame >= sec(A["三减五中间的符号是减号"]) - 2;
  return (
    <>
      <Title kicker="CHECK 2 / 3 · 三个坑" title="两个「-」，一样吗？" frame={frame} />
      <div style={{ display: "flex", gap: 40, marginTop: 60, justifyContent: "center" }}>
        <Panel style={{ width: 620, padding: 36, textAlign: "center" }}>
          <div style={{ fontFamily: MONO, fontSize: 96, fontWeight: 700 }}><span style={{ color: left ? C.amber : C.text }}>-</span><span style={{ color: C.text }}>3</span></div>
          <div style={{ marginTop: 26, fontSize: 30, color: left ? C.amber : C.muted, fontWeight: left ? 700 : 400 }}>{left ? "数前面：负号" : "？"}</div>
        </Panel>
        <Panel style={{ width: 620, padding: 36, textAlign: "center" }}>
          <div style={{ fontFamily: MONO, fontSize: 96, fontWeight: 700 }}><span style={{ color: C.text }}>3</span><span style={{ color: right ? C.amber : C.text }}>-</span><span style={{ color: C.text }}>5</span></div>
          <div style={{ marginTop: 26, fontSize: 30, color: right ? C.amber : C.muted, fontWeight: right ? 700 : 400 }}>{right ? "两数之间：减号" : "？"}</div>
        </Panel>
      </div>
    </>
  );
};

const S6c: React.FC<{ frame: number }> = ({ frame }) => {
  const points = frame >= sec(A["第三负五"]) - 2;
  const answer = frame >= sec(A["负五在负二左边"]);
  const x0 = 1160, unit = 120;
  const x = (v: number) => x0 + v * unit;
  const link = answer ? interpolate(frame, [sec(A["负五在负二左边"]), sec(A["负五在负二左边"]) + 12], [0, 1], CAP) : 0;
  return (
    <>
      <Title kicker="CHECK 3 / 3 · 三个坑" title="-5 和 -2，谁小？" frame={frame} />
      {!answer && points ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center", color: C.muted, fontSize: 28 }}>先猜，再看数轴</div>
      ) : null}
      {answer ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 290, textAlign: "center", ...fade(frame, sec(A["负五在负二左边"]), 8) }}>
          <span style={{ color: C.amber, fontFamily: MONO, fontSize: 64, fontWeight: 700 }}>-5 &lt; -2</span>
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 320, right: 320, top: 600, height: 4, background: C.text }} />
      <div style={{ position: "absolute", left: 1578, top: 588, color: C.text, fontSize: 34 }}>→</div>
      {Array.from({ length: 9 }).map((_, i) => {
        const v = i - 6;
        return <div key={"t" + i} style={{ position: "absolute", left: x(v) - 1, top: 630, width: 2, height: 18, background: C.muted, opacity: 0.5 }} />;
      })}
      <div style={{ position: "absolute", left: x(0) - 12, top: 656, color: C.muted, fontFamily: MONO, fontSize: 24, width: 24, textAlign: "center" }}>0</div>
      {points ? (
        <>
          <div style={{ position: "absolute", left: x(-5) - 12, top: 588, width: 24, height: 24, borderRadius: 12, background: answer ? C.amber : C.text }} />
          <div style={{ position: "absolute", left: x(-5) - 30, top: 656, width: 60, textAlign: "center", color: answer ? C.amber : C.text, fontFamily: MONO, fontSize: 28 }}>-5</div>
          <div style={{ position: "absolute", left: x(-2) - 12, top: 588, width: 24, height: 24, borderRadius: 12, background: answer ? C.amber : C.text }} />
          <div style={{ position: "absolute", left: x(-2) - 30, top: 656, width: 60, textAlign: "center", color: answer ? C.amber : C.text, fontFamily: MONO, fontSize: 28 }}>-2</div>
        </>
      ) : null}
      {link > 0 ? <div style={{ position: "absolute", left: x(-5), top: 560, width: (x(-2) - x(-5)) * link, height: 3, background: C.amber }} /> : null}
    </>
  );
};

const S7: React.FC = () => {
  const frame = useGlobalFrame();
  const cards = [
    { n: "①", t: "先规定正方向", at: A["先规定正方向"] },
    { n: "②", t: "0 是分界", at: A["零是分界"] },
    { n: "③", t: "数轴看位置", at: A["数轴看位置"] },
  ];
  const next = frame >= sec(A["我们学有理数的分类"]) - 2;
  const quiz = frame >= sec(A["从负二到三"]) - 2;
  const answerAt = beat("b7").end + T.hold;
  const answered = frame >= sec(answerAt);
  const x0 = 760, unit = 90;
  const x = (v: number) => x0 + v * unit;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <Title kicker="RECAP · 回收" title="第一课：三个工具" frame={frame} />
      <div style={{ display: "flex", gap: 26, marginTop: 30 }}>
        {cards.map((c) => (
          <Panel key={c.t} style={{ flex: 1, padding: 26, textAlign: "center", ...reveal(frame, c.at) }}>
            <div style={{ color: C.amber, fontSize: 26, marginBottom: 10 }}>{c.n}</div>
            <div style={{ color: C.text, fontSize: 34, fontWeight: 700 }}>{c.t}</div>
          </Panel>
        ))}
      </div>
      <div style={{ marginTop: 24, textAlign: "center", color: C.muted, fontSize: 26, opacity: next ? 1 : 0 }}>接下来：有理数的分类 → 相反数 → 绝对值</div>
      {quiz ? (
        <Panel style={{ marginTop: 26, padding: 24, ...fade(frame, sec(A["从负二到三"]) - 2, 8) }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ color: C.muted, fontSize: 20 }}>留一个问题</div>
              <div style={{ color: C.text, fontSize: 32, marginTop: 8 }}>数轴上，从 -2 到 3，要走几个单位长度？</div>
            </div>
            <div style={{ fontFamily: MONO, fontSize: 44, color: answered ? C.amber : C.text, fontWeight: 700, opacity: answered ? 1 : 0.7 + 0.3 * Math.sin(frame / 12) }}>
              {answered ? "= 5 个单位长度" : "= ? 格"}
            </div>
          </div>
          <div style={{ position: "relative", height: 120, marginTop: 16 }}>
            <div style={{ position: "absolute", left: 60, right: 60, top: 40, height: 3, background: C.muted }} />
            {Array.from({ length: 8 }).map((_, i) => {
              const v = i - 3;
              return <div key={"t" + i} style={{ position: "absolute", left: x(v) - 1, top: 60, width: 2, height: 14, background: C.muted, opacity: 0.5 }} />;
            })}
            {[-2, 3].map((v) => (
              <React.Fragment key={v}>
                <div style={{ position: "absolute", left: x(v) - 9, top: 32, width: 18, height: 18, borderRadius: 9, background: answered ? C.amber : C.text }} />
                <div style={{ position: "absolute", left: x(v) - 24, top: 80, width: 48, textAlign: "center", color: answered ? C.amber : C.text, fontFamily: MONO, fontSize: 24 }}>{v}</div>
              </React.Fragment>
            ))}
            {answered ? [0, 1, 2, 3, 4].map((i) => (
              <div key={"h" + i} style={{ position: "absolute", left: x(-2 + i) + 8, top: 12, width: unit - 16, height: 16, border: "2px solid " + C.amber, borderBottom: "none", borderRadius: "16px 16px 0 0", opacity: interpolate(frame, [sec(answerAt) + i * 4, sec(answerAt) + i * 4 + 6], [0, 1], CAP) }} />
            )) : null}
          </div>
        </Panel>
      ) : null}
    </AbsoluteFill>
  );
};


const CameraRig: React.FC<{ seed: number; children: React.ReactNode }> = ({ seed, children }) => {
  const f = useCurrentFrame();
  // 6.5s 一个镜头；硬切，制造 attention reset，不做无意义漂浮。
  const shot = Math.floor(f / (T.fps * 6.5));
  const shots = [[1.0, 0, 0], [1.03, -7, 3], [1.045, 6, -4], [1.015, -4, 2]];
  const s = shots[(shot + seed) % shots.length];
  const drift = Math.sin((f / T.fps) * 0.45) * 2;
  return <AbsoluteFill style={{ transform: "scale(" + s[0] + ") translate(" + (s[1] + drift) + "px," + (s[2] - drift) + "px)" }}>{children}</AbsoluteFill>;
};

const Wipe: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, 8], [0, 1], CAP);
  const o = interpolate(f, [0, 2, 8], [0, 0.8, 0], CAP);
  return <div style={{ position: "absolute", top: 0, bottom: 0, left: (p * 100) + "%", width: 4, background: C.amber, boxShadow: "0 0 24px " + C.amber, opacity: o }} />;
};

const ChapterBadge: React.FC<{ index: number }> = ({ index }) => {
  const f = useCurrentFrame();
  const labels = ["封面", "开场", "规定", "0", "数轴", "两个负数", "三个检查", "小结"];
  const o = interpolate(f, [0, 8], [0, 1], CAP);
  return (
    <div style={{ position: "absolute", top: 48, right: 210, display: "flex", alignItems: "center", gap: 8, opacity: o, transform: "translateX(" + interpolate(f, [0, 10], [10, 0], CAP) + "px)" }}>
      <span style={{ color: C.amber, fontFamily: MONO, fontSize: 15 }}>{String(index + 1).padStart(2, "0")}</span>
      <span style={{ width: 18, height: 1, background: C.muted, opacity: 0.6 }} />
      <span style={{ color: C.muted, fontSize: 16 }}>{labels[index] || ""}</span>
    </div>
  );
};

const ProgressBar: React.FC = () => {
  const f = useCurrentFrame();
  const p = Math.max(0, Math.min(1, f / T.frames));
  return <div style={{ position: "absolute", top: 0, left: 0, width: (p * 100) + "%", height: 2, background: C.amber, opacity: 0.45 }} />;
};


const ChapterCard: React.FC<{ index: number }> = ({ index }) => {
  const f = useCurrentFrame();
  if (index === 0 || f > 22) return null;
  const labels = ["封面", "开场", "规定", "0", "数轴", "两个负数", "三个检查", "小结"];
  const o = interpolate(f, [0, 4, 17, 22], [1, 1, 1, 0], CAP);
  const x = interpolate(f, [0, 8], [18, 0], CAP);
  return (
    <AbsoluteFill style={{ background: C.bg, opacity: o, zIndex: 20, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 28, transform: "translateX(" + x + "px)" }}>
        <div style={{ color: C.amber, fontFamily: MONO, fontSize: 116, lineHeight: 1, opacity: 0.9 }}>{String(index + 1).padStart(2, "0")}</div>
        <div style={{ width: 1, height: 96, background: C.muted, opacity: 0.5 }} />
        <div>
          <div style={{ color: C.muted, fontFamily: MONO, fontSize: 16, letterSpacing: 2 }}>CHAPTER</div>
          <div style={{ color: C.text, fontSize: 42, fontWeight: 800, marginTop: 8 }}>{labels[index]}</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const MGScene: React.FC<{ index: number; children: React.ReactNode }> = ({ index, children }) => (
  <>
    <CameraRig seed={index}>{children}</CameraRig>
    <Wipe />
    <ChapterBadge index={index} />
    <ChapterCard index={index} />
  </>
);

export const MathLesson: React.FC = () => {
  const frame = useCurrentFrame();
  const scenes = [
    { from: 0, to: sec(T.cover), node: <S0 /> },
    { from: sec(T.cover), to: sec(endOf("S1") + 0.05), node: <S1 /> },
    { from: sec(endOf("S1")), to: sec(endOf("S2") + 0.05), node: <S2 /> },
    { from: sec(endOf("S2")), to: sec(endOf("S3") + 0.05), node: <S3 /> },
    { from: sec(endOf("S3")), to: sec(endOf("S4") + 0.05), node: <S4 /> },
    { from: sec(endOf("S4")), to: sec(endOf("S5") + 0.05), node: <S5 /> },
    { from: sec(endOf("S5")), to: sec(endOf("S6") + 0.05), node: <S6 /> },
    { from: sec(endOf("S6")), to: T.frames, node: <S7 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice-full.wav")} />
      <Background />
      <ProgressBar />
      {frame >= sec(T.cover) ? <Header /> : null}
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>
          <SceneStart.Provider value={s.from}><MGScene index={i}>{s.node}</MGScene></SceneStart.Provider>
        </Sequence>
      ))}
      <Caption />
    </AbsoluteFill>
  );
};