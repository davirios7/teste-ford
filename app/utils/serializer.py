import datetime
from enum import Enum
from typing import Any


def default_serializer(obj: Any) -> Any:
    # Serializa objetos datetime
    if isinstance(obj, datetime.date):
        return obj.isoformat()

    # Serializa objetos Enum
    if isinstance(obj, Enum):
        return obj.value

    # Se não for um tipo especial, levanta erro
    raise TypeError(f"Type {type(obj)} not serializable")
