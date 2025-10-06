-- Orders table (envelope only)
CREATE TABLE IF NOT EXISTS orders (
  id            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_pasticoni  UUID,
  id_strategy   INTEGER,
  id_exchange   INTEGER,
  timestamp     TIMESTAMPTZ NOT NULL,
  timestamp_exchange TIMESTAMPTZ,
  pair          TEXT NOT NULL,
  side          TEXT NOT NULL,  -- BUY | SELL
  quote_qty     NUMERIC,
  quantity      NUMERIC,
  comments      TEXT,
  type          TEXT NOT NULL,  -- MARKET | LIMIT | ...
  status        TEXT NOT NULL,  -- NEW | ACCEPTED | REJECTED | PARTIALLY_FILLED | FILLED | CANCELLED | FROZEN
  timeInForce   TEXT NOT NULL,
  icb_delta     NUMERIC,
  icb_tip       NUMERIC,
  price         NUMERIC,
  trigger       NUMERIC,
  id_competitors NUMERIC,
  newOrderRespType TEXT NOT NULL,
  tracked_by text[]
);

-- Orders table (envelope only)
CREATE TABLE IF NOT EXISTS transactions (
  id        INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_orders INTEGER,
  filled_qty NUMERIC
);

-- Ensure privileges (safe to re-run)
GRANT SELECT ON TABLE orders TO app_reader;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE orders TO app_writer;

