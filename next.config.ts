import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  async rewrites() {
    return [
      {
        source: "/Demand/Dev_npm_downloads/",
        destination: "/Demand/Dev_npm_downloads/index.html",
      },
    ];
  },
};

export default nextConfig;
