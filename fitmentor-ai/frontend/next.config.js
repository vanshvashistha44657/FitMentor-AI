/** @type {import('next').NextConfig} */
const repoName = "FitMentor-AI";
const isProd = process.env.NODE_ENV === "production";

const nextConfig = {
  reactStrictMode: true,
  output: "export",
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: "https", hostname: "*.s3.amazonaws.com" },
      { protocol: "https", hostname: "res.cloudinary.com" },
    ],
  },
  basePath: isProd ? `/${repoName}` : "",
  assetPrefix: isProd ? `/${repoName}/` : "",
};

module.exports = nextConfig;
