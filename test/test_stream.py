import decimal
import functools
import unittest
from typing import List

from stream import stream


class TestStream(unittest.TestCase):
    _c_list: List[int]
    _i_stream: stream.Stream

    @classmethod
    def setUpClass(cls):
        cls._c_list = [1, 2, 3, 4, 5, 4, 4, 2, 3, 6, 12, 3, 45, 44]
        print("execute setUpClass")

    @classmethod
    def tearDownClass(cls):
        print("execute tearDownClass")

    def setUp(self):
        print("execute setUp")

    def test_make_stream(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)
        self.assertIsNotNone(i_stream)

    def test_collect(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        def _gen_list() -> List[int]:
            return []

        def _accumulate(coll: List[int], e: int) -> None:
            coll.append(e)
        r_lst: List[int] = i_stream.collect(
                _gen_list, _accumulate, lambda x: x)
        self.assertEqual(r_lst, TestStream._c_list)

    def test_filter(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        def _gen_list() -> List[int]:
            return []

        def _accumulate(coll: List[int], e: int) -> None:
            coll.append(e)
        r_lst: List[int] = i_stream.filter(lambda e: e % 2 == 0).collect(
                _gen_list, _accumulate, lambda x: x)
        self.assertEqual(r_lst, [2,  4,  4, 4, 2,  6, 12,   44])

    def test_sort(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        def _gen_list() -> List[int]:
            return []

        def _accumulate(coll: List[int], e: int) -> None:
            coll.append(e)
        r_lst: List[int] = i_stream.sorted(lambda x: x, False).collect(
                _gen_list, _accumulate, lambda x: x)
        self.assertEqual(r_lst, [1, 2, 2, 3, 3, 3, 4,
            4, 4, 5,  6, 12,   44, 45])

        def test_distinct(self) -> None:
            i_stream = stream.make_stream(TestStream._c_list)

        def _gen_list() -> List[int]:
            return []

        def _accumulate(coll: List[int], e: int) -> None:
            coll.append(e)
        r_lst: List[int] = i_stream.distinct().collect(
                _gen_list, _accumulate, lambda x: x)
        self.assertEqual(r_lst, [1, 2,  3, 4, 5,  6, 12, 45,   44])

    def test_slice(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        def _gen_list() -> List[int]:
            return []

        def _accumulate(coll: List[int], e: int) -> None:
            coll.append(e)
        r_lst: List[int] = i_stream.slice(4, 2).collect(
                _gen_list, _accumulate, lambda x: x)
        self.assertEqual(r_lst, [5, 4])

    def test_max(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        r: int = i_stream.max(lambda x: x)
        self.assertEqual(r, 45)

    def test_count(self) -> None:
        i_stream = stream.make_stream(TestStream._c_list)

        c: int = i_stream.count()
        self.assertEqual(c, len([1, 2, 3, 4, 5, 4, 4, 2,
            3, 6, 12, 3, 45, 44]))


        # m = s_int.filter(lambda x: x % 2 == 0).sorted(
        #     lambda x: x, True).distinct().slice(2, 2).max(lambda x: x)
        # #min(lambda x: x)
        # #collect(lambda: set(), lambda s, e: s.add(e), lambda s: s)
        # #foreach(lambda x: print(x))
        # # count()
if __name__ == '__main__':
    unittest.main()
