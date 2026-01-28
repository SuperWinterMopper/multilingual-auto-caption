import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/py/:path*',
        // Use environment variable BACKEND_URL if available, otherwise fallback to the AWS ECS URL
        destination: process.env.BACKEND_URL 
          ? `${process.env.BACKEND_URL}/:path*` 
          : 'https://mu-d68e0144d9624aadb19f02da2628c6e5.ecs.us-east-2.on.aws/:path*',
      },
    ]
  },
};

export default nextConfig;
