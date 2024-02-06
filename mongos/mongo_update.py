
from typing import Any, Callable, TypeVar

from mongos.mongo_type import D, E, create_A, create_D, create_E, create_M

# TODO min max inc rename

UpdateBuilder = Callable[[], D]
FieldSetting = E


def collect_update(update: E, *other: E) -> UpdateBuilder:
    def _ret() -> D:
        ret = create_D(update)
        if len(other) != 0:
            ret.extend([o for o in other])
        return ret
    return _ret


def update_set(setting: FieldSetting, *other: FieldSetting) -> E:
    settings = create_M()
    settings[setting.key] = setting.value

    for s in other:
        settings[s.key] = s.value

    return create_E("$set", settings)


def ppdate_unset(field: str, *other: str) -> E:
    removes = create_M()
    removes[field] = 1

    for f in other:
        removes[f] = 1
    return create_E("$unset", removes)


def update_or_insert(uoi: FieldSetting, *other: FieldSetting) -> E:
    settings = create_M()
    settings[uoi.key] = uoi.value

    for ui in other:
        settings[ui.key] = ui.value

    return create_E("$setOnInsert", settings)


class ArrayOperate:

    _field: str

    def __init__(self, field: str) -> None:
        self._field = field

    def pop_first(self) -> E:
        return create_E("$pop", create_M((self._field, -1)))

    def pop_last(self) -> E:
        return create_E("$pop", create_M((self._field, 1)))

    def pull(self, value: Any, *other: Any) -> E:
        value_ = create_A(value)
        value_.extend([o for o in other])
        return create_E("$pullAll", create_M((self._field, value_)))

    def add(self, value: Any, *other: Any) -> E:
        value_ = create_A(value)
        value_.extend([o for o in other])
        each = create_E("$each", value_)
        return create_E("$addToSet", create_M((self._field, each)))

    def push(self, value: Any, *other: Any) -> E:
        value_ = create_A(value)
        value_.extend([o for o in other])
        return create_E("$pullAll", create_M((self._field, value_)))


def update_array(field: str) -> ArrayOperate:
    return ArrayOperate(field)
