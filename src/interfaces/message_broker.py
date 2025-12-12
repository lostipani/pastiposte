import json
from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, List

import pika

Message = Any


class Broker(ABC):
    """
    Abstract methods to be implemented:
        add
        get
        is_empty

    This base class is equipped with a factory method to instantiate the
    proper derived class depending on the chosen backend.

    Args
        backend: an instance of the Message container
    Raises
        BrokerNotImplementedError
    """

    def __init__(self, backend: Any):
        self.backend = backend

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
    def add(self, Message: Message, **kwargs):
        pass

    @abstractmethod
    def get(self, **kwargs) -> Message:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass


class BrokerList(Broker):
    """
    A broker whose backend is a Python list
    """

    def __init__(self, backend: List[Message]):
        super().__init__(backend)

    def add(self, Message: Message, **kwargs):
        del kwargs
        self.backend.append(Message)

    def get(self, **kwargs) -> Message:
        del kwargs
        return self.backend[-1]

    def is_empty(self) -> bool:
        return len(self.backend) == 0


class BrokerQueue(Broker):
    """
    A broker whose backend is a Python Queue
    """

    def __init__(self, backend: Queue):
        super().__init__(backend)

    def add(self, Message: Message, **kwargs):
        del kwargs
        self.backend.put(Message)

    def get(self, **kwargs) -> Message:
        del kwargs
        return self.backend.get()

    def is_empty(self) -> bool:
        return self.backend.empty()


class BrokerRabbitMQ(Broker):
    """
    A broker whose backend is a RabbitMQ instance.

    Deps:
        - pika: python client for RabbitMQ
        - json: message serialization
    """

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

    def add(self, Message: Message, routing_key: str | None = None):
        self.channel.basic_publish(
            exchange=self.params.get("exchange"),
            routing_key=(
                routing_key
                if routing_key
                else self.params.get("routing_key_out")
            ),
            body=json.dumps(Message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ),
        )

    def get(self, **kwargs) -> Message:
        for routing_key in (
            rkey.strip() for rkey in self.params["routing_key_in"].split(",")
        ):
            # assign random name to this queue to stave off name conflicts
            result = self.channel.queue_declare(queue="", exclusive=True)
            self.channel.queue_bind(
                exchange=self.params.get("exchange"),
                queue=result.method.queue,
                routing_key=routing_key,
            )
            self.channel.basic_consume(
                queue=result.method.queue,
                on_message_callback=kwargs.get("callback"),
                auto_ack=True,
            )
        self.channel.start_consuming()

    def is_empty(self) -> bool:
        raise NotImplementedError
