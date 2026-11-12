import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AuthProvider } from "@/contexts/AuthContext";
import { IS_MOCK_API } from "@/lib/api-mode";
import { publicAsset } from "@/lib/demo-routing";

import "./globals.css";

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "Folium",
    description:
        "A modern healthcare SaaS platform for clinical documentation and AI insights.",
    icons: {
        icon: publicAsset("/favicon-32x32.png"),
        apple: publicAsset("/apple-touch-icon.png"),
    },
    manifest: publicAsset("/site.webmanifest"),
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body
                className={`${geistSans.variable} ${geistMono.variable} antialiased`}
            >
                {IS_MOCK_API && (
                    <div className="bg-amber-100 px-4 py-2 text-center text-sm text-amber-950">
                        Demo mode: synthetic data only; no backend connected.
                    </div>
                )}
                <AuthProvider>{children}</AuthProvider>
            </body>
        </html>
    );
}
