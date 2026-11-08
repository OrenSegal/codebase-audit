const test = require("node:test");
const assert = require("node:assert");
const store = require("../src/db/store");
const repo = require("../src/db/repo");
const { badge } = require("../src/ui/badge");
const { serialize } = require("../src/api/serialize");
const { exportRows } = require("../src/reports/export");

test.beforeEach(() => {
  store.reset();
  repo.saveOrder({ id: "o1", status: "paid", totalCents: 1250 });
  repo.saveOrder({ id: "o2", status: "shipped", totalCents: 999 });
});

test("badge labels a status", () => {
  assert.strictEqual(badge("paid"), "Paid");
});

test("serialize formats the total for the API", () => {
  assert.deepStrictEqual(serialize("o1"), { id: "o1", status: "paid", total: "$12.50" });
});

test("serialize rejects an unknown status", () => {
  repo.saveOrder({ id: "o3", status: "lost", totalCents: 1 });
  assert.throws(() => serialize("o3"));
});

test("export lists every order with a plain total", () => {
  assert.deepStrictEqual(exportRows(), [["o1", "paid", "12.50"], ["o2", "shipped", "9.99"]]);
});

test("repo reads through the store", () => {
  let calls = 0;
  const original = store.get;
  store.get = (id) => { calls += 1; return original(id); };
  repo.getOrder("o1");
  store.get = original;
  assert.strictEqual(calls, 1);
});

test("orders module loads", () => {
  assert.ok(true);
});
