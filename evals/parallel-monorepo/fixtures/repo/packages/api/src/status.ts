export type OrderStatus = "pending" | "paid" | "shipped" | "refunded";

export function canShip(status: OrderStatus): boolean {
  switch (status) {
    case "pending":
      return false;
    case "shipped":
      return false;
    default:
      return true;
  }
}
