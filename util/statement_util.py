

from util.typing_util import Consumer, Func, Predicate, Supplier, T


def for_loop(init: Supplier[T], predicate: Predicate[T], change: Func[T, T], block: Consumer[T]) -> None:
    _v: T = init()
    while predicate(_v):
        block(_v)
        _v = change(_v)
