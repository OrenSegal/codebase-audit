const repo = require("../db/repo");
const { formatTotal } = require("../money/format");

const KNOWN = ["pending", "paid", "shipped"];

function exportRows() {
  return repo.listOrders().map((o) => [o.id, KNOWN.includes(o.status) ? o.status : "unknown", formatTotal(o.totalCents, true)]);
}

module.exports = { exportRows };
