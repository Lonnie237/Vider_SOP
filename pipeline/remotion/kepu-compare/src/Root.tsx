import React from "react";
import { Composition } from "remotion";
import { KepuCompare } from "./Video";
import timeline from "./timeline.json";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="KepuCompare"
      component={KepuCompare}
      durationInFrames={timeline.frames}
      fps={timeline.fps}
      width={timeline.width}
      height={timeline.height}
    />
  );
};
