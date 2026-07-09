"use client";

import dynamic from "next/dynamic";
import type { InteractiveImageComponent } from "@/lib/types";

/**
 * Dispatches to the right built-in interactive image component, lazy-loaded
 * so Three.js never lands in the SSR bundle. Each variant should be a
 * "use client" component and is dynamically imported with ssr: false.
 *
 * To add a new interactive image:
 *   1. Build the component in this folder (e.g. SphereVolume3D.tsx).
 *   2. Add an entry to the COMPONENTS map.
 *   3. Add the identifier to InteractiveImageComponent in lib/types.ts.
 */
const COMPONENTS: Record<
  InteractiveImageComponent,
  React.ComponentType<{ width?: number }>
> = {
  "rubiks-cube": dynamic(() => import("./RubiksCube3D"), {
    ssr: false,
    loading: () => (
      <div
        className="flex items-center justify-center text-xs text-pnp-gray-500"
        style={{ aspectRatio: "1 / 1" }}
      >
        Loading 3D…
      </div>
    ),
  }),
};

interface Props {
  component: InteractiveImageComponent;
  width?: number;
}

export default function InteractiveImage({ component, width }: Props) {
  const Comp = COMPONENTS[component];
  if (!Comp) return null;
  return <Comp width={width} />;
}
