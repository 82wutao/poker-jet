
from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Tuple, TypeVar

from bson.son import SON
from pymongo import ASCENDING, DESCENDING, cursor

from mongos.mongo_type import (D, E, M, create_A, create_D, create_E, create_M,
                               mapD2M)

WhereBuilder = Callable[[], D]


def collect_where(*where: E) -> WhereBuilder:
    wheres = create_D(*where)

    def _ret() -> D:
        return wheres
    return _ret


class FieldCondition:
    # alias = TypeVar('alias', bound='FieldCondition')

    _expression: E

    def __call__(self) -> E:
        return self._expression

    def __init__(self, field: str) -> None:
        self._expression = create_E(field, create_M())
        pass

    def _goExp(self, operator: str, value: Any) -> None:
        condiExp: Any = self._expression.value
        condiExp[operator] = value

    def equals(self, value: Any, yes: bool) -> FieldCondition:
        op: Dict[bool, str] = {True: "$eq", False: "$ne"}
        self._goExp(op[yes], value)
        return self

    def lessthan(self, value: Any, yes: bool) -> FieldCondition:
        op: Dict[bool, str] = {True: "$lt", False: "$gte"}
        self._goExp(op[yes], value)
        return self

    def greatethan(self, value: Any, yes: bool) -> FieldCondition:
        op: Dict[bool, str] = {True: "$gt", False: "$lte"}
        self._goExp(op[yes], value)
        return self

    def in_these(self, value: List[Any], yes: bool) -> FieldCondition:
        op: Dict[bool, str] = {True: "$in", False: "$nin"}
        self. _goExp(op[yes], value)
        return self

    def existed(self, existed: bool) -> FieldCondition:
        self._goExp("$exists", existed)
        return self

    def regexp(self, regexp: str, *options: str) -> FieldCondition:
        self._goExp("$regex", regexp)
        self._goExp("$options", [o for o in options])
        return self


def by_field(field: str) -> FieldCondition:
    return FieldCondition(field)


def _relations(conditions: List[E], rel: str) -> E:
    return create_E(rel, [create_M((e.key, e.value)) for e in conditions])


def or_these(conditions: List[E]) -> E:
    return _relations(conditions, "$or")


def and_these(conditions: List[E]) -> E:
    return _relations(conditions, "$and")


def nor_these(conditions: List[E]) -> E:
    return _relations(conditions, "$nor")


def text_search(keywords: List[str], *exclude: str) -> E:
    values_: List[str] = []
    values_.extend(keywords)
    values_.extend([f"-{e}" for e in exclude])

    return create_E("$text", create_M(("$search", " ".join(values_))))


class ResultOptions:
    # alias = TypeVar('alias', bound='ResultOptions')

    _skip:  int
    _limit:  int
    _asc: List[str]
    _desc: List[str]
    _selects: List[str]
    _excludes: List[str]

    def __init__(self) -> None:
        self._skip = 0
        self._limit = 0
        self._asc = []
        self._desc = []
        self._selects = []
        self._excludes = []
        pass

    def slice(self, offset: int, limit: int) -> ResultOptions:
        self._skip = offset
        self._limit = limit
        return self

    def order(self, asc: List[str], desc: List[str]) -> ResultOptions:
        self._asc.extend(asc)
        self._desc.extend(desc)
        return self

    def select(self, fields: List[str], exclude: bool, IDExcluded: bool) -> ResultOptions:
        if IDExcluded:
            self._excludes.append("_id")
        s: Dict[bool, List[str]] = {True: self._excludes, False: self._selects}
        s[exclude].extend(fields)
        return self

    def export_projection(self) -> M:
        project = create_M()
        for s in self._selects:
            project[s] = 1
        for s in self._excludes:
            project[s] = 0
        return project

    # def ExportFindOneOption(self) -> self:
    #     opt := options.FindOne()
    #     {
    #         project := bson.M{}
    #         for _, s := range qo.selects {
    #             project[s] = 1
    #         }
    #         for _, s := range qo.excludes {
    #             project[s] = 0
    #         }
    #         opt.SetProjection(project)
    #     }
    #     {
    #         opt.SetSkip(qo.skip)
    #     }
    #     {
    #         sorts := bson.M{}
    #         for _, a := range qo.asc {
    #             sorts[a] = 1
    #         }
    #         for _, a := range qo.desc {
    #             sorts[a] = -1
    #         }
    #         opt.SetSort(bson.E{Key: operator.Sort, Value: sorts})
    #     }
    #     return opt
    def export_slice(self) -> M:
        return create_M(("skip", self._skip), ("limit", self._limit))

    def export_sort(self) -> M:
        orders: List[Tuple[str, int]] = []
        for a in self._asc:
            orders.append((a, ASCENDING))
        for de in self._desc:
            orders.append((de, DESCENDING))
        return create_E("sort", orders)

        # def ExportFindOption(self,) * options.FindOptions {
        #     opt := options.Find()
        #     {
        #         sorts := bson.M{}
        #         for _, a := range qo.asc {
        #             sorts[a] = 1
        #         }
        #         for _, a := range qo.desc {
        #             sorts[a] = -1
        #         }
        #         opt.SetSort(bson.E{Key: operator.Sort, Value: sorts})
        #     }
        #     return opt
        #     // opt.SetAllowDiskUse()
        #     // opt.SetAllowPartialResults()
        #     // opt.SetBatchSize()
        #     // opt.SetCollation()
        #     // opt.SetCursorType()
        #     // opt.SetHint()
        #     // opt.SetLet()
        #     // opt.SetMax()
        #     // opt.SetMaxAwaitTime()
        #     // opt.SetMaxTime()
        #     // opt.SetMin()
        #     // opt.SetNoCursorTimeout()
        #     // opt.SetOplogReplay()
        #     // opt.SetReturnKey()
        #     // opt.SetShowRecordID()
        #     // opt.SetSnapshot()
        # }


def create_option() -> ResultOptions:
    return ResultOptions()
