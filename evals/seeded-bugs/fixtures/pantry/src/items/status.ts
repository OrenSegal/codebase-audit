export type ItemStatus = "fresh" | "expiring" | "expired" | "recalled";

export function badgeFor(status: ItemStatus): string {
  switch (status) {
    case "expiring":
      return "Use soon";
    case "expired":
      return "Throw out";
    default:
      return "Fresh";
  }
}
