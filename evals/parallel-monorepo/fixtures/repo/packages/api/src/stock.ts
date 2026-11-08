import { db } from "./db";

export async function reserve(sku: string, qty: number) {
  const item = await db.get(sku);
  if (item.stock < qty) throw new Error("out of stock");
  await db.set(sku, { ...item, stock: item.stock - qty });
}
