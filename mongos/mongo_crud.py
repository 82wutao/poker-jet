
import datetime
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pymongo
from pymongo import collection, database
from pymongo import results as mongo_result
from pymongo.mongo_client import MongoClient

from mongos.mongo_aggregate import Pipeline
from mongos.mongo_query import ResultOptions, WhereBuilder
from mongos.mongo_type import (D, E, M, creat_objectID, create_D, create_E,
                               create_M, mapD2M)
from mongos.mongo_update import FieldSetting, UpdateBuilder, collect_update


class MongoConn:
    _uri_str: str
    _db_str: str
    _cli: MongoClient
    _database: database.Database

    def __init__(self, uri: str, database: str) -> None:
        self._uri = uri
        self._db_str = database
        pass

    def __enter__(self) -> 'MongoConn':
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
        pass

    def open(self) -> 'MongoConn':
        self._cli = pymongo.MongoClient(self._uri)
        self._database = self._cli.get_database(self._db_str)
        return self

    def switch_database(self, database: str) -> 'MongoConn':
        self._db_str = database
        self._database = self._cli.get_database(self._db_str)
        return self

    def close(self) -> None:
        self._cli.close()

    def _collection(self, coll_name: str) -> collection.Collection:
        return self._database.get_collection(coll_name)

    def insert(self, coll_name: str, *doc: MutableMapping[str, Any]) -> List[Any]:
        result: mongo_result.InsertManyResult = self._collection(
            coll_name).insert_many([d for d in doc])
        return result.inserted_ids

    def delete(self, coll_name: str, wb: WhereBuilder, single: bool) -> int:
        result: mongo_result.DeleteResult
        filter = wb() if wb is not None else create_D()

        if single:
            result = self._collection(coll_name).delete_one(mapD2M(filter))
        else:
            result = self._collection(coll_name).delete_many(mapD2M(filter))
        return result.deleted_count

    def query(self, coll_name: str, where: WhereBuilder, option: Optional[ResultOptions]) -> List[MutableMapping]:
        filter = where() if where is not None else create_D()
        select = option.export_projection() if option is not None else create_M()

        cursor_args = {}
        cursor_args.update(option.export_slice() if option is not None else {})
        cursor_args.update(option.export_sort() if option is not None else {})

        with self._collection(coll_name).find(mapD2M(filter), select, **cursor_args) as c:
            ret = [d for d in c]
        return ret

    def fetchOne(self, coll_name: str, where: WhereBuilder, option: ResultOptions) -> Optional[MutableMapping]:
        # slice_getter: Dict[bool, Callable[[cursor.Cursor], cursor.Cursor]] = {
        #     True: option.ExportSliceOption(), False: lambda c: c}
        # sort_getter: Dict[bool, Callable[[cursor.Cursor], cursor.Cursor]] = {
        #     True: option.ExportSortOption(), False: lambda c: c}

        filter = where() if where is not None else create_D()
        select = option.export_projection() if option is not None else create_M()
        # slice = slice_getter[option is not None]
        # sort = sort_getter[option is not None]

        c: Optional[MutableMapping] = self._collection(
            coll_name).find_one(mapD2M(filter), select)
        return c

    def aggregate(self, coll_name: str, pipeline: Pipeline) -> List[MutableMapping]:
        with self._collection(coll_name).aggregate(pipeline()) as c:
            ret = [d for d in c]
        return ret
    # db.mycol.aggregate([
    # {$match: {year: 2018}},
    # {$unwind:  "$books"},
    # {$group: {"_id": {"author": "$author",  "bookType": "$books.type"}, count: {$sum: 1}}},
    # {$project: {"_id": 0, "author": "$_id.author", "bookType": "$_id.bookType", "bookTypeCnt": "$count"}},
    # {$sort: {author: -1}}
    # ])

    # db.mycol.aggregate([
    # {$match: {year: 2018}},
    # {$unwind:  "$books"},
    # {$group: {"_id": {"author": "$author",  "bookType": "$books.type"}}}
    # ])

    # db.mycol.aggregate([
    # {$match: {year: 2018}},
    # {$unwind:  "$books"},
    # {$group: {"_id": {"author": "$author",  "bookType": "$books.type"}}},
    # {$group: {"_id": {"author": "$_id.author"}, "typeCnt": {$sum: 1}}}
    # ])

    def update(self, coll_name: str, wb: WhereBuilder, ub: UpdateBuilder, single: bool) -> int:
        filter = wb() if wb is not None else create_D()
        setting = ub() if ub is not None else create_D()

        result: mongo_result.UpdateResult
        if single:
            result = self._collection(coll_name).update_one(
                mapD2M(filter), mapD2M(setting), upsert=False)
        else:
            result = self._collection(coll_name).update_many(
                mapD2M(filter), mapD2M(setting), upsert=False)
        return result.modified_count

    def updateByID(self, coll_name: str, id: Any, ub: UpdateBuilder) -> bool:
        settings = ub() if ub is not None else create_D()
        result: mongo_result.UpdateResult = self._collection(coll_name).update_one(
            {"_id": creat_objectID(id)}, mapD2M(settings), upsert=False)
        return result.modified_count == 1

    def upsert(self, coll_name: str, wb: WhereBuilder, ub: UpdateBuilder, single: bool) -> Tuple[int, Any]:
        filter = wb() if wb is not None else create_D()
        setting = ub() if ub is not None else create_D()

        result: mongo_result.UpdateResult
        if single:
            result = self._collection(coll_name).update_one(
                mapD2M(filter), mapD2M(setting), upsert=True)
        else:
            result = self._collection(coll_name).UpdateMany(
                mapD2M(filter), mapD2M(setting), upsert=True)
        return (result.modified_count, result.upserted_id)

    def softDelete(self, coll_name: str, where: WhereBuilder, single: bool, *marks: FieldSetting) -> int:
        updated_at = create_E("updated_at", datetime.datetime.utcnow())

        update_builder = collect_update(updated_at, *marks)
        return self.update(coll_name, where, update_builder, single)

    def count(self, coll_name: str, where: Optional[WhereBuilder] = None) -> int:
        filter = mapD2M(where()) if where is not None else create_M()
        return self._collection(coll_name).count_documents(filter)
