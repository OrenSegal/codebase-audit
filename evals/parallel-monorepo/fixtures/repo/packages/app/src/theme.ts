export type Theme = "light" | "dark" | "high-contrast";

export function background(theme: Theme): string {
  switch (theme) {
    case "dark":
      return "#000000";
    default:
      return "#ffffff";
  }
}
