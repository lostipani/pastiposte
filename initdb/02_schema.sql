-- Orders table (envelope only)
CREATE TABLE IF NOT EXISTS orders (
  order_id    TEXT PRIMARY KEY,
  "timestamp" TIMESTAMPTZ NOT NULL,
  pair        TEXT NOT NULL,
  side        TEXT NOT NULL,  -- BUY | SELL
  qty         NUMERIC NOT NULL,
  type        TEXT NOT NULL,  -- MARKET | LIMIT | ...
  status      TEXT NOT NULL,  -- NEW | ACCEPTED | REJECTED | PARTIALLY_FILLED | FILLED | CANCELLED | FROZEN
  strategy_id TEXT NULL,
  note        TEXT NULL,
  version     INT  NOT NULL DEFAULT 1
);

-- Idempotent indexes
CREATE INDEX IF NOT EXISTS idx_orders_pair_ts   ON orders (pair, "timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status    ON orders (status);
CREATE INDEX IF NOT EXISTS idx_orders_strategy  ON orders (strategy_id);

-- Ensure privileges (safe to re-run)
GRANT SELECT ON TABLE orders TO app_reader;
GRANT INSERT, UPDATE, DELETE ON TABLE orders TO app_writer;

