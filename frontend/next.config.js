/** @type {import('next').NextConfig} */
const isStaticDemo = process.env.NEXT_PUBLIC_DEMO_STATIC === "true";

if (isStaticDemo && process.env.NEXT_PUBLIC_API_MODE !== "mock") {
    throw new Error("Static demo builds require NEXT_PUBLIC_API_MODE=mock");
}

const nextConfig = {
    // Enable standalone output for Docker
    output: isStaticDemo ? "export" : "standalone",
    ...(isStaticDemo && {
        basePath: process.env.NEXT_PUBLIC_BASE_PATH || "",
        trailingSlash: true,
        images: { unoptimized: true },
    }),

    // Environment variables
    env: {
        BACKEND_URL: process.env.BACKEND_URL,
    },

    // Force Radix UI to use bundled React (fixes CJS/ESM interop)
    transpilePackages: ["@radix-ui"],
};

module.exports = nextConfig;
