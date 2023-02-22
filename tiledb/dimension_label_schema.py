from typing import Any, Optional, Sequence, Union

import numpy as np

import tiledb.cc as lt

from .ctx import Ctx, default_ctx
from .data_order import DataOrder
from .datatypes import DataType
from .filter import Filter, FilterList


class DimLabelSchema(lt.DimensionLabelSchema):
    def __init__(
        self,
        dim_index: np.uint32,
        order: str = "increasing",
        label_dtype: np.dtype = np.uint64,
        dim_dtype: np.dtype = np.uint64,
        dim_tile: Any = None,
        label_filters: Union[FilterList, Sequence[Filter]] = None,
        ctx: Ctx = None,
    ):
        self._ctx = ctx or default_ctx()

        # Get DataType and DataOrder objects
        _label_order = DataOrder[order]
        _label_dtype = DataType.from_numpy(label_dtype)
        _dim_dtype = DataType.from_numpy(dim_dtype)

        # Convert the tile extent (if set)
        if dim_tile is not None:
            if np.issubdtype(_dim_dtype.np_dtype, np.bytes_):
                raise TypeError(
                    "invalid tile extent, cannot set a tile a string dimension"
                )
            _dim_tile = _dim_dtype.cast_tile_extent(dim_tile)
        else:
            _dim_tile = None

        # Create the PyBind superclass
        if label_filters is None:
            super().__init__(
                dim_index,
                _dim_dtype.tiledb_type,
                _dim_tile,
                _label_order.value,
                _label_dtype.tiledb_type,
            )
        else:
            _label_filters = (
                label_filters
                if isinstance(label_filters, FilterList)
                else FilterList(label_filters)
            )
            super().__init__(
                dim_index,
                _dim_dtype.tiledb_type,
                _dim_tile,
                _label_order.value,
                _label_dtype.tiledb_type,
                _label_filters,
            )

    @property
    def dim_dtype(self) -> np.dtype:
        """Numpy dtype object representing the dimension type"""
        return DataType.from_tiledb(self._dim_dtype).np_dtype

    @property
    def dim_tile(self) -> Optional[np.generic]:
        """The tile extent of the dimension for the dimension label.

        :rtype: numpy scalar of np.timedelta64

        """
        tile_extent = self._dim_tile_extent
        if tile_extent is None:
            return None
        dim_dtype = DataType.from_tiledb(self._dim_dtype)
        return (
            None if tile_extent is None else dim_dtype.uncast_tile_extent(tile_extent)
        )

    @property
    def label_filters(self) -> Optional[FilterList]:
        """FilterList of the labels"""
        return (
            FilterList.from_pybind11(self._ctx, self._label_filters)
            if self._has_label_filters
            else None
        )

    @property
    def label_dtype(self) -> np.dtype:
        """Numpy dtype object representing the label type"""
        return DataType.from_tiledb(self._label_dtype).np_dtype

    @property
    def label_order(self) -> str:
        """Sort order of the labels on the dimension label"""
        return DataOrder(self._label_order).name
