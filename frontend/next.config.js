/** @type {import('next').NextConfig} */
const nextConfig = {
    // Standalone output supports Docker and Azure Static Web Apps hybrid hosting.
    output: "standalone",

    // Environment variables
    env: {
        BACKEND_URL: process.env.BACKEND_URL,
    },

    // Force Radix UI to use bundled React (fixes CJS/ESM interop)
    transpilePackages: ["@radix-ui"],
};

module.exports = nextConfig;
