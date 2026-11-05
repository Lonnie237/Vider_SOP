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
import { Background } from "./Video";

const T: any = timeline;
const CUES: any[] = cues as any[];
const C = {
  bg: "#0A0E17",
  panel: "#111826",
  panel2: "#0C121D",
  line: "rgba(255,255,255,0.09)",
  text: "#F4F7FB",
  muted: "#8C97A8",
  tencent: "#2F7BFF",
  alibaba: "#FF6A00",
  amber: "#F0A93B",
  green: "#3DDC97",
  coral: "#FF6B61",
};
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const MONO = '"JetBrains Mono","SFMono-Regular",Menlo,monospace';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const sec = (t: number) => Math.round(t * T.fps);
const beat = (id: string) => T.beats.find((x: any) => x.id === id);

const fade = (frame: number, delay: number, dur = 12) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [18, 0], CAP) + "px)",
});

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.panel, border: "1px solid " + C.line, borderRadius: 4, boxShadow: "0 22px 60px rgba(0,0,0,0.32)", ...style }}>{children}</div>
);

const Badge: React.FC<{ letter: string; color: string }> = ({ letter, color }) => (
  <div style={{ width: 52, height: 52, borderRadius: 10, background: color, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26, fontWeight: 800, flexShrink: 0 }}>{letter}</div>
);

const highlight = (text: string) => {
  const parts = text.split(/(WorkBuddy|Qoder|AI 工作台|CodeBuddy|QoderWork)/g);
  return parts.map((p, i) => {
    if (p === "WorkBuddy" || p === "CodeBuddy") return <span key={i} style={{ color: C.tencent }}>{p}</span>;
    if (p === "Qoder" || p === "QoderWork") return <span key={i} style={{ color: C.alibaba }}>{p}</span>;
    if (p === "AI 工作台") return <span key={i} style={{ color: C.amber }}>{p}</span>;
    return <span key={i}>{p}</span>;
  });
};

const Thread: React.FC<{ frame: number }> = ({ frame }) => {
  const w = 1728;
  const x = 96 + (interpolate(frame, [0, T.frames], [0, w], CAP) + Math.sin(frame / 28) * 6);
  const pulse = 0.55 + 0.45 * Math.sin(frame / 18);
  return (
    <div style={{ position: "absolute", left: 96, right: 96, top: 720, height: 24 }}>
      <div style={{ position: "absolute", top: 10, left: 0, right: 0, height: 2, background: "linear-gradient(90deg, rgba(47,123,255,0.15), rgba(240,169,59,0.55), rgba(255,106,0,0.15))" }} />
      <div style={{ position: "absolute", top: 6, left: x - 96, width: 10, height: 10, borderRadius: 5, background: C.amber, boxShadow: "0 0 18px " + C.amber, opacity: pulse }} />
    </div>
  );
};

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
        <span style={{ color: C.amber, marginLeft: 14, fontFamily: MONO, fontSize: 15 }}>V3 SAMPLE</span>
      </div>
    </>
  );
};

const CueCaption: React.FC<{ frame: number }> = ({ frame }) => {
  const cue = CUES.find((c) => frame >= sec(c.start) && frame <= sec(c.end));
  if (!cue) return null;
  const local = frame - sec(cue.start);
  const dur = sec(cue.end) - sec(cue.start);
  const o = Math.min(1, Math.min(local / 5, (dur - local) / 5));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 54, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "13px 30px", borderRadius: 6, background: "rgba(0,0,0,0.72)", border: "1px solid rgba(255,255,255,0.12)", color: C.text, fontFamily: FONT, fontSize: 38, lineHeight: 1.2, whiteSpace: "nowrap", fontWeight: 500 }}>
        {highlight(cue.text)}
      </div>
    </div>
  );
};

const SceneTitle: React.FC<{ kicker: string; title: string; frame: number; instant?: boolean }> = ({ kicker, title, frame, instant }) => (
  <>
    <div style={{ ...(instant ? {} : fade(frame, 0, 9)), display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
      <span style={{ width: 6, height: 20, background: C.amber }} />
      <span style={{ color: C.muted, fontFamily: MONO, fontSize: 18, letterSpacing: 1 }}>{kicker}</span>
    </div>
    <div style={{ ...(instant ? {} : fade(frame, 2, 12)), color: C.text, fontSize: 50, fontWeight: 800 }}>{title}</div>
  </>
);

const S1: React.FC = () => {
  const frame = useCurrentFrame();
  const float = Math.sin(frame / 24) * 2;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle instant kicker="COLD OPEN · 周一 9:00" title="如果只装一个 AI 工作台，你选谁？" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 30 }}>
        <Panel style={{ flex: 1, padding: 26, transform: "translateY(" + float + "px)", opacity: fade(frame, 2).opacity }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 14 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
            <span style={{ color: C.muted, fontSize: 16, marginLeft: 10 }}>Q3 周报.doc</span>
          </div>
          <div style={{ color: C.text, fontSize: 28, fontWeight: 700, marginBottom: 16 }}>本周复盘</div>
          {[0.86, 0.74, 0.9, 0.62, 0.8].map((x, i) => <div key={i} style={{ height: 10, width: (x * 100) + "%", background: "rgba(255,255,255,0.13)", borderRadius: 3, marginBottom: 11 }} />)}
          <div style={{ marginTop: 18, color: C.tencent, fontSize: 19 }}>待办：写总结 · 贴数据 · 发老板</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 26, transform: "translateY(" + (-float) + "px)", opacity: fade(frame, 6).opacity }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 14 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
            <span style={{ color: C.muted, fontSize: 16, marginLeft: 10 }}>terminal — bug #1284</span>
          </div>
          <div style={{ fontFamily: MONO, fontSize: 18, color: C.coral, marginBottom: 10 }}>FAIL checkout.test.ts</div>
          <div style={{ fontFamily: MONO, fontSize: 17, color: C.muted, lineHeight: 1.8 }}>
            Expected: 200<br />Received: 500<br />at checkout.ts:42<br />at runTest (node:test)
          </div>
          <div style={{ marginTop: 16, color: C.alibaba, fontSize: 19 }}>待办：复现 · 定位 · 提 PR</div>
        </Panel>
      </div>
      <div style={{ ...fade(frame, 24), marginTop: 24, textAlign: "center", color: C.muted, fontSize: 25 }}>
        一份文档，一个 bug。两条完全不同的工作流。
      </div>
    </AbsoluteFill>
  );
};

const S2: React.FC = () => {
  const frame = useCurrentFrame();
  const parts = ["拆任务", "调工具", "交付结果"];
  const float = Math.sin(frame / 22) * 2;
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="DEFINITION · 一句话定义" title="都是 AI 工作台，区别在主场" frame={frame} />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, marginTop: 24 }}>
        {parts.map((p, i) => (
          <React.Fragment key={p}>
            <div style={{ ...fade(frame, 3 + i * 5), padding: "10px 18px", border: "1px solid " + C.amber + "66", background: C.amber + "12", color: C.text, fontSize: 24, borderRadius: 3 }}>{p}</div>
            {i < parts.length - 1 ? <span style={{ color: C.muted, fontSize: 24 }}>+</span> : null}
          </React.Fragment>
        ))}
        <span style={{ color: C.muted, fontSize: 24, margin: "0 4px" }}>=</span>
        <div style={{ ...fade(frame, 18), padding: "10px 20px", background: C.text, color: C.bg, fontSize: 24, fontWeight: 800, borderRadius: 3 }}>AI 工作台</div>
      </div>
      <div style={{ display: "flex", gap: 28, marginTop: 28 }}>
        {[
          { name: "WorkBuddy", color: C.tencent, role: "腾讯 · 办公工作台", tags: ["文档", "表格", "会议", "调研"] },
          { name: "Qoder", color: C.alibaba, role: "阿里 · 编程工作台", tags: ["代码", "仓库", "Agent", "Repo Wiki"] },
        ].map((p, i) => (
          <Panel key={p.name} style={{ flex: 1, padding: 24, opacity: fade(frame, 22 + i * 5).opacity, transform: "translateY(" + float * (i === 0 ? 1 : -1) + "px)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <Badge letter={p.name[0]} color={p.color} />
              <div>
                <div style={{ color: C.text, fontSize: 32, fontWeight: 800 }}>{p.name}</div>
                <div style={{ color: C.muted, fontSize: 19, marginTop: 3 }}>{p.role}</div>
              </div>
            </div>
            <div style={{ marginTop: 16 }}>{p.tags.map((t) => <span key={t} style={{ display: "inline-block", padding: "7px 12px", marginRight: 8, marginBottom: 8, border: "1px solid " + p.color + "55", background: p.color + "12", color: C.text, fontSize: 18, borderRadius: 3 }}>{t}</span>)}</div>
          </Panel>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const S3: React.FC = () => {
  const frame = useCurrentFrame();
  const groups = [
    { title: "WorkBuddy 读什么", color: C.tencent, items: ["文档 / 表格", "会议纪要", "腾讯文档", "企业微信", "知识库"], hint: "办公上下文" },
    { title: "Qoder 读什么", color: C.alibaba, items: ["代码 / 仓库", "PR / 提交记录", "终端报错", "项目 Wiki", "依赖关系"], hint: "工程上下文" },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 128, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="差异 01 · 上下文" title="它们读的东西不一样" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 26 }}>
        {groups.map((g, i) => (
          <Panel key={g.title} style={{ flex: 1, padding: 24, borderTop: "3px solid " + g.color, opacity: fade(frame, 3 + i * 5).opacity }}>
            <div style={{ color: g.color, fontSize: 22, fontWeight: 700, marginBottom: 12 }}>{g.title}</div>
            {g.items.map((it, j) => (
              <div key={it} style={{ ...fade(frame, 8 + i * 4 + j * 3), display: "flex", alignItems: "center", gap: 10, padding: "9px 0", borderBottom: "1px solid " + C.line, color: C.text, fontSize: 23 }}>
                <span style={{ width: 7, height: 7, background: g.color, borderRadius: 2 }} />{it}
              </div>
            ))}
            <div style={{ marginTop: 12, color: C.muted, fontSize: 18 }}>{g.hint}</div>
          </Panel>
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const KepuV3Sample: React.FC = () => {
  const frame = useCurrentFrame();
  const b01 = beat("b01");
  const b03 = beat("b03");
  const b04 = beat("b04");
  const scenes = [
    { from: 0, to: sec(b01.end + 0.1), node: <S1 /> },
    { from: sec(b01.end - 0.2), to: sec(b03.end + 0.1), node: <S2 /> },
    { from: sec(b03.end - 0.2), to: sec(T.duration), node: <S3 /> },
  ];
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice-v3-sample.wav")} />
      <Background />
      <Thread frame={frame} />
      <Header frame={frame} />
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>{s.node}</Sequence>
      ))}
      <CueCaption frame={frame} />
    </AbsoluteFill>
  );
};