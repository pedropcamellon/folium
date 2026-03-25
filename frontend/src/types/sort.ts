export type SortDirection = "asc" | "desc";

export const commonListSortOptions = [
    "createdAt-desc",
    "createdAt-asc",
    "updatedAt-desc",
    "title-asc",
] as const;

export type CommonListSortOption = (typeof commonListSortOptions)[number];
