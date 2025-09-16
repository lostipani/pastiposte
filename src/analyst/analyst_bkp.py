# analyst/order_on_minute.py
import os, time, json, ast, uuid
import pika

# ---- Inputs: where we listen for Binance messages ----
BROKER_HOST = os.getenv("BROKER_HOST", "rabbitmq")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE", "exchange")
BROKER_EXCHANGE_TYPE = os.getenv("BROKER_EXCHANGE_TYPE", "direct")
BROKER_ROUTING_KEY = os.getenv(
    "BROKER_ROUTING_KEY", "kline_1m"
)  # can be "trade, kline_1m, frankfurter"

# ---- Outputs: where we publish orders (matches db-writer defaults) ----
ORDERS_EXCHANGE = os.getenv("EXCHANGE_NAME", "postal-service")
ORDERS_ROUTING_KEY = os.getenv("ROUTING_KEY", "orders.new")


def wait_for_next_minute():
    now = time.time()
    next_minute = int(now // 60) * 60 + 60
    time.sleep(max(0, next_minute - now))


# analyst/order_on_minute.py


def _connect():
    import pika

    params = pika.ConnectionParameters(BROKER_HOST)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # --- INPUT exchange ('exchange'): make sure it exists.
    # If it's missing (after a clean RabbitMQ restart), CREATE it to match the listener.
    try:
        ch.exchange_declare(exchange=BROKER_EXCHANGE, passive=True)
    except pika.exceptions.ChannelClosedByBroker:
        ch = (
            conn.channel()
        )  # channel gets closed on passive miss → open a new one
        ch.exchange_declare(
            exchange=BROKER_EXCHANGE,
            exchange_type=BROKER_EXCHANGE_TYPE,  # usually "direct"
            durable=False,  # listener creates it NON-durable
        )

    # --- OUTPUT exchange ('postal-service'): don't change its settings.
    # It already exists (writer creates it). Just assert it's there.
    try:
        ch.exchange_declare(exchange=ORDERS_EXCHANGE, passive=True)
    except pika.exceptions.ChannelClosedByBroker:
        ch = conn.channel()
        raise RuntimeError(
            f"Orders exchange '{ORDERS_EXCHANGE}' not found. Start db-writer first."
        )

    return conn, ch


def _parse_payload(body: bytes):
    # listener sends str({'source':..., 'message': <json_or_dict>})
    text = body.decode("utf-8")
    try:
        outer = json.loads(text)
    except json.JSONDecodeError:
        outer = ast.literal_eval(text)
    msg = outer.get("message", outer)
    if isinstance(msg, str):
        try:
            msg = json.loads(msg)
        except json.JSONDecodeError:
            msg = ast.literal_eval(msg)
    kline = msg.get("k", msg)  # binance kline payload nests under "k"
    return kline, msg


def _symbol_from(kline, fallback="BTCUSDT"):
    return kline.get("s") or fallback


def _close_from(kline):
    c = kline.get("c") or kline.get("close")
    return float(c) if c is not None else None


def get_next_message(ch):
    # temp exclusive queue bound to first routing key (if comma-separated)
    q = ch.queue_declare(queue="", exclusive=True, auto_delete=True)
    qname = q.method.queue
    rk = [r.strip() for r in BROKER_ROUTING_KEY.split(",")][0]
    ch.queue_bind(exchange=BROKER_EXCHANGE, routing_key=rk, queue=qname)

    box = {}

    def _on_msg(ch0, method, props, body):
        box["body"] = body
        ch0.basic_cancel(consumer_tag="one")

    ch.basic_consume(
        queue=qname,
        on_message_callback=_on_msg,
        auto_ack=True,
        consumer_tag="one",
    )
    while "body" not in box:
        ch.connection.process_data_events(time_limit=1)
    try:
        ch.queue_unbind(exchange=BROKER_EXCHANGE, routing_key=rk, queue=qname)
    except Exception:
        pass
    return box["body"]


def build_order(kline, close_price, symbol):
    return {
        "order_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pair": symbol,
        "side": "BUY",
        "qty": 0.1,
        "type": "MARKET",
        "status": "NEW",
        "strategy_id": "minute-tick",
        "note": f"close={close_price}",
        "version": 1,
    }


def publish_order(ch, order):
    ch.basic_publish(
        exchange=ORDERS_EXCHANGE,
        routing_key=ORDERS_ROUTING_KEY,
        body=json.dumps(order).encode("utf-8"),
        properties=pika.BasicProperties(
            content_type="application/json", delivery_mode=2
        ),
    )


def main():
    print("[analyst/order_on_minute] starting...")
    conn, ch = _connect()
    try:
        while True:
            wait_for_next_minute()
            print(
                "[analyst] minute tick; waiting for next message on:",
                BROKER_ROUTING_KEY,
                flush=True,
            )
            body = get_next_message(ch)
            kline, _ = _parse_payload(body)
            symbol = _symbol_from(kline)
            close = _close_from(kline)
            order = build_order(kline, close, symbol or "BTCUSDT")
            print(json.dumps(order, indent=2))  # <-- you review this
            publish_order(ch, order)  # <-- then it’s sent
    finally:
        conn.close()


if __name__ == "__main__":
    main()
