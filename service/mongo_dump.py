
import json
from typing import Any, Dict, List, MutableMapping

from mongos.mongo_crud import MongoConn
from mongos.mongo_query import collect_where, create_option
from mongos.mongo_type import MongoDefaultEncoder, MongoDocumentDecoder
from util.file_util import MultilineFileReader, MultilineFileWriter


# keep _id ?
# .dump
# keep index ?
def mongo_dump(conn: MongoConn, coll_name: str, file_name: str,
               keep_id: bool = False, keep_index: bool = True) -> None:
    UNIT_MAX = 1000
    count: int = conn.count(coll_name)

    times = 50
    unit = count//times
    if unit > UNIT_MAX:
        unit = UNIT_MAX
    times = (count+unit-1)//unit

    def _map_to_str(r: MutableMapping) -> str:
        return json.dumps(r, default=MongoDefaultEncoder)

    def _handle_ObjID(r: MutableMapping) -> None:
        if keep_id:
            return
        r.pop('_id')

    writer: MultilineFileWriter[MutableMapping] = MultilineFileWriter[MutableMapping](
        file_name, _map_to_str)
    writer.open()

    for t in range(times):
        option = create_option().slice(t*unit, unit)
        rs: List[MutableMapping] = conn.query(
            coll_name, collect_where(), option)

        [_handle_ObjID(r) for r in rs]
        writer.write(rs)
    # TODO handle index
    writer.close()


def mongo_import(conn: MongoConn, coll_name: str, file_name: str) -> None:

    unit = 50

    def _map_to_dict(r: str) -> Dict[str, Any]:
        return json.loads(r, object_hook=MongoDocumentDecoder)

    reader: MultilineFileReader[Dict[str, Any]] = MultilineFileReader[Dict[str, Any]](
        file_name, _map_to_dict)
    reader.open()

    running = True
    while running:
        records, goon = reader.read(unit)
        conn.insert(coll_name, *records)
        running = goon
    reader.close()
