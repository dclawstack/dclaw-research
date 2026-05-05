/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.TAURI_BUILD ? 'export' : 'standalone',
  distDir: process.env.TAURI_BUILD ? 'dist' : '.next',
  async rewrites() {
    if (process.env.TAURI_BUILD) return [];
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8098/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
