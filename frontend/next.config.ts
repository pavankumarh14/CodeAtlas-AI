import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  experimental: {
    cpus: 1,
    staticGenerationMaxConcurrency: 1,
    staticGenerationRetryCount: 3,
    prerenderEarlyExit: false,
  },
  reactStrictMode: true,
  staticPageGenerationTimeout: 180,
};

export default nextConfig;
