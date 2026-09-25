import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  ...(isProd ? { output: "export" } : {
    async rewrites() {
      return [
        {
          source: "/api/:path*",
          destination: "http://127.0.0.1:8000/api/:path*",
        },
      ];
    },
  }),
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
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
