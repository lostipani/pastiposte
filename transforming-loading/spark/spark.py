import json

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType
from pyspark.storage import StorageLevel

spark = SparkSession.builder.appName("pastiposte").getOrCreate()
schema = StructType([...])


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
