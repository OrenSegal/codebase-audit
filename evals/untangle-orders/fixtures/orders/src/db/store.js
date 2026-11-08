const rows = new Map();

function get(id) {
  return rows.get(id);
}

function put(order) {
  rows.set(order.id, order);
}

function all() {
  return [...rows.values()];
}

function reset() {
  rows.clear();
}

module.exports = { get, put, all, reset };
