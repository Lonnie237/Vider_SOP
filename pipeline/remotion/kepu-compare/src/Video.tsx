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
import timeline from "./timeline.json";

const T: any = timeline;
const C = {
  bg: "#080B12",
  panel: "#101724",
  panel2: "#0C121D",
  line: "rgba(255,255,255,0.09)",
  text: "#F4F7FB",
  muted: "#8C97A8",
  tencent: "#2F7BFF",
  alibaba: "#FF6A00",
  green: "#3DDC97",
  yellow: "#FFD166",
};
const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const CAP = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const beat = (id: string) => T.beats.find((x: any) => x.id === id);
const sec = (t: number) => Math.round(t * T.fps);

const fade = (frame: number, delay: number, dur = 10) => ({
  opacity: interpolate(frame, [delay, delay + dur], [0, 1], CAP),
  transform: "translateY(" + interpolate(frame, [delay, delay + dur], [26, 0], CAP) + "px)",
});

const Chip: React.FC<{ label: string; color: string; dim?: boolean }> = ({ label, color, dim }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      padding: "10px 16px",
      borderRadius: 999,
      border: "1px solid " + color + (dim ? "55" : "88"),
      background: color + (dim ? "12" : "1C"),
      color: dim ? C.muted : C.text,
      fontSize: 22,
      fontWeight: 500,
      marginRight: 10,
      marginBottom: 10,
    }}
  >
    <span style={{ width: 8, height: 8, borderRadius: 4, background: color }} />
    {label}
  </div>
);

const Panel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: C.panel,
      border: "1px solid " + C.line,
      borderRadius: 24,
      boxShadow: "0 24px 70px rgba(0,0,0,0.35)",
      ...style,
    }}
  >
    {children}
  </div>
);

const LogoBadge: React.FC<{ letter: string; color: string }> = ({ letter, color }) => (
  <div
    style={{
      width: 64,
      height: 64,
      borderRadius: 18,
      background: color,
      color: "#fff",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: 34,
      fontWeight: 800,
      fontFamily: FONT,
    }}
  >
    {letter}
  </div>
);

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 18;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(900px 600px at 12% 18%, rgba(47,123,255,0.16), transparent 65%)," +
            "radial-gradient(900px 600px at 88% 82%, rgba(255,106,0,0.14), transparent 65%)",
          transform: "translate(" + drift + "px, " + drift * 0.5 + "px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px)," +
            "linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
          backgroundSize: "96px 96px",
        }}
      />
      {[120, 420, 760, 1040].map((x, i) => (
        <div
          key={x}
          style={{
            position: "absolute",
            left: x,
            top: 120 + i * 190 + Math.sin((frame + i * 40) / 70) * 10,
            width: 4,
            height: 4,
            borderRadius: 2,
            background: "rgba(255,255,255,0.25)",
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

const Header: React.FC<{ frame: number }> = ({ frame }) => {
  const current = T.beats.find((x: any) => frame >= sec(x.start) - 4 && frame <= sec(x.end) + 8);
  const labels: Record<string, string> = {
    hook: "00 · 开场",
    define: "01 · 一句话定位",
    workbuddy: "02 · WorkBuddy",
    qoder: "03 · Qoder",
    why: "04 · 为什么是两款",
    choose: "05 · 普通人怎么选",
    caution: "05 · 注意",
    cta: "06 · 结尾",
  };
  const label = current ? labels[current.section] || "" : "";
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          height: 4,
          width: interpolate(frame, [0, T.frames], [0, 1920], CAP),
          background: "linear-gradient(90deg, " + C.tencent + ", " + C.alibaba + ")",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 44,
          left: 72,
          right: 72,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          color: C.muted,
          fontFamily: FONT,
          fontSize: 20,
          letterSpacing: 1,
        }}
      >
        <div style={{ display: "flex", gap: 22, alignItems: "center" }}>
          <span style={{ color: C.text, fontWeight: 700 }}>AI 产品科普</span>
          <span style={{ opacity: 0.7 }}>{label}</span>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span style={{ color: C.tencent, fontWeight: 700 }}>WorkBuddy</span>
          <span>×</span>
          <span style={{ color: C.alibaba, fontWeight: 700 }}>Qoder</span>
        </div>
      </div>
    </>
  );
};

const Captions: React.FC<{ frame: number }> = ({ frame }) => {
  const current = T.beats.find((x: any) => frame >= sec(x.start) && frame <= sec(x.end));
  if (!current) return null;
  if (current.section === "cta") return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 58,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          maxWidth: 1720,
          padding: "16px 30px",
          borderRadius: 18,
          background: "rgba(0,0,0,0.62)",
          border: "1px solid rgba(255,255,255,0.12)",
          color: C.text,
          fontFamily: FONT,
          fontSize: 35,
          lineHeight: 1.45,
          textAlign: "center",
          letterSpacing: 0.5,
        }}
      >
        {current.text}
      </div>
    </div>
  );
};

const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s1 = spring({ frame, fps, config: { damping: 200 }, delay: 4 });
  const s2 = spring({ frame, fps, config: { damping: 200 }, delay: 14 });
  const s3 = spring({ frame, fps, config: { damping: 200 }, delay: 24 });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", fontFamily: FONT }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 26 }}>
        <div style={{ transform: "scale(" + (0.92 + s1 * 0.08) + ")", opacity: s1, color: C.tencent, fontSize: 118, fontWeight: 800 }}>
          WorkBuddy
        </div>
        <div style={{ opacity: s2, color: C.muted, fontSize: 52, fontWeight: 600 }}>VS</div>
        <div style={{ transform: "scale(" + (0.92 + s3 * 0.08) + ")", opacity: s3, color: C.alibaba, fontSize: 118, fontWeight: 800 }}>
          Qoder
        </div>
      </div>
      <div style={{ ...fade(frame, 34), marginTop: 34, color: C.text, fontSize: 40, fontWeight: 500 }}>
        腾讯的办公 Agent · 阿里的编程 Agent
      </div>
      <div style={{ ...fade(frame, 48), marginTop: 16, color: C.muted, fontSize: 26 }}>
        60 秒看懂两款 AI 工作台：区别、原因与选择
      </div>
    </AbsoluteFill>
  );
};

const DefineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const left = spring({ frame, fps, config: { damping: 200 }, delay: 0 });
  const right = spring({ frame, fps, config: { damping: 200 }, delay: 5 });
  const card = (color: string, letter: string, name: string, role: string, tags: string[], style: React.CSSProperties) => (
    <Panel style={{ width: 640, padding: 34, ...style }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <LogoBadge letter={letter} color={color} />
        <div>
          <div style={{ color: C.text, fontSize: 42, fontWeight: 800 }}>{name}</div>
          <div style={{ color: C.muted, fontSize: 23, marginTop: 6 }}>{role}</div>
        </div>
      </div>
      <div style={{ marginTop: 28 }}>{tags.map((t) => <Chip key={t} label={t} color={color} />)}</div>
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 150 }}>
      <div style={{ ...fade(frame, 0), textAlign: "center", color: C.text, fontSize: 54, fontWeight: 800 }}>
        一句话定位
      </div>
      <div style={{ display: "flex", justifyContent: "center", gap: 40, marginTop: 44 }}>
        <div style={{ opacity: left, transform: "translateX(" + (1 - left) * -40 + "px)" }}>
          {card(C.tencent, "W", "WorkBuddy", "腾讯 · 全场景 AI 办公工作台", ["办公", "文档", "会议", "调研"], {})}
        </div>
        <div style={{ opacity: right, transform: "translateX(" + (1 - right) * 40 + "px)" }}>
          {card(C.alibaba, "Q", "Qoder", "阿里 · AI 编程智能体工作台", ["代码", "Agent", "Repo Wiki", "云端"], {})}
        </div>
      </div>
      <div style={{ ...fade(frame, 20), textAlign: "center", color: C.muted, fontSize: 30, marginTop: 40 }}>
        同一个目标：让 Agent 替你干活；区别在「主场」不同。
      </div>
    </AbsoluteFill>
  );
};

const WorkBuddyScene: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = ["写文档：周报、方案、复盘", "做表格：数据整理与图表", "查资料：15 分钟深度调研", "开会：纪要、待办、跟进"];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 150, paddingLeft: 110, paddingRight: 110 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div style={{ width: 760 }}>
          <div style={{ ...fade(frame, 0), display: "flex", alignItems: "center", gap: 18 }}>
            <LogoBadge letter="W" color={C.tencent} />
            <div>
              <div style={{ color: C.text, fontSize: 58, fontWeight: 800 }}>WorkBuddy</div>
              <div style={{ color: C.muted, fontSize: 24, marginTop: 4 }}>腾讯 · 办公赛道的个人 Agent</div>
            </div>
          </div>
          <div style={{ marginTop: 34 }}>
            {rows.map((r, i) => (
              <div key={r} style={{ ...fade(frame, i * 5), display: "flex", alignItems: "center", gap: 16, marginBottom: 22 }}>
                <div style={{ width: 34, height: 34, borderRadius: 17, border: "2px solid " + C.tencent, color: C.tencent, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 700 }}>
                  ✓
                </div>
                <div style={{ color: C.text, fontSize: 30 }}>{r}</div>
              </div>
            ))}
          </div>
          <div style={{ ...fade(frame, 22), marginTop: 18 }}>
            {["腾讯文档", "企业微信", "腾讯会议", "腾讯网盘"].map((t) => <Chip key={t} label={t} color={C.tencent} />)}
          </div>
        </div>
        <Panel style={{ width: 720, padding: 30, opacity: fade(frame, 2).opacity, transform: fade(frame, 2).transform }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 18 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => <div key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />)}
            <div style={{ marginLeft: 12, color: C.muted, fontSize: 18 }}>季度复盘.docx</div>
          </div>
          <div style={{ color: C.text, fontSize: 24, fontWeight: 700, marginBottom: 18 }}>Q3 增长复盘</div>
          {[0.9, 0.72, 0.84, 0.6, 0.76].map((w, i) => (
            <div key={i} style={{ height: 12, width: (w * 100) + "%", borderRadius: 6, background: i === 1 ? C.tencent : "rgba(255,255,255,0.12)", marginBottom: 12 }} />
          ))}
          <div style={{ display: "flex", gap: 14, marginTop: 24 }}>
            {[42, 64, 52, 78, 58, 88].map((h, i) => (
              <div key={i} style={{ width: 52, height: h, borderRadius: 8, background: i > 3 ? C.tencent : "rgba(47,123,255,0.35)", alignSelf: "flex-end" }} />
            ))}
          </div>
          <div style={{ marginTop: 24, color: C.muted, fontSize: 18 }}>AI 已生成：摘要 / 图表 / 待办</div>
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

const QoderScene: React.FC = () => {
  const frame = useCurrentFrame();
  const lines = [
    [["#C792EA", "export"], ["#F4F7FB", " async function"], ["#82AAFF", " review"], ["#F4F7FB", "(pr) {"]],
    [["#546E7A", "  // Repo Wiki 提供项目上下文"], ["#F4F7FB", ""]],
    [["#F4F7FB", "  const ctx = "], ["#82AAFF", "await"], ["#F4F7FB", " repo.wiki()"]],
    [["#F4F7FB", "  "], ["#C792EA", "return"], ["#F4F7FB", " agent.plan(pr, ctx)"]],
    [["#F4F7FB", "}"]],
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 150, paddingLeft: 110, paddingRight: 110 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <Panel style={{ width: 900, padding: 26, background: "#0B111B", opacity: fade(frame, 0).opacity }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => <div key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />)}
            <div style={{ marginLeft: 14, color: C.muted, fontSize: 18 }}>review.ts — Qoder</div>
          </div>
          {lines.map((line, i) => (
            <div key={i} style={{ display: "flex", gap: 6, fontSize: 24, lineHeight: "42px", fontFamily: "Menlo, monospace" }}>
              <span style={{ color: "#3A4558", width: 32, textAlign: "right" }}>{i + 1}</span>
              {line.map(([color, text], j) => <span key={j} style={{ color }}>{text}</span>)}
            </div>
          ))}
          <div style={{ marginTop: 18, padding: "12px 16px", borderRadius: 12, background: "rgba(255,106,0,0.12)", border: "1px solid rgba(255,106,0,0.35)", color: "#FFB27A", fontSize: 19 }}>
            Agent 模式：读取项目 → 规划 → 改多个文件 → 跑测试
          </div>
        </Panel>
        <div style={{ width: 680 }}>
          <div style={{ ...fade(frame, 0), display: "flex", alignItems: "center", gap: 18 }}>
            <LogoBadge letter="Q" color={C.alibaba} />
            <div>
              <div style={{ color: C.text, fontSize: 58, fontWeight: 800 }}>Qoder</div>
              <div style={{ color: C.muted, fontSize: 24, marginTop: 4 }}>阿里 · 以编程智能体为核心</div>
            </div>
          </div>
          <div style={{ marginTop: 30 }}>
            {["代码补全 / 对话", "自主编程：多文件任务", "Repo Wiki 项目知识库", "Agent SDK / Cloud Agents"].map((t) => (
              <div key={t} style={{ ...fade(frame, 6), display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
                <div style={{ width: 10, height: 10, borderRadius: 5, background: C.alibaba }} />
                <div style={{ color: C.text, fontSize: 28 }}>{t}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const WhyScene: React.FC = () => {
  const frame = useCurrentFrame();
  const col = (title: string, color: string, items: string[], side: "left" | "right") => (
    <Panel style={{ width: 620, padding: 30, opacity: fade(frame, side === "left" ? 6 : 16).opacity }}>
      <div style={{ color, fontSize: 28, fontWeight: 800, marginBottom: 20 }}>{title}</div>
      {items.map((it, i) => (
        <div key={it} style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 16 }}>
          <div style={{ width: 30, height: 30, borderRadius: 15, background: color + "22", border: "1px solid " + color + "66", color, fontSize: 16, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
            {i + 1}
          </div>
          <div style={{ color: C.text, fontSize: 27 }}>{it}</div>
        </div>
      ))}
    </Panel>
  );
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 140 }}>
      <div style={{ ...fade(frame, 0), textAlign: "center", color: C.text, fontSize: 52, fontWeight: 800 }}>
        为什么两家各推一款？
      </div>
      <div style={{ ...fade(frame, 10), textAlign: "center", color: C.muted, fontSize: 26, marginTop: 10 }}>
        不是重复造轮子，而是把 Agent 放进各自的主场。
      </div>
      <div style={{ display: "flex", justifyContent: "center", gap: 60, marginTop: 40 }}>
        {col("腾讯", C.tencent, ["CodeBuddy：编程", "WorkBuddy：办公", "Buddy One：跨应用协同"], "left")}
        {col("阿里", C.alibaba, ["Qoder：代码与开发", "QoderWork：办公", "云 + 开发者生态"], "right")}
      </div>
      <div style={{ ...fade(frame, 18), textAlign: "center", color: C.muted, fontSize: 24, marginTop: 30 }}>
        编程 Agent 与办公 Agent，是同一能力的两条产品线
      </div>
    </AbsoluteFill>
  );
};

const ChooseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const rows = [
    { q: "每天产出？", a: "文档 / 表格 / 会议", b: "代码 / 技术任务", ca: C.tencent, cb: C.alibaba },
    { q: "在用什么生态？", a: "腾讯文档 / 企业微信", b: "阿里云 / 开发者工具", ca: C.tencent, cb: C.alibaba },
    { q: "预算不确定？", a: "先用免费版", b: "先试用 / 按需订阅", ca: C.green, cb: C.yellow },
  ];
  return (
    <AbsoluteFill style={{ fontFamily: FONT, paddingTop: 130, paddingLeft: 110, paddingRight: 110 }}>
      <div style={{ ...fade(frame, 0), color: C.text, fontSize: 50, fontWeight: 800 }}>普通人怎么选？</div>
      <div style={{ marginTop: 30 }}>
        {rows.map((r, i) => (
          <div key={r.q} style={{ ...fade(frame, i * 6), display: "flex", alignItems: "center", gap: 18, marginBottom: 22 }}>
            <div style={{ width: 300, color: C.muted, fontSize: 26 }}>{r.q}</div>
            <div style={{ flex: 1, display: "flex", gap: 18 }}>
              <div style={{ flex: 1, padding: "14px 20px", borderRadius: 14, background: r.ca + "14", border: "1px solid " + r.ca + "55", color: C.text, fontSize: 26 }}>
                <span style={{ color: r.ca, fontWeight: 700 }}>WorkBuddy</span> · {r.a}
              </div>
              <div style={{ flex: 1, padding: "14px 20px", borderRadius: 14, background: r.cb + "14", border: "1px solid " + r.cb + "55", color: C.text, fontSize: 26 }}>
                <span style={{ color: r.cb, fontWeight: 700 }}>Qoder</span> · {r.b}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div style={{ ...fade(frame, 22), display: "flex", gap: 20, marginTop: 26 }}>
        <Panel style={{ flex: 1, padding: 22, borderColor: C.tencent + "66" }}>
          <div style={{ color: C.tencent, fontSize: 22, fontWeight: 700 }}>办公为主</div>
          <div style={{ color: C.text, fontSize: 28, marginTop: 6 }}>WorkBuddy</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 22, borderColor: C.alibaba + "66" }}>
          <div style={{ color: C.alibaba, fontSize: 22, fontWeight: 700 }}>开发为主</div>
          <div style={{ color: C.text, fontSize: 28, marginTop: 6 }}>Qoder</div>
        </Panel>
        <Panel style={{ flex: 1, padding: 22, borderColor: C.green + "66" }}>
          <div style={{ color: C.green, fontSize: 22, fontWeight: 700 }}>两者都干</div>
          <div style={{ color: C.text, fontSize: 28, marginTop: 6 }}>分场景使用</div>
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily: FONT, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...fade(frame, 0), color: C.text, fontSize: 78, fontWeight: 800, textAlign: "center" }}>
        工具没有绝对好坏
      </div>
      <div style={{ ...fade(frame, 14), color: C.alibaba, fontSize: 62, fontWeight: 800, marginTop: 16, textAlign: "center" }}>
        能接进你工作流的，才是好工具
      </div>
      <div style={{ ...fade(frame, 30), color: C.muted, fontSize: 22, marginTop: 34 }}>
        信息截至 2026-11 · 功能与价格以官网为准
      </div>
    </AbsoluteFill>
  );
};

export const KepuCompare: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const b01 = beat("b01");
  const b02 = beat("b02");
  const b03 = beat("b03");
  const b04 = beat("b04");
  const b05 = beat("b05");
  const b06 = beat("b06");
  const b07 = beat("b07");
  const b09 = beat("b09");
  const b10 = beat("b10");

  const scenes = [
    { from: 0, to: sec(b01.end + 0.15), node: <HookScene /> },
    { from: sec(b01.end + 0.15), to: sec(b02.end + 0.1), node: <DefineScene /> },
    { from: sec(b02.end + 0.1), to: sec(b03.end + 0.1), node: <WorkBuddyScene /> },
    { from: sec(b03.end + 0.1), to: sec(b04.end + 0.1), node: <QoderScene /> },
    { from: sec(b04.end + 0.1), to: sec(b06.end + 0.1), node: <WhyScene /> },
    { from: sec(b06.end + 0.1), to: sec(b09.end + 0.1), node: <ChooseScene /> },
    { from: sec(b09.end + 0.1), to: sec(T.duration), node: <CTAScene /> },
  ];

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("voice.wav")} />
      <Background />
      <Header frame={frame} />
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)}>
          {s.node}
        </Sequence>
      ))}
      <Captions frame={frame} />
    </AbsoluteFill>
  );
};