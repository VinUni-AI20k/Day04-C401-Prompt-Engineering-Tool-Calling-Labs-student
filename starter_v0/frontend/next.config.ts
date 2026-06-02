import type { NextConfig } from "next";

const nextConfig = {
  allowedDevOrigins: ["172.16.8.189", "localhost:3000"],
} as NextConfig & { allowedDevOrigins: string[] };

export default nextConfig;
