import React from "react";
import { Composition } from "remotion";
import { MathSample } from "./MathSample";
import { MathLesson } from "./MathLesson";
import timeline from "./timeline.json";
import timelineFull from "./timeline-full.json";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="MathSample"
      component={MathSample}
      durationInFrames={timeline.frames}
      fps={timeline.fps}
      width={timeline.width}
      height={timeline.height}
    />
    <Composition
      id="MathLesson"
      component={MathLesson}
      durationInFrames={timelineFull.frames}
      fps={timelineFull.fps}
      width={timelineFull.width}
      height={timelineFull.height}
    />
  </>
);
