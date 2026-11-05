import React from "react";
import { Composition } from "remotion";
import { MathSample } from "./MathSample";
import timeline from "./timeline.json";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="MathSample"
    component={MathSample}
    durationInFrames={timeline.frames}
    fps={timeline.fps}
    width={timeline.width}
    height={timeline.height}
  />
);
