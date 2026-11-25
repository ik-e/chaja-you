// Candidate frontend binding for VIEWER, derived from AuthGrant.
// The pinned JSON Schema is authoritative for serialized data.
export type AuthGrant = {
  generation: number;
  viewer_grant: string;
  expires_at: string;
};
export type ViewerEvent = "ready" | "error" | "disconnected";
export type ViewerHandle = { dispose(): void };
export interface Viewer {
  mount(container: HTMLElement, grant: AuthGrant,
        onEvent: (event: ViewerEvent) => void): ViewerHandle;
}
// dispose detaches the UI only, never cancels/restarts an accepted job.
// Grant validation, same owner/generation and transport security are mandatory.
