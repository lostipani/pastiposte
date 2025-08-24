import json, os, signal, sys, time
import pika
import psycopg

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
DB_URL   = os.environ.get("DATABASE_URL", "postgresql://app_writer:writer_password_change_me@postgres:5432/db_orders")


# replace the three constants with:
EXCHANGE_NAME = os.environ.get("EXCHANGE_NAME", "postal-service")
QUEUE_NAME    = os.environ.get("QUEUE_NAME", "postal-service.db")
ROUTING_KEY   = os.environ.get("ROUTING_KEY", "orders.new")

stop = False
def handle_sig(*_):  # graceful shutdown
    global stop
    stop = True

signal.signal(signal.SIGINT, handle_sig)
signal.signal(signal.SIGTERM, handle_sig)

def ensure_rabbitmq(ch):
    ch.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    ch.queue_declare(queue=QUEUE_NAME, durable=True)
    ch.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)
    ch.basic_qos(prefetch_count=100)

def wait_for_orders_table(conn, retries=30, delay=1.0):
    q = """select 1 from information_schema.tables
           where table_schema='public' and table_name='orders'"""
    for _ in range(retries):
        with conn.cursor() as cur:
            cur.execute(q)
            if cur.fetchone():
                return
        time.sleep(delay)
    raise RuntimeError("orders table not found; schema-migrator may have failed")

def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
          order_id    TEXT PRIMARY KEY,
          "timestamp" TIMESTAMPTZ NOT NULL,
          pair        TEXT NOT NULL,
          side        TEXT NOT NULL,
          qty         NUMERIC NOT NULL,
          type        TEXT NOT NULL,
          status      TEXT NOT NULL,
          strategy_id TEXT NULL,
          note        TEXT NULL,
          version     INT  NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_orders_pair_ts   ON orders (pair, "timestamp" DESC);
        CREATE INDEX IF NOT EXISTS idx_orders_status    ON orders (status);
        CREATE INDEX IF NOT EXISTS idx_orders_strategy  ON orders (strategy_id);
        GRANT SELECT ON TABLE orders TO app_reader;
        GRANT INSERT, UPDATE, DELETE ON TABLE orders TO app_writer;
        """)
    conn.commit()

def validate_envelope(o):
    required = ["order_id","timestamp","pair","side","qty","type","status","version"]
    for k in required:
        if k not in o:
            raise ValueError(f"missing field: {k}")

def insert_order(conn, o):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO orders (order_id, "timestamp", pair, side, qty, type, status, strategy_id, note, version)
            VALUES (%(order_id)s, %(timestamp)s, %(pair)s, %(side)s, %(qty)s, %(type)s, %(status)s, %(strategy_id)s, %(note)s, %(version)s)
            ON CONFLICT (order_id) DO NOTHING;
        """, {
            "order_id": o.get("order_id"),
            "timestamp": o.get("timestamp"),
            "pair": o.get("pair"),
            "side": o.get("side"),
            "qty": o.get("qty"),
            "type": o.get("type"),
            "status": o.get("status"),
            "strategy_id": o.get("strategy_id"),
            "note": o.get("note"),
            "version": o.get("version", 1),
        })
    conn.commit()

def main():
    # DB connect (+ keepalive)
    db = psycopg.connect(DB_URL, autocommit=False)
    wait_for_orders_table(db)


    # RabbitMQ connect
    params = pika.URLParameters(AMQP_URL)
    params.heartbeat = 30
    params.blocked_connection_timeout = 300
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    ensure_rabbitmq(channel)

    def on_message(ch, method, properties, body):
        try:
            o = json.loads(body.decode("utf-8"))
            validate_envelope(o)
            insert_order(db, o)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError:
            # bad message: ack to avoid infinite loop; log minimal info
            print("[WARN] bad JSON, acking", file=sys.stderr)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            # transient failure: requeue once by NACK
            print(f"[ERROR] {e}", file=sys.stderr)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(0.2)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message, auto_ack=False)
    print("[db-writer] up; consuming...")
    try:
        while not stop:
            connection.process_data_events(time_limit=1)
    finally:
        try:
            channel.stop_consuming()
        except: pass
        connection.close()
        db.close()
        print("[db-writer] down.")

if __name__ == "__main__":
    main()

