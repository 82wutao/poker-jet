
from typing import (Any, Callable, Dict, List, Mapping, Optional, Tuple, Type,
                    Union)

from bson import SON

from mongos.mongo_query import WhereBuilder
from mongos.mongo_type import D, E, M, create_D, create_E, create_M, mapD2M


class ProjectBuilder:
    _project_expressions: D

    def __init__(self) -> None:
        self._project_expressions = create_D()
        pass

    def exclude_id(self, yes: bool) -> 'ProjectBuilder':
        self._project_expressions.append(create_E("_id", 0 if yes else 1))
        return self

    def show(self, fields: List[str], yes: bool) -> 'ProjectBuilder':
        self._project_expressions.extend(
            [create_E(f, 1 if yes else 0) for f in fields])
        return self

    def as_alias(self, fields: Mapping[str, str]) -> 'ProjectBuilder':
        self._project_expressions.extend(
            [create_E(a, f'${f}') for (f, a) in fields.items()])
        return self

    @staticmethod
    def _alias_after_handle(field: str, expression: E, as_alias: Optional[str] = None) -> E:
        if as_alias is not None:
            return create_E(as_alias, expression)
        as_temp = create_E(f"{field}_as_temp", expression)
        return create_E(field, as_temp)

    def concat(self, field: str, *val_concat: str, as_alias: Optional[str] = None) -> 'ProjectBuilder':
        concat_express: E = create_E(
            "$concat", [f"${field}"].extend(val_concat))

        project_field: E = ProjectBuilder._alias_after_handle(
            field, concat_express, as_alias)
        self._project_expressions.append(project_field)
        return self

    def substr(self, field: str, begin: int, length: int,  as_alias: Optional[str] = None) -> 'ProjectBuilder':
        substr_express = create_E("$substr", [f"${field}", begin, length])

        project_field: E = ProjectBuilder._alias_after_handle(
            field, substr_express, as_alias)
        self._project_expressions.append(project_field)
        return self

    def case_convert(self, field: str, upper: bool,  as_alias: Optional[str] = None) -> 'ProjectBuilder':
        op: str = "$toUpper" if upper else "$toLower"
        casser_express = create_E(op, f"${field}")
        project_filed = ProjectBuilder._alias_after_handle(
            field, casser_express, as_alias)
        self._project_expressions.append(project_filed)
        return self

    def format_date(self, field: str, format: str, as_alias: Optional[str] = None) -> 'ProjectBuilder':
        format_express = create_E("$dateToString", create_M(
            ("format", format), ("date", f"${field}")))
        project_filed = ProjectBuilder._alias_after_handle(
            field, format_express, as_alias)
        self._project_expressions.append(project_filed)
        return self

    def len_of(self, field, as_alias: Optional[str] = None) -> 'ProjectBuilder':
        len_express = create_E("$size", f"${field}")
        project_filed = ProjectBuilder._alias_after_handle(
            field, len_express, as_alias)
        self._project_expressions.append(project_filed)
        return self

    def extend(self) -> 'ProjectBuilder':
        # db.sales.aggregate([{ $project :
        #     { _id: 0, item : 1, price: "$price", dateInfo: { day: { $dayOfYear: "$date"}, year: { $year: "$date" } } }
        # }]);

        # db.ratings.aggregate([
        #    {
        #      $project: { delta: { $abs: { $subtract: [ "$start", "$end" ] } } }
        #    }
        # ])
        return self

    def math_compute(self, field: str, asmdm: str, num_or_reference: Union[int,  str], as_alias: Optional[str] = None) -> 'ProjectBuilder':
        num_or_reference = f"${num_or_reference}" if isinstance(
            num_or_reference, str) else num_or_reference
        op: Mapping[str, str] = {"+": "$add", "-": "$subtract",
                                 "*": "$multipy", "/": "$divide", "%": "$mod"}
        math_express = create_E(op[asmdm], [f"${field}", num_or_reference])
        project_field = ProjectBuilder._alias_after_handle(
            field, math_express, as_alias)
        self._project_expressions.append(project_field)
        return self

    def relational_compare(self) -> 'ProjectBuilder':
        # 关系运算：大小比较（"$cmp"）、等于（"$eq"）、大于（"$gt"）、大于等于（"$gte"）、小于（"$le"）、小于等于（"$lte"）、不等于（"$ne"）、判断 null （"$ifNull"），这些返回值都是 boolean 值类型的。
        return self

    def logic_compare(self) -> 'ProjectBuilder':
        # 逻辑运算：与（"$and"）、或（"$or"）、非 （"$not"）
        return self

    def build(self) -> E:
        projects: M = mapD2M(self._project_expressions)
        return create_E("$project", projects)


class Pipeline:
    # alias = TypeVar('alias', bound='Pipeline')
    _chains: List[M]

    def __init__(self) -> None:
        self._chains = []
        pass

    def __call__(self) -> List[M]:
        return self._chains

    def match(self, wb: WhereBuilder) -> 'Pipeline':
        where_d = wb()
        match = ("$match", mapD2M(where_d))
        self._chains.append(create_M(match))
        return self

    def split_arr_rows(self, field: str) -> 'Pipeline':
        self._chains.append(create_M(("$unwind", f"${field}")))
        return self

    def _group_func(self, groupBy: str, fn: str, fn_exp: Callable[[], Any], field_view: str) -> None:
        groups = create_D()

        _id = None if groupBy is None else f"${groupBy}"
        groups.append(create_E("_id", _id))
        groups.append(create_E(field_view, create_M((fn, fn_exp()))))

        self._chains.append(create_M(("$group", mapD2M(groups))))
        pass

    def average(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$avg", lambda: f"${field}", field_alias)
        return self

    def sum(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        sumed = f"${field}" if field is not field else 1
        self._group_func(groupBy, "$sum", lambda: sumed, field_alias)
        return self

    def count(self, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$sum", lambda: 1, field_alias)
        return self

    def min(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$min", lambda: f"${field}", field_alias)
        return self

    def max(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$max", lambda: f"${field}", field_alias)
        return self

    def append(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$push", lambda: f"${field}", field_alias)
        return self

    def add_2_set(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$addToSet",
                         lambda: f"${field}", field_alias)
        return self

    def first(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$first", lambda: f"${field}", field_alias)
        return self

    def last(self, field: str, field_alias: str, groupBy: str) -> 'Pipeline':
        self._group_func(groupBy, "$last", lambda: f"${field}", field_alias)
        return self

    def select(self, fields: List[str], exclude: bool, IDExcluded: bool) -> 'Pipeline':
        s: Dict[bool, int] = {True: 0, False: 1}

        selects = create_D()
        selects.append(create_E("_id", s[IDExcluded]))

        for f in fields:
            selects.append(create_E(f, s[exclude]))
        self._chains.append(create_M(("$project", mapD2M(selects))))
        return self

    def select_expression(self, builder: ProjectBuilder) -> 'Pipeline':
        self._chains.append(builder.build())
        return self

    def slice(self, offset: int, limit: int) -> 'Pipeline':
        self._chains.append(create_M(("$skip", offset)))
        self._chains.append(create_M(("$limit", limit)))
        return self

    def sort(self, asc: List[str], desc: List[str]) -> 'Pipeline':
        '''
        排序字段的名字是计算产生后的投影的名字
        '''
        sorted: List[Tuple[str, int]] = []
        for a in asc:
            sorted.append((a, 1))
        for de in desc:
            sorted.append((de, -1))

        self._chains.append(create_M(("$sort", SON(sorted))))
        return self


def create_pipeline() -> 'Pipeline':
    return Pipeline()


# $sum	计算总和。	db.mycol.aggregate([{$group: {_id: "$by_user", num_tutorial: {$sum: "$likes"}}}])
# $avg	计算平均值	db.mycol.aggregate([{$group: {_id: "$by_user", num_tutorial: {$avg: "$likes"}}}])
# $min	获取集合中所有文档对应值得最小值。	db.mycol.aggregate([{$group: {_id: "$by_user", num_tutorial: {$min: "$likes"}}}])
# $max	获取集合中所有文档对应值得最大值。	db.mycol.aggregate([{$group: {_id: "$by_user", num_tutorial: {$max: "$likes"}}}])
# $push	将值加入一个数组中，不会判断是否有重复的值。	db.mycol.aggregate([{$group: {_id: "$by_user", url: {$push: "$url"}}}])
# $addToSet	将值加入一个数组中，会判断是否有重复的值，若相同的值在数组中已经存在了，则不加入。	db.mycol.aggregate([{$group: {_id: "$by_user", url: {$addToSet: "$url"}}}])
# $first	根据资源文档的排序获取第一个文档数据。	db.mycol.aggregate([{$group: {_id: "$by_user", first_url: {$first: "$url"}}}])
# $last	根据资源文档的排序获取最后一个文档数据	db.mycol.aggregate([{$group: {_id: "$by_user", last_url: {$last: "$url"}}}])

# $project：修改输入文档的结构。可以用来重命名、增加或删除域，也可以用于创建计算结果以及嵌套文档。 db.article.aggregate({$project: {title: 1, author: 1, }})
# $match：用于过滤数据，只输出符合条件的文档。$match使用MongoDB的标准查询操作。 db.articles.aggregate([{$match: {score: {$gt: 70, $lte: 90}}}, {$group: {_id: null, count: {$sum: 1}}}])
# $limit：用来限制MongoDB聚合管道返回的文档数。 db.article.aggregate({$skip: 5})
# $skip：在聚合管道中跳过指定数量的文档，并返回余下的文档。
# $unwind：将文档中的某一个数组类型字段拆分成多条，每条包含数组中的一个值。
# $group：将集合中的文档分组，可用于统计结果。
# $sort：将输入文档排序后输出。
# $geoNear：输出接近某一地理位置的有序文档。
