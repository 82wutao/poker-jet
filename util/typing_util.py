from typing import Callable, TypeVar

T = TypeVar('T')
S = TypeVar('S')
R = TypeVar('R')

Runnable = Callable[[], None]
Func = Callable[[T], R]
BinFunc = Callable[[T, S], R]
Consumer = Callable[[T], None]
BinConsumer = Callable[[T, S], None]
Supplier = Callable[[], R]
Predicate = Callable[[T], bool]
Comparator = Callable[[T, T], int]
SortKey = Callable[[T], R]
