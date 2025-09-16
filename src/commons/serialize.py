def serializeJSON():
    pass


def deserializeJSON(class_, body):
    if "name" in dct and "created_at" in dct:
        return class_(
            name=dct["name"],
            created_at=datetime.fromisoformat(dct["created_at"]),
        )
    return dct
