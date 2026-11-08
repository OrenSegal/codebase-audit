const FREE_SCANS = 5;

export function isPro(): boolean {
  return localStorage.getItem("isPro") === "true";
}

export function scansLeft(): number {
  return Number(localStorage.getItem("scansLeft") ?? FREE_SCANS);
}

export function useScan(): boolean {
  if (isPro()) return true;
  let remaining = scansLeft();
  if (remaining <= 0) return false;
  remaining -= 1;
  localStorage.setItem("scansLeft", String(remaining));
  return true;
}
