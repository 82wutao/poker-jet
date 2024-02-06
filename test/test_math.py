import decimal
import functools
import unittest

from mathematics import linear


class TestMath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("execute setUpClass")

    @classmethod
    def tearDownClass(cls):
        print("execute tearDownClass")

    # def setUp(self):
    #     print("execute setUp")

    # def tearDown(self):
    #     print("execute tearDown")

    def test_make_eye_matrix(self) -> None:
        r: linear.MATRIX = linear.make_eye_matrix(2, 1)
        assert r == [[1, 0], [0, 1]]
        r: linear.MATRIX = linear.make_eye_matrix(2, 2)
        assert r == [[2, 0], [0, 2]]

    def test_matrix_T(self) -> None:
        r: linear.MATRIX = linear.matrix_T([[1, 1], [2, 2], [3, 3]])
        assert r == [[1, 2, 3], [1, 2, 3]]
        r: linear.MATRIX = linear.matrix_T(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        assert r == [[1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12]]

    def test_make_vector(self) -> None:
        r: linear.VECTOR = linear.make_vector(5, lambda: 1)
        self.assertEqual(r, [1, 1, 1, 1, 1])

        s: int = 0

        def _g() -> int:
            nonlocal s
            s += 1
            return s
        r: linear.VECTOR = linear.make_vector(5, _g)
        self.assertEqual(r, [1, 2, 3, 4, 5])

    def test_vector_plus_vector(self) -> None:
        a: linear.VECTOR = [1, 2, 3, 4, 5, 6]
        b: linear.VECTOR = [5, 6, 7, 8, 9, 0]
        r: linear.VECTOR = linear.vector_plus_vector(a, b)
        self.assertEqual(r, [6, 8, 10, 12, 14, 6])

    def test_vector_sub_vector(self) -> None:
        a: linear.VECTOR = [1, 2, 3, 4, 5, 6]
        b: linear.VECTOR = [5, 6, 7, 8, 9, 0]
        r: linear.VECTOR = linear.vector_subtract_vector(a, b)
        self.assertEqual(r, [-4, -4, -4, -4, -4, 6])

    def test_vector_multiply_scalar(self) -> None:
        a: linear.VECTOR = [1, 2, 3, 4, 5, 6]
        r: linear.VECTOR = linear.vector_multiply_scalar(a, 0.1)

        self.assertEqual([decimal.Decimal(e).quantize(decimal.Decimal('0.00')) for e in r],
                         [decimal.Decimal(e).quantize(decimal.Decimal('0.00')) for e in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]])

    def test_vector_multiply_vector(self) -> None:
        a: linear.VECTOR = [4, 6, 7]
        b: linear.VECTOR = [1, 2, 3]
        r: linear.SCALAR = linear.vector_multiply_vector(a, b)
        self.assertEqual(r, 37)
        a: linear.VECTOR = [4.5, 6.3, 0.47]
        b: linear.VECTOR = [1.2, 2.6, 3.3]
        r: linear.SCALAR = linear.vector_multiply_vector(a, b)
        self.assertEqual(decimal.Decimal(r).quantize(decimal.Decimal('0.00')),
                         functools.reduce(lambda d, v: decimal.Decimal(v).quantize(decimal.Decimal('0.00'))+d,
                         [4.5*1.2, 6.3*2.6, 0.47*3.3], decimal.Decimal(0)))

    def test_vector_multiply_matrix(self) -> None:
        v: linear.VECTOR = [4, 4, 4, 4]
        m: linear.MATRIX = [[0.5, 0.5], [2, 2], [4, 4], [8, 8]]
        r: linear.VECTOR = linear.vector_multiply_matrix(v, m)
        self.assertEqual([decimal.Decimal(e).quantize(decimal.Decimal('0.00')) for e in r],
                         [decimal.Decimal(v).quantize(decimal.Decimal('0.00')) for v in [4*0.5+4*2+4*4+4*8, 4*0.5+4*2+4*4+4*8]])

    def test_matrix_multiply_scalar(self) -> None:
        m: linear.MATRIX = [[0.5, 0.5, 0.5, 0.5], [2, 2, 2, 2]]
        s: linear.SCALAR = 0.5
        r: linear.MATRIX = linear.matrix_multiply_scalar(m, s)
        self.assertEqual(r,
                         [[decimal.Decimal(i).quantize(decimal.Decimal('0.00')) for i in e]
                          for e in [[0.5*0.5, 0.5*0.5, 0.5*0.5, 0.5*0.5], [2*0.5, 2*0.5, 2*0.5, 2*0.5]]])

    def test_matrix_multiply_vector(self) -> None:
        m: linear.MATRIX = [[0.5, 0.5, 0.5, 0.5], [2, 2, 2, 2]]
        v: linear.VECTOR = [0.1, 0.2, 0.3, 0.4]
        r: linear.VECTOR = linear.matrix_multiply_vector(m, v)
        self.assertEqual(r,
                         [decimal.Decimal(e).quantize(decimal.Decimal('0.00'))
                          for e in [0.5*0.1 + 0.5*0.2 + 0.5*0.3 + 0.5*0.4, 2*0.1 + 2*0.2 + 2*0.3 + 2*0.4]])

    def test_matrix_multiply_matrix(self) -> None:
        m1: linear.MATRIX = [[5, 5, 5, 5], [2, 2, 2, 2]]
        m2: linear.MATRIX = [[0.1, 0.2, 0.3, 0.4],
                           [1, 2, 3, 4], [10, 20, 30, 40]]
        r: linear.MATRIX = linear.matrix_multiply_matrix(m1, m2, True)
        self.assertEqual(r,
                         [[decimal.Decimal(i).quantize(decimal.Decimal('0.00')) for i in e]
                          for e in [[5*0.1+5*0.2+5*0.3+5*0.4, 5*1+5*2+5*3+5*4, 5*10+5*20+5*30+5*40],
                                    [2*0.1+2*0.2+2*0.3+2*0.4, 2*1+2*2+2*3+2*4, 2*10+2*20+2*30+2*40]]])

        m1: linear.MATRIX = [[5, 5, 5, 5], [2, 2, 2, 2]]
        m2: linear.MATRIX = [[0.1, 1, 10], [0.2, 2, 20],
                           [0.3, 3, 30], [0.4, 4, 40]]
        r: linear.MATRIX = linear.matrix_multiply_matrix(m1, m2)
        self.assertEqual(r,
                         [[decimal.Decimal(i).quantize(decimal.Decimal('0.00')) for i in e]
                          for e in [[5*0.1+5*0.2+5*0.3+5*0.4, 5*1+5*2+5*3+5*4, 5*10+5*20+5*30+5*40],
                                    [2*0.1+2*0.2+2*0.3+2*0.4, 2*1+2*2+2*3+2*4, 2*10+2*20+2*30+2*40]]])


if __name__ == '__main__':
    unittest.main()
