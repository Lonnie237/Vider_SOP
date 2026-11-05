import React from "react";
import { Composition } from "remotion";
import { KepuCompare } from "./Video";
import { Cover } from "./Cover";
import { KepuCompareV2 } from "./VideoV2";
import { KepuV3Sample } from "./VideoV3Sample";
import timelineV3Sample from "./timeline-v3-sample.json";
import timelineV2 from "./timeline-v2.json";
import timeline from "./timeline.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition
      id="KepuCompare"
      component={KepuCompare}
      durationInFrames={timeline.frames}
      fps={timeline.fps}
      width={timeline.width}
      height={timeline.height}
    />
    <Composition
      id="KepuCompareV2"
      component={KepuCompareV2}
      durationInFrames={timelineV2.frames}
      fps={timelineV2.fps}
      width={timelineV2.width}
      height={timelineV2.height}
    />
    <Composition
      id="KepuV3Sample"
      component={KepuV3Sample}
      durationInFrames={timelineV3Sample.frames}
      fps={timelineV3Sample.fps}
      width={timelineV3Sample.width}
      height={timelineV3Sample.height}
    />
    <Composition
      id="KepuCover"
      component={Cover}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
    />
    </>
  );
};