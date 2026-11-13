export function jsonResponse(data: unknown, status = 200): Response {
    return new Response(status === 204 ? null : JSON.stringify(data), {
        status,
        headers: { "Content-Type": "application/json" },
    });
}

export function readJsonBody(init: RequestInit): Record<string, unknown> {
    if (typeof init.body !== "string") return {};
    try {
        return JSON.parse(init.body) as Record<string, unknown>;
    } catch {
        return {};
    }
}
