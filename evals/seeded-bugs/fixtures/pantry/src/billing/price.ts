export type LineItem = { name: string; price: number; quantity: number };

export function total(lines: LineItem[]): number {
  let sum = 0;
  for (const line of lines) {
    sum += Math.round(line.price * line.quantity * 100) / 100;
  }
  return sum;
}
