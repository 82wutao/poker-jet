import enum
from typing import (Any, Dict, Generic, Iterable, Iterator, List, Mapping,
                    Optional, Set, Tuple, cast)

from util.statement_util import for_loop
from util.typing_util import (BinConsumer, BinFunc, Comparator, Consumer, Func,
                              Predicate, R, S, SortKey, Supplier, T)


class Next(Generic[T]):
    _it: Iterator[T]

    _v: Optional[T]

    def __init__(self, it: Iterator[T]) -> None:
        self._it = it
        self._v = None

    def take(self) -> T:
        if self._v is None:
            raise Exception(
                "should call 'has_more' method before take element")
        return self._v

    def has_more(self) -> bool:
        self._v = None
        try:
            self._v = next(self._it)
            return True
        except StopIteration:
            return False


class Stream(Generic[T]):
    _next: Supplier[Tuple[bool, Optional[T]]]  # is_end,ele

    class HowToMatch(enum.Enum):
        ALL_MATCH = -1
        NONE_MATCH = 0
        ANY_match = 1

    def __init__(self, n: Supplier[Tuple[bool, Optional[T]]]) -> None:
        self._next = n
        pass

    def count(self) -> int:
        c: int = 0

        def _counter(_: Tuple[bool, Optional[T]]) -> None:
            nonlocal c
            c += 1

        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), _counter)
        return c

    def foreach(self, c: Consumer[T]) -> None:
        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), lambda z: c(cast(T, z[1])))

    def reduce(self, r: BinFunc[T, T, T], s: Supplier[T]) -> Optional[T]:
        _dest: T = s()

        def _reduce(t: T) -> None:
            nonlocal _dest
            _dest = r(_dest,  t)

        for_loop(lambda: self._next(), lambda x: not x[0], lambda _: self._next(),
                 lambda z: _reduce(cast(T, z[1])))
        return _dest

    def collect(self, supplier: Supplier[S],
                accumulator: BinConsumer[S, T], finisher: Func[S, R]) -> R:
        _dest: S = supplier()
        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), lambda z: accumulator(_dest, cast(T, z[1])))
        return finisher(_dest)

    def group(self, supplier: Supplier[List[R]], group_func: Func[T, Tuple[S, R]],
              accumulator: BinConsumer[List[R], R]) -> Dict[S, List[R]]:
        _dest: Dict[S, List[R]] = {}

        def _group_accumulate(t: T) -> None:
            k, v = group_func(t)
            lst: List[R] = _dest.get(k, supplier())
            accumulator(lst, v)

        for_loop(lambda: self._next(), lambda x: not x[0], lambda _: self._next(),
                 lambda z: _group_accumulate(cast(T, z[1])))
        return _dest

    def hash(self, group_func: Func[T, Tuple[S, R]]) -> Dict[S, R]:
        _dest: Dict[S, R] = {}

        def _mapping(t: T) -> None:
            nonlocal _dest
            k, v = group_func(t)
            _dest[k] = v

        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), lambda z: _mapping(cast(T, z[1])))
        return _dest

    def min(self, valuer: Func[T, int]) -> Optional[T]:
        _dest: Optional[T] = None

        def _min(t: T) -> None:
            nonlocal _dest
            _dest = t if _dest is None else _dest if valuer(
                cast(T, _dest)) < valuer(t) else t
        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), lambda z: _min(cast(T, z[1])))
        return cast(T, _dest)

    def max(self, valuer: Func[T, int]) -> T:
        _dest: Optional[T] = None

        def _max(t: T) -> None:
            nonlocal _dest
            _dest = t if _dest is None else _dest if valuer(
                cast(T, _dest)) > valuer(t) else t
        for_loop(lambda: self._next(), lambda x: not x[0],
                 lambda _: self._next(), lambda z: _max(cast(T, z[1])))
        return cast(T, _dest)

    def match(self, predicate: Predicate[T], how: HowToMatch) -> bool:
        '''
        :Parameters:
          - `how` :  The valid options are :
            - :attr:`-1` - all elements of stream match the predicate.
            - :attr:`0` - no any element of stream match the predicate.
            - :attr:`1` - at least one element match the predicate.
        '''
        _match_count: int = 0
        _fail_count: int = 0

        # complete_how,result
        def _all_match(end_iterate: bool) -> Tuple[bool, bool]:
            return (True, False) if _fail_count > 0 else (end_iterate, end_iterate)

        # complete_how,result
        def _none_match(end_iterate: bool) -> Tuple[bool, bool]:
            return (True, False) if _match_count > 0 else (end_iterate, end_iterate)

        # complete_how,result
        def _any_match(end_iterate: bool) -> Tuple[bool, bool]:
            return (True, True) if _match_count > 0 else (end_iterate, not end_iterate)

        _matches: Mapping[Stream.HowToMatch, Func[bool, Tuple[bool, bool]]] = {
            Stream.HowToMatch.ALL_MATCH: _all_match,
            Stream.HowToMatch.NONE_MATCH: _none_match,
            Stream.HowToMatch.ANY_match: _any_match}
        _match_func = _matches[how]

        while True:
            (is_end, ele) = self._next()
            if is_end:
                break

            if predicate(cast(T, ele)):
                _match_count += 1
            else:
                _fail_count += 1
            _complete, _result = _match_func(False)
            if _complete:
                return _result
        _, _result = _match_func(True)
        return _result

    def filter(self, f: Predicate[T]) -> 'Stream[T]':
        _next_origin = self._next

        def _next_filter() -> Tuple[bool, Optional[T]]:
            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    return (is_end, ele)

                if f(cast(T, ele)):
                    return (False, ele)
        ns = Stream[T](_next_filter)
        return ns

    def map(self, mapper: Func[T, R]) -> 'Stream[R]':
        _next_origin = self._next

        def _next_map() -> Tuple[bool, Optional[R]]:
            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    return (is_end, None)

                return (False, mapper(cast(T, ele)))
        ns = Stream[R](_next_map)
        return ns

    # def flatmap(self, mapper: Func[T, R]) -> 'Stream[R]':
    #     _next_origin = self._next

    #     def _next_map() -> Tuple[bool, Optional[R]]:
    #         while True:
    #             (is_end, ele) = _next_origin()

    #             if is_end:
    #                 return (is_end, None)
    #             return (False, mapper(cast(T, ele)))
    #     ns = Stream[R]()
    #     ns._set_nextfunc(_next_map)
    #     return ns
    def distinct(self) -> 'Stream[T]':
        _next_origin = self._next

        _s: Set[T] = set()

        def _next_distinct() -> Tuple[bool, Optional[T]]:
            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    return (is_end, None)

                _t: T = cast(T, ele)
                if _t not in _s:
                    _s.add(_t)
                    return (False, _t)

        ns = Stream[T](_next_distinct)
        return ns

    def sorted(self, comparator: SortKey[T, Any], r: bool) -> 'Stream[T]':
        _next_origin = self._next
        _has_sorted: bool = False

        def _get_nextorigin() -> Supplier[Tuple[bool, Optional[T]]]:
            return _next_origin

        def _sort_func() -> None:
            nonlocal _next_origin, _has_sorted

            _s: List[T] = []
            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    break
                _s.append(cast(T, ele))
            _s.sort(key=comparator, reverse=r)
            n = Next(iter(_s))

            def _next_new() -> Tuple[bool, Optional[T]]:
                return (False, n.take()) if n.has_more() else (True, None)
            _next_origin = _next_new
            _has_sorted = True

        def _next_sorted() -> Tuple[bool, Optional[T]]:
            if not _has_sorted:
                _sort_func()

            while True:
                (is_end, ele) = _get_nextorigin()()
                if is_end:
                    return (is_end, None)

                return (False, cast(T, ele))

        ns = Stream[T](_next_sorted)
        return ns

    def peek(self, action: Consumer[T]) -> 'Stream[T]':
        _next_origin = self._next

        def _next_peek() -> Tuple[bool, Optional[T]]:
            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    return (is_end, None)

                action(cast(T, ele))
                return (False, cast(T, ele))

        ns = Stream[T](_next_peek)
        return ns

    def slice(self, beg: int, length: int) -> 'Stream[T]':
        _next_origin = self._next
        _position: int = 0

        def _next_slice() -> Tuple[bool, Optional[T]]:
            nonlocal _position
            _end = beg+length

            while True:
                (is_end, ele) = _next_origin()
                if is_end:
                    return (is_end, None)

                if _position < beg:
                    _position += 1
                    continue
                if length == -1:
                    _position += 1
                    return (False, cast(T, ele))
                if _position < _end:
                    _position += 1
                    return (False, cast(T, ele))
                _position += 1

        ns = Stream[T](_next_slice)
        return ns


# def make_stream(n: Next[T]) -> Stream[T]:
#     def _next_origin() -> Tuple[bool, Optional[T]]:
#         return (False, n.take()) if n.has_more() else (True, None)

#     s = Stream[T]()
#     s._set_nextfunc(_next_origin)
#     return s


def make_stream(able: Iterable[T]) -> Stream[T]:
    n = Next[T](iter(able))

    def _next_origin() -> Tuple[bool, Optional[T]]:
        return (False, n.take()) if n.has_more() else (True, None)

    s = Stream[T](_next_origin)
    return s
