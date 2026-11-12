export const IS_STATIC_DEMO = process.env.NEXT_PUBLIC_DEMO_STATIC === "true";
export const BASE_PATH = IS_STATIC_DEMO ? process.env.NEXT_PUBLIC_BASE_PATH || "" : "";

export function publicAsset(path: string): string {
    return `${BASE_PATH}${path}`;
}

export function patientHref(id: string): string {
    return IS_STATIC_DEMO
        ? `/patients/demo/?id=${encodeURIComponent(id)}`
        : `/patients/${encodeURIComponent(id)}`;
}
