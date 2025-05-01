import websocket
import json

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType
from pyspark.storage import StorageLevel

# Spark Session
spark = SparkSession.builder.appName("DualWebSocket").getOrCreate()

# Schemas (adapt to your data)
schema1 = StructType([...])  # Schema for endpoint1
schema2 = StructType([...])  # Schema for endpoint2


def automated_schema():
    # Sample JSON message (replace with actual data)
    sample_json = """
  {"name": "John", "age": 30, "city": "New York"}
  """

    # Infer schema
    schema = spark.read.json(sc.parallelize([sample_json])).schema

    # Apply schema to streaming DataFrame
    streaming_df = df.select(from_json(df.value, schema).alias("data")).select(
        "data.*"
    )


# WebSocket handling functions
def process_endpoint1(ws, message):
    data = json.loads(message)
    df = spark.createDataFrame([data], schema=schema1)
    df.persist(StorageLevel.MEMORY_ONLY)  # In-memory
    # Process df (e.g., write to console, further transformations)
    df.show()


def process_endpoint2(ws, message):
    data = json.loads(message)
    df = spark.createDataFrame([data], schema=schema2)
    df.persist(StorageLevel.DISK_ONLY)  # On-disk
    # Process df (e.g., save to file)
    df.write.parquet("data_from_endpoint2")


# WebSocket connections
def connect_to_endpoint(endpoint, handler):
    ws = websocket.WebSocketApp(
        endpoint,
        on_message=handler,
        on_error=lambda ws, msg: print(f"Error: {msg}"),
        on_close=lambda ws: print(f"Connection to {endpoint} closed"),
    )
    ws.run_forever()


# Start connections in separate threads (for parallel processing)
import threading

thread1 = threading.Thread(
    target=connect_to_endpoint, args=("wss://endpoint1", process_endpoint1)
)
thread2 = threading.Thread(
    target=connect_to_endpoint, args=("wss://endpoint2", process_endpoint2)
)

thread1.start()
thread2.start()
