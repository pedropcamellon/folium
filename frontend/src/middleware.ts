import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for client-side auth pattern
 * Only handles public route redirects - actual auth checked client-side
 */

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Public routes accessible without auth
    const publicRoutes = ["/", "/login", "/register", "/health"];
    const isPublicRoute = publicRoutes.includes(pathname);

    // Allow all requests through - ProtectedRoute handles auth client-side
    return NextResponse.next();
}

// Configure which routes use this middleware
export const config = {
    matcher: [
        /*
         * Match all request paths except:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - public assets
         */
        "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|_next).*)",
    ],
};
