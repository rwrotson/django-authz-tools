from typing import Any


def has_not_empty(obj: Any, attr_name: str) -> bool:
    return hasattr(obj, attr_name) and getattr(obj, attr_name)


def has_empty(obj: Any, attr_name: str) -> bool:
    return hasattr(obj, attr_name) and not getattr(obj, attr_name)


def get_if_exists(obj: Any, attr_name: str) -> Any | None:
    return getattr(obj, attr_name) if hasattr(obj, attr_name) else None
