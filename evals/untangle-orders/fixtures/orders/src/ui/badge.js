const LABELS = {
  pending: "Pending",
  paid: "Paid",
  shipped: "Shipped",
  refunded: "Refunded",
};

function badge(status) {
  return LABELS[status] || "Unknown";
}

module.exports = { badge };
