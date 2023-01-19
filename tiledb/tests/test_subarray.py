import io
import numpy as np
import pytest

import tiledb
from tiledb import TileDBError
from tiledb.tests.common import DiskTestCase


class SubarrayTest(DiskTestCase):
    def test_add_range(self):
        dim1 = tiledb.Dim("row", domain=(1, 10))
        dim2 = tiledb.Dim("col", domain=(1, 10))
        dom = tiledb.Domain(dim1, dim2)
        att = tiledb.Attr("val", dtype=np.uint64)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,))
        uri = self.path("dense_array")
        tiledb.Array.create(uri, schema)

        with tiledb.open(uri, "w") as array:
            array[1:5, 1:5] = np.reshape(np.arange(1, 17, dtype=np.float64), (4, 4))

        with tiledb.open(uri, "r") as array:
            subarray1 = tiledb.Subarray(array)
            assert subarray1.nrange(0) == 1
            assert subarray1.nrange(1) == 1

            subarray1.add_dim_range(0, (1, 2))
            subarray1.add_dim_range(0, (4, 4))
            assert subarray1.nrange(0) == 2

    def test_add_ranges_basic(self):
        uri = self.path("test_pyquery_basic")
        with tiledb.from_numpy(uri, np.random.rand(4)) as A:
            pass

        with tiledb.open(uri) as array:
            subarray = tiledb.Subarray(array)

            subarray.add_ranges([[(0, 3)]])

            with self.assertRaises(TileDBError):
                subarray.add_ranges([[(0, 3.0)]])

            subarray.add_ranges([[(0, np.int32(3))]])

            with self.assertRaises(TileDBError):
                subarray.add_ranges([[(3, "a")]])

            with self.assertRaisesRegex(
                TileDBError,
                "Failed to cast dim range '\\(1.2344, 5.6789\\)' to dim type UINT64.*$",
            ):
                subarray.add_ranges([[(1.2344, 5.6789)]])

            with self.assertRaisesRegex(
                TileDBError,
                "Failed to cast dim range '\\('aa', 'bbbb'\\)' to dim type UINT64.*$",
            ):
                subarray.add_ranges([[("aa", "bbbb")]])
