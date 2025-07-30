from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, List

import pika

Value = Any


class Broker(ABC):
    """
    Abstract methods to be implemented:
        add
        get
        is_empty

    This base class is equipped with a factory method to instantiate the
    proper derived class depending on the chosen backend.

    Args
        backend: an instance of the Value container
    Raises
        BrokerNotImplementedError
    """

    def __init__(self, backend: Any):
        self.backend = backend

    def __str__(self) -> str:
        return str(self.backend)

    @staticmethod
    def factory(backend, **kwargs):
        if isinstance(backend, list):
            return BrokerList(backend)
        if isinstance(backend, Queue):
            return BrokerQueue(backend)
        elif isinstance(backend, str) and backend.lower() == "rabbitmq":
            return BrokerRabbitMQ(**kwargs)
        else:
            raise NotImplementedError

    @abstractmethod
    def add(self, value: Value, **kwargs):
        pass

    @abstractmethod
    def get(self, **kwargs) -> Value:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass


class BrokerList(Broker):

    def __init__(self, backend: List[Value]):
        super().__init__(backend)

    def add(self, value: Value, **kwargs):
        del kwargs
        self.backend.append(value)

    def get(self, **kwargs) -> Value:
        del kwargs
        return self.backend[-1]

    def is_empty(self) -> bool:
        return len(self.backend) == 0


class BrokerQueue(Broker):

    def __init__(self, backend: Queue):
        super().__init__(backend)

    def add(self, value: Value, **kwargs):
        del kwargs
        self.backend.put(value)

    def get(self, **kwargs) -> Value:
        del kwargs
        return self.backend.get()

    def is_empty(self) -> bool:
        return self.backend.empty()


class BrokerRabbitMQ(Broker):

    def __init__(self, **kwargs):
        super().__init__("rabbitmq")
        self.params = kwargs
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.params.get("host"))
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.params.get("exchange"),
            exchange_type=self.params.get("exchange_type"),
        )

    def add(self, value: Value):
        self.channel.basic_publish(
            exchange=self.params.get("exchange"),
            routing_key=self.params.get("routing_key"),
            body=value,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ),
        )

    def get(self, **kwargs) -> Value:
        for routing_key in (
            rkey.strip() for rkey in self.params["routing_key"].split(",")
        ):
            queue_name = f"{routing_key}_queue"
            self.channel.queue_declare(queue=queue_name, exclusive=True)
            self.channel.queue_bind(
                exchange=self.params.get("exchange"),
                queue=queue_name,
                routing_key=routing_key,
            )
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=kwargs.get("callback"),
                auto_ack=True,
            )
        self.channel.start_consuming()

    def is_empty(self) -> bool:
        queue = self.channel.queue_declare(
            queue=self.params.get("queue"), passive=True
        )
        return queue.method.message_count == 0
