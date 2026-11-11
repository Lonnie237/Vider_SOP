import React from "react";
import { Composition } from "remotion";
import { RealPromo } from "./RealPromo";
import { VerticalPromo } from "./VerticalPromo";
import timeline from "./timeline.json";
export const Root: React.FC = () => (
  <>
    <Composition id="CollectorPromoReal" component={RealPromo} durationInFrames={1220} fps={timeline.fps} width={timeline.width} height={timeline.height} />
    <Composition id="CollectorPromoVertical" component={VerticalPromo} durationInFrames={487} fps={30} width={1080} height={1920} />
  </>
);