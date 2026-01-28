import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/py/:path*',
        destination: 'https://mu-d68e0144d9624aadb19f02da2628c6e5.ecs.us-east-2.on.aws/:path*',
      },
    ]
  },
};

export default nextConfig;
