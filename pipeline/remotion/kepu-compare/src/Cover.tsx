import React from "react";
import { AbsoluteFill } from "remotion";
import { Background } from "./Video";

const FONT = '"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif';
const C = { text: "#F4F7FB", muted: "#8C97A8", tencent: "#2F7BFF", alibaba: "#FF6A00" };

export const Cover: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#080B12", fontFamily: FONT }}>
      <Background />
      <div style={{ position: "absolute", top: 48, left: 76, right: 76, display: "flex", justifyContent: "space-between", fontSize: 22, letterSpacing: 1 }}>
        <span style={{ color: C.text, fontWeight: 700 }}>AI 产品科普</span>
        <span style={{ color: C.muted }}>WorkBuddy × Qoder</span>
      </div>

      <div style={{ position: "absolute", top: 280, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "baseline", gap: 28 }}>
        <span style={{ color: C.tencent, fontSize: 132, fontWeight: 800 }}>WorkBuddy</span>
        <span style={{ color: C.muted, fontSize: 54, fontWeight: 600 }}>VS</span>
        <span style={{ color: C.alibaba, fontSize: 132, fontWeight: 800 }}>Qoder</span>
      </div>

      <div style={{ position: "absolute", top: 490, left: 0, right: 0, textAlign: "center", color: C.text, fontSize: 44, fontWeight: 500 }}>
        腾讯的办公 Agent × 阿里的编程 Agent
      </div>
      <div style={{ position: "absolute", top: 570, left: 0, right: 0, textAlign: "center", color: C.muted, fontSize: 28 }}>
        60 秒看懂：区别 · 原因 · 怎么选
      </div>

      <div style={{ position: "absolute", bottom: 70, left: 0, right: 0, textAlign: "center", color: "#5E6A7D", fontSize: 20, letterSpacing: 1 }}>
        Qwen TTS · Remotion · 2026-11
      </div>
    </AbsoluteFill>
  );
};
