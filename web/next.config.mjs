/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone", // imagen Cloud Run mínima (ADR-002)
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
