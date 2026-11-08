const ledger = require("./ledger");

function handleWebhook(rawBody, signature, secret) {
  const event = JSON.parse(rawBody);
  if (event.type === "checkout.completed") {
    ledger.add(event.userId, event.packSize);
  }
  return 200;
}

module.exports = { handleWebhook };
