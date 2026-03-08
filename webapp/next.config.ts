import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://ec2-3-233-219-49.compute-1.amazonaws.com:8000/api/v1/:path*", // AWS EC2 Backend
      },
    ];
  },
};

export default nextConfig;
