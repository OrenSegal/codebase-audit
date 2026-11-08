export function expiresAt(purchasedAt: Date, shelfLifeDays: number): Date {
  return new Date(purchasedAt.getTime() + shelfLifeDays * 86400 * 1000);
}

export function isExpired(expiry: Date, now: Date = new Date()): boolean {
  return expiry.toISOString().slice(0, 10) < now.toISOString().slice(0, 10);
}
