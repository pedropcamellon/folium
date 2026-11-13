export function publicAsset(path: string): string {
    return path;
}

export function patientHref(id: string): string {
    return `/patients/${encodeURIComponent(id)}`;
}
