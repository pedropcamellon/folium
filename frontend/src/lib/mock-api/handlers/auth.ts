import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

export const handleAuth: MockApiHandler = ({ path, method, state }) => {
    if (path === "/health") {
        return jsonResponse({ status: "ok", message: "Mock API is ready." });
    }

    if (path === "/auth/register" && method === "POST") {
        return jsonResponse(state.demoUser, 201);
    }
    if (path === "/auth/jwt/login" && method === "POST") {
        return jsonResponse({
            access_token: "demo-token",
            token_type: "bearer",
        });
    }
    if (path === "/auth/jwt/logout" && method === "POST") {
        return jsonResponse(null, 204);
    }
    if (path === "/users/me" && method === "GET") {
        return jsonResponse(state.demoUser);
    }

    return undefined;
};
