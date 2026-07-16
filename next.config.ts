import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit .next/standalone with only the traced runtime files so the Docker
  // image ships ~100MB of node_modules instead of all 1.1GB — Cloud Run cold
  // starts pull and boot the image, so size is latency.
  output: "standalone",
  outputFileTracingIncludes: {
    // sharp powers /_next/image in production; its native binaries can be
    // missed by static tracing (see next.config output docs).
    "/*": ["node_modules/sharp/**/*"],
  },
};

export default nextConfig;
