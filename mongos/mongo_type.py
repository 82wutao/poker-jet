

import binascii
import json
import re
from datetime import date, datetime
from time import strftime, struct_time
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from bson.objectid import ObjectId
from util import time_util
from util.typing_util import T

A = List[Any]
M = Dict[str, Any]


class E(Dict[str, Any]):
    def __init__(self, k: str, v: Any) -> None:
        super().__init__([(k, v)])
        self._key = k
        self._val = v

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        return self._val


D = List[E]


def create_A(*a: Any) -> A:
    ret: List[Any] = []
    ret.extend([i for i in a])
    return ret


def create_M(*pair: Tuple[str, Any]) -> M:
    return dict(pair)


def create_E(k: str, v: Any) -> E:
    return E(k, v)


def create_D(*e: E) -> D:
    ret: List[E] = []
    ret.extend([i for i in e])
    return ret


def mapD2M(d: D) -> M:
    ret: M = {}
    for e in d:
        ret[e.key] = e.value
    return ret


def creat_objectID(id: str) -> ObjectId:
    return ObjectId(id)


def unbox_objectID(id: ObjectId, map: Callable[[bytes], T]) -> T:
    return map(id.binary)


_ISODATE_RE = re.compile(
    r'"(ISODate\([\'\"]\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,6}Z[\'\"]\))"')
_OBJECTID_RE = re.compile(
    r'"(ObjectId\([\'\"][A-Za-z0-9]+[\'\"]\))"')

_ISODATE_VAL_RE = re.compile(
    r'"?ISODate\([\'\"](\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,6}Z)[\'\"]\)"?')
_OBJECTID_VAL_RE = re.compile(
    r'"?ObjectId\([\'\"]([A-Za-z0-9]+)[\'\"]\)"?')


def format_datetime_to_ISO(v: datetime) -> str:
    s = time_util.format_datetime(v, time_util.ISO_YMDTHMSSSSZ)
    return f'ISODate("{s}")'


def isodate_literal_to_constructor(txt: str) -> str:
    return _ISODATE_RE.sub(lambda m: m.group(1), txt)


def objectID_to_constructor(txt: str) -> str:
    return _OBJECTID_RE.sub(lambda m: m.group(1), txt)


def MongoDefaultEncoder(field):
    if isinstance(field, ObjectId):
        id: str = unbox_objectID(
            field, lambda bs: binascii.hexlify(bs).decode())
        return f"ObjectId('{id}')"
    if isinstance(field, datetime):
        s = time_util.format_datetime(field, time_util.ISO_YMDTHMSSSSZ)
        return f"ISODate('{s}')"
    if isinstance(field, date):
        date_format = field.strftime("%F")
        return f"ISODate('{date_format}')"
    if isinstance(field, struct_time):
        iso_format = strftime(time_util.ISO_YMDTHMSSSSZ, field)
        return f"ISODate('{iso_format}')"
    else:
        return json.JSONEncoder().default(field)


def MongoDocumentDecoder(obj: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in obj.items():
        if k == "_id":
            if isinstance(v, ObjectId):
                continue
            if isinstance(v, str):
                v = _OBJECTID_VAL_RE.sub(lambda m: m.group(1), v)
                obj[k] = ObjectId(v)
            continue
        if k == "updated_at" or k == "created_at":
            if isinstance(v, datetime):
                continue
            if isinstance(v, str):
                v = _ISODATE_VAL_RE.sub(lambda m: m.group(1), v)
                obj[k] = datetime.strptime(v, time_util.ISO_YMDTHMSSSSZ)
            continue
        if isinstance(v, str):
            m: Optional[re.Match[str]] = _ISODATE_VAL_RE.match(v)
            if m is None:
                continue

            v = m.group(1)
            obj[k] = datetime.strptime(v, time_util.ISO_YMDTHMSSSSZ)
            continue

        if isinstance(v, dict):
            obj[k] = MongoDocumentDecoder(v)
    return obj
