/** @type {import('next').NextConfig} */
const nextConfig = {
    // Enable standalone output for Docker
    output: 'standalone',

    // Environment variables
    env: {
        BACKEND_URL: process.env.BACKEND_URL,
    },

    // External packages for server components
    serverExternalPackages: ['@radix-ui'],
};

module.exports = nextConfig;
