import React from "react";
import { Composition } from "remotion";
import { KepuCompare } from "./Video";
import { Cover } from "./Cover";
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