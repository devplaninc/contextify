import dataclasses
import json
import logging
import os
import sys
from abc import abstractmethod
from typing import Protocol


class Encoder(Protocol):
    @abstractmethod
    def encode(self, msg: "StructuredMessage"):
        ...

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        # Handle Protocol Buffer message objects
        if hasattr(obj, 'DESCRIPTOR') and hasattr(obj, 'SerializeToDict'):
            return obj.SerializeToDict()
        # Handle Protocol Buffer message objects (alternative method)
        if hasattr(obj, 'DESCRIPTOR') and hasattr(obj, 'ListFields'):
            result = {}
            for field, value in obj.ListFields():
                result[field.name] = value
            return result
        return super().default(obj)


class JSONEncoder(Encoder):

    def encode(self, msg: "StructuredMessage"):
        d = {**msg.kwargs, "msg": msg.message}
        return json.dumps(d, cls=DataclassJSONEncoder)


class PlainTextEncoder(Encoder):
    _color: bool

    def __init__(self, color: bool = False):
        self._color = color

    def encode(self, msg: "StructuredMessage"):
        if self._color:
            extra = " ".join(f"\033[32m[{k}]={v}\033[0m" for k, v in msg.kwargs.items())
        else:
            extra = " ".join(f"[{k}]={v}" for k, v in msg.kwargs.items())
        return f"{msg.message} {extra}"


encoder: Encoder = JSONEncoder()


class _BelowErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def _log_level_from_env(default: str = "INFO") -> int:
    level_name = os.getenv("LOG_LEVEL", default).upper()
    level = logging.getLevelName(level_name)
    if isinstance(level, int):
        return level
    return logging.INFO


def configure_logging(default_level: str = "INFO") -> None:
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(_BelowErrorFilter())
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(_log_level_from_env(default_level))
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)


class StructuredMessage:
    message: str
    kwargs: dict

    def __init__(self, message, /, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return encoder.encode(self)


s_ = StructuredMessage
