import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "https://api.adhi.rootedai.co.in/api/v1/:path*", // AWS ALB (HTTPS)
      },
    ];
  },
};

export default nextConfig;
