import unittest
import numpy as np
import pandas as pd
from src.modules.utilities import type_check

class TestTypeCheck(unittest.TestCase):
    
    def test_int(self):
        self.assertTrue(type_check(int, 5))
        self.assertFalse(type_check(int, 'foo'))

    def test_float(self):
        self.assertTrue(type_check(float, 5.0))
        self.assertFalse(type_check(float, 'nut'))

    def test_numpy_int32(self):
        self.assertTrue(type_check(np.int32, 5))
        self.assertFalse(type_check(np.int32, 'mesh'))

    def test_pandas_string_dytpe(self):
        self.assertTrue(type_check(pd.StringDtype(), 'BBB'))
        self.assertFalse(type_check(pd.StringDtype(), 123))

    def test_unexpected_type(self):
        self.assertFalse(type_check(np.int32, {'key': 'value'}))


if __name__ == '__main':
    unittest.main()
