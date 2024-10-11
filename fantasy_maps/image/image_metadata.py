# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

from dataclasses import dataclass, field
from typing import Mapping, Union, Sequence


@dataclass
class BBox:
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    label: str = 'grid_cell'

    def to_dict(self) -> Mapping[str, Union[float, str]]:
        return {
            'xMin': self.x_min,
            'xMax': self.x_max,
            'yMin': self.y_min,
            'yMax': self.y_max,
            'displayName': self.label,
        }

    def __str__(self):
        return str(self.to_dict())


class ImageMetadata:
    '''Dataclass for storing information about a FantasyMap. 
    '''
    _columns: int = 1
    _rows: int = 1
    _width: int = 0
    _height: int = 0

    url: str
    rid: str
    title: str

    # Set default values
    path: str = ''

    uid: str = ''
    parent_uid: str = ''
    is_shard: bool = False
    bboxes: Sequence[BBox] = field(default_factory=list)
    cell_width: int = 0
    cell_height: int = 0
    cell_offset_x: int = 0
    cell_offset_y: int = 0
    is_usable: bool = True

    def __init__(self, url: str, rid: str, title: str, **kwargs):
        self.url = url
        self.rid = rid
        self.title = title

        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Mapping[str, Union[str, int, float, None]]:
        return self.__dict__

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_vtt(self):
        if (self.columns > 1 and self.cell_width == 0):
            self.cell_width = int(self.width / self.columns)

        if (self.rows > 1 and self.cell_height == 0):
            self.cell_height = int(self.height / self.rows)

        return {
            'imageHeight': int(self.height),
            'imageWidth': int(self.width),
            'cellHeight': self.cell_height,
            'cellWidth': self.cell_width,
            'cellsOffsetX': self.cell_offset_x,
            'cellsOffsetY': self.cell_offset_y,
        }

    def _calculate_cell_dimensions(self):
        if not (self._width and self._height and self._rows and self._columns):
            return

        self.cell_width = int(self._width / self._columns)
        self.cell_height = int(self._height / self._rows)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w
        self._calculate_cell_dimensions()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, h):
        self._height = h
        self._calculate_cell_dimensions()

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, c):
        self._columns = c
        self._calculate_cell_dimensions()

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, r):
        self._rows = r
        self._calculate_cell_dimensions()
