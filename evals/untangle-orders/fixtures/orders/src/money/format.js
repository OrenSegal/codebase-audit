function formatTotal(cents, forReport) {
  if (forReport) {
    return (cents / 100).toFixed(2);
  }
  return "$" + (cents / 100).toFixed(2);
}

module.exports = { formatTotal };
