import React from "react";
import { AbsoluteFill, Audio, Composition, interpolate, staticFile, useCurrentFrame } from "remotion";
import timeline from "./timeline.json";
import cues from "./cues.json";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = { bg: "#101418", text: "#F2EFE6", muted: "#A8A49A", amber: "#F0A93B", red: "#FF6B61", blue: "#4D9FFF" };
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const sec = (t: number) => Math.round(t * T.fps);
const cue = (s: string) => CUES.find((c) => c.text === s) || CUES[0];

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = CUES.find((x) => f >= sec(x.start) && f <= sec(x.end));
  if (!c) return null;
  const local = f - sec(c.start); const dur = sec(c.end) - sec(c.start);
  const o = Math.min(1, Math.min(local / 3, (dur - local) / 3));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 52, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "12px 26px", borderRadius: 6, background: "rgba(0,0,0,0.68)", border: "1px solid rgba(242,239,230,0.12)", color: C.text, fontFamily: FONT, fontSize: 34, whiteSpace: "nowrap" }}>{c.text}</div>
    </div>
  );
};

const Background: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(242,239,230,0.04) 1px, transparent 1px),linear-gradient(90deg, rgba(242,239,230,0.04) 1px, transparent 1px)", backgroundSize: "96px 96px", transform: "translate(" + Math.sin(f / 140) * 5 + "px," + Math.cos(f / 160) * 4 + "px)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 360, background: "radial-gradient(900px 320px at 50% 100%, rgba(240,169,59,0.08), transparent 70%)" }} />
    </AbsoluteFill>
  );
};

const Title: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 56, left: 96, display: "flex", alignItems: "center", gap: 10 }}>
      <span style={{ width: 5, height: 22, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: "monospace", fontSize: 16, letterSpacing: 1 }}>S2 视觉原型 · 数轴</span>
    </div>
    <div style={{ position: "absolute", top: 96, left: 96, color: C.text, fontFamily: FONT, fontSize: 46, fontWeight: 800 }}>把温度放到数轴上</div>
  </>
);

export const Prototype: React.FC = () => {
  const f = useCurrentFrame();
  const verticalOut = interpolate(f, [sec(3.1), sec(3.8)], [1, 0], CAP);
  const draw = interpolate(f, [sec(3.4), sec(5.2)], [0, 1], CAP);
  const zeroOn = f >= sec(3.35) && draw > 0.6;
  const oneOn = f >= cue("负一在零左边一格").start * T.fps;
  const threeOn = f >= cue("负三在左边三格").start * T.fps;
  const leftRule = f >= cue("越往左，数越小").start * T.fps;
  const answer = f >= cue("所以，负三小于负一").start * T.fps;
  const x0 = 960, unit = 80;
  const pts = [
    { n: "0", x: x0, on: zeroOn, color: C.text },
    { n: "-1", x: x0 - unit, on: oneOn, color: C.blue },
    { n: "-3", x: x0 - 3 * unit, on: threeOn, color: C.red },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT }}>
      <Background />
      <Title />
      {f < sec(4.2) ? (
        <div style={{ position: "absolute", left: 760, top: 220, width: 400, height: 600, opacity: verticalOut }}>
          <div style={{ position: "absolute", left: 190, top: 0, width: 20, height: 520, border: "2px solid " + C.text, borderRadius: 10 }} />
          <div style={{ position: "absolute", left: 196, top: 330, width: 8, height: 190, background: C.red, borderRadius: 4 }} />
          <div style={{ position: "absolute", left: 170, top: 510, width: 60, height: 60, borderRadius: 30, background: C.red }} />
          {[["0℃", 150, C.text], ["-1℃", 250, C.blue], ["-3℃", 370, C.red]].map(([t, y, c]) => (
            <React.Fragment key={String(t)}>
              <div style={{ position: "absolute", left: 220, top: y as number, width: 90, height: 2, background: c as string }} />
              <div style={{ position: "absolute", left: 320, top: (y as number) - 18, color: c as string, fontSize: 30 }}>{t}</div>
            </React.Fragment>
          ))}
          <div style={{ position: "absolute", left: 40, top: 580, color: C.muted, fontSize: 24, whiteSpace: "nowrap" }}>先猜：哪个温度更低？</div>
        </div>
      ) : null}

      {f >= sec(3.3) ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 600 }}>
          <div style={{ position: "absolute", left: 420, top: 0, width: 1080 * draw, height: 4, background: C.text }} />
          {draw > 0.92 ? <div style={{ position: "absolute", left: 1490, top: -14, color: C.text, fontSize: 34 }}>→</div> : null}
          {pts.map((p) => p.on ? <div key={p.n} style={{ position: "absolute", left: p.x - 11, top: -11, width: 22, height: 22, borderRadius: 11, background: answer && p.n !== "0" ? C.amber : p.color }} /> : null)}
          {pts.map((p) => p.on ? <div key={p.n + "l"} style={{ position: "absolute", left: p.x - 24, top: 24, width: 48, textAlign: "center", color: answer && p.n !== "0" ? C.amber : p.color, fontFamily: "monospace", fontSize: 28 }}>{p.n}</div> : null)}
          {draw > 0.75 ? <div style={{ position: "absolute", left: 930, top: 60, color: C.muted, fontSize: 20 }}>原点</div> : null}
          {threeOn ? <div style={{ position: "absolute", left: 720, top: 90, width: 240, height: 24, borderTop: "2px dashed " + C.muted, borderLeft: "2px solid " + C.muted, borderRight: "2px solid " + C.muted }} /> : null}
          {threeOn ? <div style={{ position: "absolute", left: 800, top: 122, color: C.muted, fontSize: 20 }}>左边更小</div> : null}
          {leftRule ? <div style={{ position: "absolute", left: 500, top: -150, color: C.amber, fontSize: 28, opacity: interpolate(f, [cue("越往左，数越小").start * T.fps, cue("越往左，数越小").start * T.fps + 8], [0, 1], CAP) }}>← 越往左，数越小</div> : null}
          {answer ? <div style={{ position: "absolute", left: 640, top: -240, color: C.amber, fontFamily: "monospace", fontSize: 58, fontWeight: 800 }}>-3 &lt; -1</div> : null}
        </div>
      ) : null}
      <Caption />
      <Audio src={staticFile("voice.wav")} />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="S2Prototype" component={Prototype} durationInFrames={T.frames} fps={T.fps} width={T.width} height={T.height} />
);