// Repro for MONEY-1 and STATE-1: goes red today, green once ticket 01 is fixed.
const test = require("node:test");
const assert = require("node:assert");
const crypto = require("node:crypto");
const ledger = require("../../src/ledger");
const { handleWebhook } = require("../../src/webhook");

const SECRET = "whsec_test";
const sign = (body) => crypto.createHmac("sha256", SECRET).update(body).digest("hex");
const body = JSON.stringify({ id: "evt_1", type: "checkout.completed", userId: "u1", packSize: 10 });

test.beforeEach(() => ledger.reset());

test("a forged signature grants nothing", () => {
  const status = handleWebhook(body, "forged", SECRET);
  assert.strictEqual(status, 400);
  assert.strictEqual(ledger.balance("u1"), 0);
});

test("a redelivered event grants credits once", () => {
  handleWebhook(body, sign(body), SECRET);
  handleWebhook(body, sign(body), SECRET);
  assert.strictEqual(ledger.balance("u1"), 10);
});
