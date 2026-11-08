const repo = require("../db/repo");
const { formatTotal } = require("../money/format");

const STATUSES = ["pending", "paid", "shipped", "refunded"];

function serialize(id) {
  const order = repo.getOrder(id);
  if (!STATUSES.includes(order.status)) throw new Error("bad status " + order.status);
  return { id: order.id, status: order.status, total: formatTotal(order.totalCents, false) };
}

module.exports = { serialize };
