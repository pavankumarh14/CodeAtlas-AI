import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The production UI is a static bundle served by FastAPI in the single Render service.
  output: "export",
  trailingSlash: true,
};

export default nextConfig;
