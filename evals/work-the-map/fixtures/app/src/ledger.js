const balances = new Map();

function add(userId, amount) {
  balances.set(userId, balance(userId) + amount);
}

function spend(userId, amount) {
  balances.set(userId, balance(userId) - amount);
}

function balance(userId) {
  return balances.get(userId) || 0;
}

function reset() {
  balances.clear();
}

module.exports = { add, spend, balance, reset };
