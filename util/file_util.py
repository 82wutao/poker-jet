import json
from functools import reduce
from io import TextIOWrapper
from typing import Any, Callable, Dict, Generic, List, Tuple, TypeVar

T = TypeVar('T')

Json = Dict[str, Any]


def save_as_csv(file_name: str,
                objects: List[T], to_clmn: Callable[[T], List[str]],
                title_supplier: Callable[[], List[str]], separator: str = ",") -> None:

    titles: List[str] = title_supplier()
    titles[-1] = titles[-1] + "\n"
    row_title = separator.join(titles)

    def _to_row(o: T):
        clmns = to_clmn(o)
        clmns[-1] = clmns[-1] + "\n"
        return separator.join(clmns)

    lines: List[str] = [_to_row(o) for o in objects]

    with open(file_name, "w", buffering=1024, encoding='utf-8') as wr:
        wr.write(row_title)
        wr.writelines(lines)


def save_as_json(file_name: str, objects: List[T], to_json: Callable[[T], Json]) -> None:
    json_list = [to_json(o) for o in objects]
    json_str = json.dumps(json_list)

    with open(file_name, "w", buffering=1024, encoding='utf-8') as wr:
        wr.write(json_str)


def load_from_json(file_name: str, map_to_T: Callable[[Json], T], buffer_size: int = 5120) -> List[T]:
    with open(file_name, "r", buffering=buffer_size, encoding='utf-8') as rd:
        json_list = json.load(rd)

    return [map_to_T(d) for d in json_list]


def load_from_csv(file_name: str, map_to_T: Callable[[List[str]], T],
                  skip_rows: int = 0, separator: str = ",") -> List[T]:
    with open(file_name, "r", encoding='utf-8') as rd:
        row_list: List[List[str]] = [
            l.split(separator) for l in rd.readlines()]

    def _strip_lf_and_map(str_lst: List[str]) -> T:
        str_lst[-1] = str_lst[-1].strip('\n')
        return map_to_T(str_lst)

    return [_strip_lf_and_map(r) for r in row_list[skip_rows:]]


class MultilineFileWriter(Generic[T]):
    _fn: str
    _map_line: Callable[[T], str]
    _file_hanle: TextIOWrapper
    _encoding: str

    def __init__(self, file_name: str, map_to_line: Callable[[T], str], encoding: str = 'utf-8'):
        self._fn = file_name
        self._map_line = map_to_line
        self._encoding = encoding
        pass

    def write_line(self, line: str) -> int:
        line = line + "\n"
        self._file_hanle.writelines([line])
        return len(line)

    def write(self, objects: List[T]) -> int:
        def _join(x): return self._map_line(x) + "\n"

        lines: List[str] = [_join(o) for o in objects]
        size = reduce(lambda c, e: len(e) + c, lines, 0)
        self._file_hanle.writelines(lines)
        return size

    def open(self):
        self._file_hanle = open(
            self._fn, "wt", buffering=1024, encoding=self._encoding)
        pass

    def close(self):
        self._file_hanle.close()
        pass

    def __enter__(self) -> "MultilineFileWriter[T]":
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    pass


class MultilineFileReader(Generic[T]):

    _fn: str
    _map_T: Callable[[str], T]
    _file_hanle: TextIOWrapper
    _encoding: str

    def __init__(self, file_name: str, map_to_T: Callable[[str], T], encoding: str = 'utf-8'):
        self._fn = file_name
        self._map_T = map_to_T
        self._encoding = encoding
        pass

    def read(self, lines: int) -> Tuple[List[T], bool]:
        ret: List[T] = []
        goon: bool = True

        for _ in range(lines):
            l = self._file_hanle.readline()
            if l is None or len(l) == 0:
                goon = False
                break

            l = l.rstrip("\n")
            t: T = self._map_T(l)
            ret.append(t)
        return ret, goon

    def read_line(self) -> str:
        return self._file_hanle.readline()

    def open(self):
        self._file_hanle = open(
            self.fn, "rt", buffering=1024, encoding='utf-8')
        pass

    def close(self):
        self._file_hanle.close()
        pass

    def __enter__(self) -> "MultilineFileReader[T]":
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    pass
