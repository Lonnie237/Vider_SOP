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
import timeline from "./timeline-v33.json";
import cues from "./cues-v33.json";
import wordsData from "./words-v33.json";
import { Background } from "./Video";

const T: any = timeline;
const CUES: any[] = cues as any[];
const WORDS: any = wordsData as any;
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

const beat = (id: string) => T.beats.find((x: any) => x.id === id);
const sec = (t: number) => Math.round(t * T.fps);
const SceneStart = React.createContext(0);
const phraseTime = (beatId: string, phrase: string) => {
  const b = beat(beatId);
  if (!b) return 0;
  const words = (WORDS[beatId] && WORDS[beatId].words) || [];
  const norm = words.map((x: any) => x.text || "").join("");
  const p = norm.indexOf(phrase.replace(/ /g, ""));
  if (p < 0) return b.start + 0.25;
  let acc = 0;
  for (const x of words) {
    const len = (x.text || "").length || 1;
    if (p < acc + len) {
      return b.start + x.begin_time / 1000 + (p - acc) / len * ((x.end_time - x.begin_time) / 1000);
    }
    acc += len;
  }
  return b.start + 0.25;
};
const Reveal: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; ghost?: boolean }> = ({ at, children, style, ghost }) => {
  const local = useCurrentFrame();
  const offset = React.useContext(SceneStart);
  const frame = local + offset;
  const fps = T.fps;
  const start = Math.round((at - 0.12) * fps);
  const o = interpolate(frame, [start, start + 9], [ghost ? 0.16 : 0, 1], CAP);
  const y = interpolate(frame, [start, start + 9], [ghost ? 0 : 16, 0], CAP);
  return <div style={{ opacity: o, transform: "translateY(" + y + "px)", ...style }}>{children}</div>;
};

const fade = (frame: number, delay: number, dur = 14) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [22, 0], CAP) + "px)",
});

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: C.panel,
      border: "1px solid " + C.line,
      borderRadius: 4,
      boxShadow: "0 22px 60px rgba(0,0,0,0.32)",
      ...style,
    }}
  >
    {children}
  </div>
);

const Badge: React.FC<{ letter: string; color: string; size?: number }> = ({ letter, color, size = 56 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: 12,
      background: color,
      color: "#fff",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: size * 0.5,
      fontWeight: 800,
      fontFamily: FONT,
      flexShrink: 0,
    }}
  >
    {letter}
  </div>
);

const Chip: React.FC<{ label: string; color: string; frame: number; delay: number }> = ({ label, color, frame, delay }) => (
  <div
    style={{
      ...fade(frame, delay, 10),
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      padding: "9px 15px",
      borderRadius: 3,
      border: "1px solid " + color + "55",
      background: color + "12",
      color: C.text,
      fontSize: 21,
      marginRight: 10,
      marginBottom: 10,
      fontFamily: FONT,
    }}
  >
    <span style={{ width: 6, height: 6, borderRadius: 3, background: color }} />
    {label}
  </div>
);

const highlight = (text: string) => {
  const parts = text.split(/(WorkBuddy|Qoder|CodeBuddy|QoderWork|AI 工作台)/g);
  return parts.map((p, i) => {
    if (p === "WorkBuddy" || p === "CodeBuddy") return <span key={i} style={{ color: C.tencent }}>{p}</span>;
    if (p === "Qoder" || p === "QoderWork") return <span key={i} style={{ color: C.alibaba }}>{p}</span>;
    if (p === "AI 工作台") return <span key={i} style={{ color: C.amber }}>{p}</span>;
    return <span key={i}>{p}</span>;
  });
};

const Header: React.FC<{ frame: number }> = ({ frame }) => {
  const current = T.beats.find((x: any) => frame >= sec(x.start) - 4 && frame <= sec(x.end) + 10);
  const labels: Record<string, string> = {
    hook: "01 / 08 · 开场",
    myth: "02 / 08 · 误解",
    define: "03 / 08 · 定位",
    context: "04 / 08 · 差异① 上下文",
    output: "05 / 08 · 差异② 产出",
    form: "06 / 08 · 差异③ 形态",
    why: "07 / 08 · 为什么是两款",
    choose: "08 / 08 · 怎么选",
    recommend: "08 / 08 · 建议",
    close: "08 / 08 · 收尾",
  };
  const label = current ? labels[current.section] || "" : "";
  return (
    <>
      <div style={{ position: "absolute", top: 0, left: 0, height: 3, width: interpolate(frame, [0, T.frames], [0, 1920], CAP), background: "linear-gradient(90deg, " + C.tencent + ", " + C.alibaba + ")" }} />
      <div style={{ position: "absolute", top: 46, left: 76, display: "flex", alignItems: "center", gap: 12, fontFamily: FONT }}>
        <span style={{ width: 4, height: 26, background: C.amber }} />
        <span style={{ color: C.muted, fontFamily: MONO, fontSize: 20, letterSpacing: 1 }}>{label}</span>
      </div>
      <div style={{ position: "absolute", top: 48, right: 76, fontFamily: FONT, fontSize: 20, color: C.muted }}>
        <span style={{ color: C.tencent, fontWeight: 700 }}>WorkBuddy</span>
        <span> × </span>
        <span style={{ color: C.alibaba, fontWeight: 700 }}>Qoder</span>
        <span style={{ color: C.amber, marginLeft: 14, fontFamily: MONO, fontSize: 15 }}>V3.3</span>
      </div>
    </>
  );
};

const FocusBar: React.FC<{ frame: number }> = ({ frame }) => {
  const b = T.beats.find((x: any) => frame >= sec(x.start) - 2 && frame <= sec(x.end) + 6);
  const text: Record<string, string> = {
    hook: "一份文档 · 一个 bug · 两条工作流",
    myth: "不是聊天框，是两条产品线",
    define: "AI 工作台 = 拆任务 + 调工具 + 交付",
    context: "办公上下文 ↔ 工程上下文",
    output: "文件 ↔ 代码 / PR",
    form: "桌面工作台 ↔ 开发者工作流",
    why: "编程 Agent + 办公 Agent",
    choose: "三个问题 · 一个方向",
    recommend: "先试一周，再决定付费",
    close: "工具是壳，工作流才是核心",
  };
  return (
    <div style={{ position: "absolute", left: 96, right: 96, top: 758, height: 58, display: "flex", alignItems: "center", borderTop: "1px solid " + C.line, borderBottom: "1px solid " + C.line }}>
      <span style={{ color: C.amber, fontFamily: MONO, fontSize: 15, letterSpacing: 1, width: 150 }}>FOCUS</span>
      <span style={{ color: C.muted, fontSize: 22 }}>{b ? text[b.section] : ""}</span>
    </div>
  );
};

const Caption: React.FC<{ frame: number }> = ({ frame }) => {
  const cue = CUES.find((c) => frame >= sec(c.start) && frame <= sec(c.end));
  if (!cue) return null;
  const local = frame - sec(cue.start);
  const dur = sec(cue.end) - sec(cue.start);
  const o = Math.min(1, Math.min(local / 4, (dur - local) / 4));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 50, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: o, padding: "13px 28px", borderRadius: 6, background: "rgba(0,0,0,0.72)", border: "1px solid rgba(255,255,255,0.12)", color: C.text, fontFamily: FONT, fontSize: 36, lineHeight: 1.2, whiteSpace: "nowrap", fontWeight: 500 }}>{cue.text}</div>
    </div>
  );
};

const SceneTitle: React.FC<{ kicker: string; title: string; frame: number; color?: string }> = ({ kicker, title, frame, color = C.amber }) => (
  <>
    <div style={{ ...fade(frame, 0, 10), display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
      <span style={{ width: 6, height: 20, background: color }} />
      <span style={{ fontFamily: MONO, color: C.muted, fontSize: 19, letterSpacing: 1 }}>{kicker}</span>
    </div>
    <div style={{ ...fade(frame, 2, 12), color: C.text, fontSize: 52, fontWeight: 800, letterSpacing: 0.5 }}>{title}</div>
  </>
);

const S1ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const left = spring({ frame, fps, config: { damping: 200 }, delay: 2 });
  const right = spring({ frame, fps, config: { damping: 200 }, delay: 8 });
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 132, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="COLD OPEN · 周一 9:00" title="如果只装一个 AI 工作台，你选谁？" frame={frame} />
      <div style={{ display: "flex", gap: 36, marginTop: 34 }}>
        <Panel style={{ flex: 1, padding: 28, opacity: left, transform: "translateX(" + (1 - left) * -40 + "px)" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 16 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
            <span style={{ color: C.muted, fontSize: 17, marginLeft: 10 }}>Q3 周报.doc</span>
          </div>
          <div style={{ color: C.text, fontSize: 30, fontWeight: 700, marginBottom: 18 }}>本周复盘</div>
          {[0.86, 0.74, 0.9, 0.62, 0.8].map((x, i) => <div key={i} style={{ height: 11, width: (x * 100) + "%", background: "rgba(255,255,255,0.13)", borderRadius: 3, marginBottom: 12 }} />)}
          <div style={{ marginTop: 22, color: C.tencent, fontSize: 20 }}>待办：写总结 · 贴数据 · 发老板</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 28, opacity: right, transform: "translateX(" + (1 - right) * 40 + "px)" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 16 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}
            <span style={{ color: C.muted, fontSize: 17, marginLeft: 10 }}>terminal — bug #1284</span>
          </div>
          <div style={{ fontFamily: MONO, fontSize: 20, color: C.coral, marginBottom: 10 }}>FAIL  checkout.test.ts</div>
          <div style={{ fontFamily: MONO, fontSize: 19, color: C.muted, lineHeight: 1.8 }}>
            Expected: 200<br />Received: 500<br />at checkout.ts:42<br />at runTest (node:test)
          </div>
          <div style={{ marginTop: 20, color: C.alibaba, fontSize: 20 }}>待办：复现 · 定位 · 提 PR</div>
        </Panel>
      </div>
      <div style={{ ...fade(frame, 30, 14), marginTop: 30, textAlign: "center", color: C.muted, fontSize: 28 }}>
        一份文档，一个 bug。两条完全不同的工作流。
      </div>
    </AbsoluteFill>
  );
};

const S2Myth: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...fade(frame, 0), display: "flex", gap: 80, alignItems: "center" }}>
        <div style={{ width: 540, padding: "26px 30px", borderRadius: 22, background: C.panel, border: "1px solid " + C.tencent + "66", opacity: fade(frame, 4).opacity }}>
          <div style={{ color: C.tencent, fontSize: 22, fontFamily: MONO, marginBottom: 10 }}>WorkBuddy</div>
          <div style={{ color: C.text, fontSize: 30 }}>“帮我写个周报。”</div>
        </div>
        <div style={{ color: C.amber, fontSize: 30, fontWeight: 700, fontFamily: MONO }}>两条路</div>
        <div style={{ width: 540, padding: "26px 30px", borderRadius: 22, background: C.panel, border: "1px solid " + C.alibaba + "66", opacity: fade(frame, 10).opacity }}>
          <div style={{ color: C.alibaba, fontSize: 22, fontFamily: MONO, marginBottom: 10 }}>Qoder</div>
          <div style={{ color: C.text, fontSize: 30 }}>“帮我修个 bug。”</div>
        </div>
      </div>
      <div style={{ ...fade(frame, 18), marginTop: 48, textAlign: "center" }}>
        <div style={{ color: C.muted, fontSize: 26, textDecoration: "line-through" }}>不是两个更聪明的聊天框</div>
        <div style={{ color: C.text, fontSize: 54, fontWeight: 800, marginTop: 18 }}>是两条产品线</div>
      </div>
      <div style={{ ...fade(frame, 30), marginTop: 18, color: C.muted, fontSize: 24 }}>一个从文档出发，一个从代码库出发。</div>
    </AbsoluteFill>
  );
};

const S3Define: React.FC = () => {
  const frame = useCurrentFrame();
  const parts = ["拆任务", "调工具", "交付结果"];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 132, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="DEFINITION · 一句话定义" title="都是 AI 工作台，区别在主场" frame={frame} />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12, marginTop: 28 }}>
        {parts.map((p, i) => (
          <React.Fragment key={p}>
            <div style={{ ...fade(frame, 4 + i * 6), padding: "12px 22px", border: "1px solid " + C.amber + "66", background: C.amber + "12", color: C.text, fontSize: 28, borderRadius: 3 }}>{p}</div>
            {i < parts.length - 1 ? <span style={{ color: C.muted, fontSize: 28 }}>+</span> : null}
          </React.Fragment>
        ))}
        <span style={{ color: C.muted, fontSize: 28, margin: "0 6px" }}>=</span>
        <div style={{ ...fade(frame, 22), padding: "12px 24px", background: C.text, color: C.bg, fontSize: 28, fontWeight: 800, borderRadius: 3 }}>AI 工作台</div>
      </div>
      <div style={{ display: "flex", gap: 32, marginTop: 34 }}>
        {[
          { name: "WorkBuddy", color: C.tencent, role: "腾讯 · 办公工作台", tags: ["文档", "表格", "会议", "调研"] },
          { name: "Qoder", color: C.alibaba, role: "阿里 · 编程工作台", tags: ["代码", "仓库", "Agent", "Repo Wiki"] },
        ].map((p, i) => (
          <Panel key={p.name} style={{ flex: 1, padding: 28, opacity: fade(frame, 28 + i * 6).opacity, transform: fade(frame, 28 + i * 6).transform }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <Badge letter={p.name[0]} color={p.color} />
              <div>
                <div style={{ color: C.text, fontSize: 36, fontWeight: 800 }}>{p.name}</div>
                <div style={{ color: C.muted, fontSize: 21, marginTop: 4 }}>{p.role}</div>
              </div>
            </div>
            <div style={{ marginTop: 18 }}>{p.tags.map((t) => <Chip key={t} label={t} color={p.color} frame={frame} delay={34 + i * 6} />)}</div>
          </Panel>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const S4Context: React.FC = () => {
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
  const col = (title: string, color: string, items: any[]) => (
    <Panel style={{ flex: 1, padding: 26, borderTop: "3px solid " + color }}>
      <div style={{ color, fontSize: 24, fontWeight: 700, marginBottom: 16 }}>{title}</div>
      {items.map((it) => (
        <Reveal key={it.t} ghost at={it.at}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "1px solid " + C.line, color: C.text, fontSize: 26 }}>
            <span style={{ width: 8, height: 8, background: color, borderRadius: 2 }} /><span style={{ color: C.text }}>{it.t}</span>
          </div>
        </Reveal>
      ))}
      <div style={{ marginTop: 16, color: C.muted, fontSize: 20 }}>{color === C.tencent ? "办公上下文" : "工程上下文"}</div>
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 132, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="差异 01 · 上下文" title="它们读的东西不一样" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 30 }}>
        {col("WorkBuddy 读什么", C.tencent, left)}
        {col("Qoder 读什么", C.alibaba, right)}
      </div>
      <div style={{ ...fade(frame, 38), textAlign: "center", marginTop: 24, color: C.muted, fontSize: 24 }}>上下文不同，能接的任务就不同。</div>
    </AbsoluteFill>
  );
};

const S5Output: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 132, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="差异 02 · 产出" title="最后交给你的东西不一样" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 30 }}>
        <Panel style={{ flex: 1, padding: 26 }}>
          <div style={{ color: C.tencent, fontSize: 24, fontWeight: 700, marginBottom: 14 }}>WorkBuddy → 文件</div>
          <div style={{ display: "flex", gap: 14 }}>
            {["DOCX", "XLSX", "PPTX"].map((x, i) => (
              <div key={x} style={{ ...fade(frame, 6 + i * 5), flex: 1, padding: "18px 12px", background: C.panel2, border: "1px solid " + C.tencent + "44", textAlign: "center", color: C.text, fontFamily: MONO, fontSize: 22 }}>{x}</div>
            ))}
          </div>
          <div style={{ ...fade(frame, 22), marginTop: 18, color: C.text, fontSize: 26 }}>报告 / 图表 / 待办清单</div>
          <div style={{ marginTop: 10, color: C.muted, fontSize: 20 }}>交付对象：老板、客户、同事</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 26 }}>
          <div style={{ color: C.alibaba, fontSize: 24, fontWeight: 700, marginBottom: 14 }}>Qoder → 代码与 PR</div>
          <div style={{ ...fade(frame, 8), background: "#0B111B", border: "1px solid " + C.alibaba + "44", padding: 16, fontFamily: MONO, fontSize: 19, lineHeight: 1.7 }}>
            <div><span style={{ color: C.coral }}>+</span> <span style={{ color: C.green }}>const fix = await agent.plan(bug)</span></div>
            <div><span style={{ color: C.coral }}>-</span> <span style={{ color: C.muted }}>if (!session) throw error</span></div>
            <div><span style={{ color: C.coral }}>+</span> <span style={{ color: C.text }}>if (!session) return redirect</span></div>
          </div>
          <div style={{ ...fade(frame, 24), marginTop: 18, color: C.text, fontSize: 26 }}>测试通过 · 提交记录 · PR</div>
          <div style={{ marginTop: 10, color: C.muted, fontSize: 20 }}>交付对象：代码库、线上系统</div>
        </Panel>
      </div>
      <div style={{ ...fade(frame, 36), textAlign: "center", marginTop: 22, color: C.muted, fontSize: 24 }}>
        一个交付「结果」，一个交付「可运行的系统」。
      </div>
    </AbsoluteFill>
  );
};

const S6Form: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 132, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="差异 03 · 形态" title="它长在你的工作流里" frame={frame} />
      <div style={{ display: "flex", gap: 34, marginTop: 30 }}>
        <Panel style={{ flex: 1, padding: 26 }}>
          <div style={{ color: C.tencent, fontSize: 24, fontWeight: 700 }}>WorkBuddy · 桌面工作台</div>
          <div style={{ ...fade(frame, 8), marginTop: 16, background: C.panel2, border: "1px solid " + C.line, padding: 18 }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>{["#FF5F57", "#FEBC2E", "#28C840"].map((x) => <span key={x} style={{ width: 10, height: 10, borderRadius: 5, background: x }} />)}</div>
            {["写周报", "做竞品调研", "整理会议纪要"].map((x, i) => (
              <div key={x} style={{ ...fade(frame, 12 + i * 4), color: C.text, fontSize: 22, padding: "8px 0", borderBottom: "1px solid " + C.line }}>{x}</div>
            ))}
          </div>
          <div style={{ ...fade(frame, 26), marginTop: 12, color: C.muted, fontSize: 20 }}>长在腾讯办公生态：文档 · 会议 · 企微</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 26 }}>
          <div style={{ color: C.alibaba, fontSize: 24, fontWeight: 700 }}>Qoder · 开发者工作流</div>
          <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
            {["IDE", "CLI", "Cloud Agent"].map((x, i) => (
              <div key={x} style={{ ...fade(frame, 10 + i * 6), flex: 1, padding: "18px 8px", background: C.panel2, border: "1px solid " + C.alibaba + "44", textAlign: "center", color: C.text, fontFamily: MONO, fontSize: 20 }}>{x}</div>
            ))}
          </div>
          <div style={{ ...fade(frame, 28), marginTop: 18, fontFamily: MONO, fontSize: 19, color: C.muted, lineHeight: 1.8 }}>
            $ qoder plan "fix checkout"<br />
            <span style={{ color: C.green }}>✓ repo indexed</span><br />
            <span style={{ color: C.alibaba }}>→ PR #1284 opened</span>
          </div>
          <div style={{ marginTop: 12, color: C.muted, fontSize: 20 }}>长在开发者工作流：仓库 · PR · 终端</div>
        </Panel>
      </div>
      <div style={{ ...fade(frame, 38), textAlign: "center", marginTop: 22, color: C.muted, fontSize: 24 }}>
        不是一个软件装在哪，而是它从哪一步开始接手。
      </div>
    </AbsoluteFill>
  );
};

const S7Why: React.FC = () => {
  const frame = useCurrentFrame();
  const column = (title: string, color: string, items: string[], start: number) => (
    <Panel style={{ flex: 1, padding: 24, borderTop: "3px solid " + color, opacity: fade(frame, start).opacity }}>
      <div style={{ color, fontSize: 25, fontWeight: 800, marginBottom: 14 }}>{title}</div>
      {items.map((it, i) => (
        <div key={it} style={{ ...fade(frame, start + 4 + i * 5), display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "1px solid " + C.line, color: C.text, fontSize: 24 }}>
          <span style={{ width: 24, height: 24, borderRadius: 12, border: "1px solid " + color + "88", color, fontSize: 14, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: MONO }}>{i + 1}</span>
          {it}
        </div>
      ))}
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 126, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="为什么 · 产品地图" title="为什么两家各推一款？" frame={frame} />
      <div style={{ display: "flex", gap: 28, marginTop: 28 }}>
        {column("腾讯", C.tencent, ["CodeBuddy：管编程", "WorkBuddy：管办公", "Buddy One：跨应用协同"], 4)}
        {column("阿里", C.alibaba, ["Qoder：管代码与开发", "QoderWork：管办公", "云 + 开发者生态"], 8)}
      </div>
      <div style={{ ...fade(frame, 30), marginTop: 26, textAlign: "center" }}>
        <div style={{ color: C.text, fontSize: 38, fontWeight: 800 }}>不是重复造轮子，是同一能力的两条产品线。</div>
        <div style={{ color: C.muted, fontSize: 23, marginTop: 10 }}>编程 Agent 与办公 Agent，各自长在自家生态里。</div>
      </div>
    </AbsoluteFill>
  );
};

const S8Choose: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = [
    { q: "你每天打开的是？", a: "文档 / 表格 / 会议", b: "IDE / 终端 / 仓库" },
    { q: "产出交给谁？", a: "老板 / 客户 / 同事", b: "代码库 / 线上系统" },
    { q: "你已经在用？", a: "腾讯文档 / 企微", b: "阿里云 / 开发者工具" },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 126, paddingLeft: 96, paddingRight: 96 }}>
      <SceneTitle kicker="怎么选 · 三个问题" title="先回答三个问题，再选工具" frame={frame} />
      <div style={{ marginTop: 26 }}>
        {rows.map((r, i) => (
          <div key={r.q} style={{ ...fade(frame, 4 + i * 8), display: "flex", alignItems: "center", gap: 18, marginBottom: 18 }}>
            <div style={{ width: 300, color: C.muted, fontSize: 24 }}>{r.q}</div>
            <div style={{ flex: 1, display: "flex", gap: 14 }}>
              <div style={{ flex: 1, padding: "13px 18px", border: "1px solid " + C.tencent + "66", background: C.tencent + "12", color: C.text, fontSize: 24 }}>
                <span style={{ color: C.tencent, fontWeight: 700 }}>WorkBuddy</span> · {r.a}
              </div>
              <div style={{ flex: 1, padding: "13px 18px", border: "1px solid " + C.alibaba + "66", background: C.alibaba + "12", color: C.text, fontSize: 24 }}>
                <span style={{ color: C.alibaba, fontWeight: 700 }}>Qoder</span> · {r.b}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div style={{ ...fade(frame, 34), marginTop: 14, color: C.muted, fontSize: 23 }}>
        三个问题里，两个以上落在同一边，答案就很清楚了。
      </div>
    </AbsoluteFill>
  );
};

const S9Recommend: React.FC = () => {
  const frame = useCurrentFrame();
  const cards = [
    { title: "办公为主", product: "WorkBuddy", color: C.tencent, note: "文档、表格、会议、调研" },
    { title: "开发为主", product: "Qoder", color: C.alibaba, note: "代码、仓库、PR、终端" },
    { title: "两个都干", product: "各试一周", color: C.green, note: "先用免费版，再决定付费" },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 150, paddingLeft: 96, paddingRight: 96 }}>
      <div style={{ ...fade(frame, 0), textAlign: "center", color: C.text, fontSize: 50, fontWeight: 800 }}>一句话建议</div>
      <div style={{ display: "flex", gap: 26, marginTop: 34 }}>
        {cards.map((c, i) => (
          <Panel key={c.title} style={{ flex: 1, padding: 24, opacity: fade(frame, 6 + i * 6).opacity, borderTop: "3px solid " + c.color }}>
            <div style={{ color: c.color, fontSize: 21, fontWeight: 700 }}>{c.title}</div>
            <div style={{ color: C.text, fontSize: 34, fontWeight: 800, marginTop: 8 }}>{c.product}</div>
            <div style={{ color: C.muted, fontSize: 20, marginTop: 10 }}>{c.note}</div>
          </Panel>
        ))}
      </div>
      <div style={{ ...fade(frame, 30), marginTop: 30, textAlign: "center", color: C.muted, fontSize: 24 }}>
        别急着为「全能」付费。先用一周，看它能不能接住你的真实任务。
      </div>
    </AbsoluteFill>
  );
};

const S10Close: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...fade(frame, 0), color: C.muted, fontSize: 26, letterSpacing: 2 }}>最后一句</div>
      <div style={{ ...fade(frame, 6), color: C.text, fontSize: 74, fontWeight: 800, marginTop: 18 }}>工具是壳</div>
      <div style={{ ...fade(frame, 16), color: C.amber, fontSize: 58, fontWeight: 800, marginTop: 10 }}>工作流才是核心</div>
      <div style={{ ...fade(frame, 30), color: C.muted, fontSize: 24, marginTop: 28 }}>价格和功能会变，商用前看官网与合规要求。</div>
      <div style={{ ...fade(frame, 40), color: C.text, fontSize: 32, marginTop: 34 }}>你每天的工作，更像哪一边？</div>
    </AbsoluteFill>
  );
};

export const KepuV33: React.FC = () => {
  const frame = useCurrentFrame();
  const b01 = beat("b01");
  const b02 = beat("b02");
  const b03 = beat("b03");
  const b04 = beat("b04");
  const b05 = beat("b05");
  const b06 = beat("b06");
  const b07 = beat("b07");
  const b08 = beat("b08");
  const b09 = beat("b09");

  const scenes = [
    { from: 0, to: sec(b01.end + 0.1), node: <S1ColdOpen /> },
    { from: sec(b01.end + 0.1), to: sec(b02.end + 0.1), node: <S2Myth /> },
    { from: sec(b02.end + 0.1), to: sec(b03.end + 0.1), node: <S3Define /> },
    { from: sec(b03.end + 0.1), to: sec(b04.end + 0.1), node: <S4Context /> },
    { from: sec(b04.end + 0.1), to: sec(b05.end + 0.1), node: <S5Output /> },
    { from: sec(b05.end + 0.1), to: sec(b06.end + 0.1), node: <S6Form /> },
    { from: sec(b06.end + 0.1), to: sec(b07.end + 0.1), node: <S7Why /> },
    { from: sec(b07.end + 0.1), to: sec(b08.end + 0.1), node: <S8Choose /> },
    { from: sec(b08.end + 0.1), to: sec(b09.end + 0.1), node: <S9Recommend /> },
    { from: sec(b09.end + 0.1), to: sec(T.duration), node: <S10Close /> },
  ];

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice-v33.wav")} />
      <Background />
      <Header frame={frame} />
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>
          <SceneStart.Provider value={s.from}>{s.node}</SceneStart.Provider>
        </Sequence>
      ))}
      <FocusBar frame={frame} />
      <Caption frame={frame} />
    </AbsoluteFill>
  );
};