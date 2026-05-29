/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '100gb',
    },
  },
  async redirects() {
    return [
      {
        source: '/api-docs',
        destination: `${process.env.FASTAPI_URL ?? 'http://localhost:8000'}/docs`,
        permanent: false,
      },
    ]
  },
}

export default nextConfig
