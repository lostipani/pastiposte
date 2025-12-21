import random
import string
from typing import Any, Dict

TYPE_GENERATORS = {
    "int": lambda: random.randint(1, 1000),
    "char": lambda: random.choices(string.ascii_letters, k=1),
    "str": lambda: "".join(random.choices(string.ascii_letters, k=40)),
    "float_uni": lambda: random.uniform(0, 1000),
    "float_normal": lambda: random.gauss(0, 1),
    "bool": lambda: random.choice([True, False]),
}


def _format(data: Any) -> Dict[str, Any]:
    return {"response": data}


def gauss_list(size: int):
    return _format([TYPE_GENERATORS["float_normal"]() for _ in range(size)])


def char_scalar():
    return _format(TYPE_GENERATORS["char"]())


def structured_data():
    from models.sql import StructuredData

    return _format(
        {
            col_name: TYPE_GENERATORS[str(col.type.python_type.__name__)]()
            for col_name, col in StructuredData.__mapper__.columns.items()
            if col_name != "id"
        }
    )
