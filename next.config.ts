import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/pokechess",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
