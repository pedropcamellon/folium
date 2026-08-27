export const CHART_REVIEW_STATUS = {
    QUEUED: "queued",
    RUNNING: "running",
    COMPLETED: "completed",
    FAILED: "failed",
} as const;

export type ChartReviewStatus =
    (typeof CHART_REVIEW_STATUS)[keyof typeof CHART_REVIEW_STATUS];