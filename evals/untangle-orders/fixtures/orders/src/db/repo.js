const store = require("./store");

function getOrder(id) {
  return store.get(id);
}

function saveOrder(order) {
  return store.put(order);
}

function listOrders() {
  return store.all();
}

module.exports = { getOrder, saveOrder, listOrders };
