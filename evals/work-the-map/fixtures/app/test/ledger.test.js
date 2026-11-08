const test = require("node:test");
const assert = require("node:assert");
const ledger = require("../src/ledger");

test.beforeEach(() => ledger.reset());

test("adding credits raises the balance", () => {
  ledger.add("u1", 5);
  assert.strictEqual(ledger.balance("u1"), 5);
});
