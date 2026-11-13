import type { MockApiState } from "./state";

export interface MockApiRequest {
    url: URL;
    path: string;
    method: string;
    body: Record<string, unknown>;
    state: MockApiState;
}

export type MockApiHandler = (request: MockApiRequest) => Response | undefined;
