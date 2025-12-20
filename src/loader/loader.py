"""Load to persistence DB"""

import json
from typing import Any, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from interfaces.message_broker import Broker
from interfaces.consumer import RabbitMQConsumer
from commons.configuration import Configuration
from commons.broker import broker
from models import ModelBase
from models.sql import StructuredData


class Loader(RabbitMQConsumer):

    def init_db(self, **kwargs):
        # for future reference:
        # you could move these at module's level scope to let more than one
        # class create the database and open sessions on the same engine
        db_engine = create_engine(self.kwargs["db_url"], **kwargs)
        ModelBase.metadata.create_all(db_engine)  # to remove for DB versioning
        self.session_maker = sessionmaker(db_engine)

    def _action(self, message: Dict[str, Any]) -> Any:
        message = json.loads(message)
        with self.session_maker() as session:
            data = message["response"]
            record = StructuredData(**data)
            session.add(record)
            session.commit()


def main(broker: Broker) -> None:
    config = Configuration()
    loader = Loader(broker, config["sleep"], db_url=config["db_url"])
    loader.init_db()
    loader.consume()


if __name__ == "__main__":
    main(broker)
