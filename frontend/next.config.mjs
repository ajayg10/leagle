const nextConfig = {
  reactCompiler: true,
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://perseuskyogre-leagle-assistance.hf.space';
    return [
      {
        source: '/api/v1/neural/:path*',
        destination: `${backendUrl}/api/v1/neural/:path*`,
      },
    ];
  },
};

export default nextConfig;
