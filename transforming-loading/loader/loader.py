import time

from pyspark.sql import SparkSession
from pyspark.sql import types as T

from commons.logger import logger
from commons.configuration import get_sleep, get_spark_master_URL
from commons.broker import Broker
from commons.rabbitmq import broker


class Loader(object):

    def __init__(self, master_URL: str, broker: Broker, sleep: float):
        self.master = master_URL
        self.broker = broker
        self.sleep = sleep

    def action(self, data):
        """
        The loader takes the message and stores it in the pyspark dataframe
        """
        data = data["message"]
        newRow = self.spark.createDataFrame(data, schema=self.infer_schema())
        self.df = self.df.union(newRow)
        logger.info(self.df.show())

    def callback_fun(self, channel, method, properties, body):
        """
        RabbitMQ dependent callback function to deal with incoming message
        """
        del channel, method, properties
        self.action(body.decode("utf-8"))
        time.sleep(self.sleep)

    def setup_spark(self):
        """
        Close pending session, build a new session, create an empty dataframe.
        """
        SparkSession.builder.master(self.master).getOrCreate().stop()
        self.spark_session = SparkSession.builder.remote(
            self.master
        ).getOrCreate()
        self.df = self.spark.createDataFrame([], schema=self.infer_schema())

    def infer_schema(self):
        return T.StructType(
            [
                T.StructField("A", T.StringType()),
                T.StructField("B", T.StringType()),
                T.StructField("C", T.StringType()),
            ]
        )

    def run(self):
        """
        Run loader
        """
        self.setup_spark()
        self.broker.get(callback=self.callback_fun)


def main(broker: Broker) -> None:
    loader = Loader(get_spark_master_URL(), broker, get_sleep())
    loader.run()


if __name__ == "__main__":
    main(broker)
