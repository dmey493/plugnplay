import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit .next/standalone with only the traced runtime files so the Docker
  // image ships ~100MB of node_modules instead of all 1.1GB — Cloud Run cold
  // starts pull and boot the image, so size is latency.
  output: "standalone",
  outputFileTracingIncludes: {
    // sharp powers /_next/image in production; its native binaries live in
    // node_modules/@img/* (sharp 0.34+) and static tracing grabs only the
    // .node stub without the libvips libraries beside it — verified by a
    // standalone smoke test serving unoptimized PNGs. Include both trees.
    "/*": ["node_modules/sharp/**/*", "node_modules/@img/**/*"],
  },
  outputFileTracingExcludes: {
    // Only scripts/remove-bg.mjs (a local one-off) imports @imgly, but the
    // whole-project trace drags its 50MB ONNX runtime into standalone.
    "/*": ["node_modules/@imgly/**"],
  },
};

export default nextConfig;
