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


@dataclass
class ImageMetadata:
    '''Dataclass for storing information about a FantasyMap. 
    '''
    url: str
    rid: str
    title: str

    # Set default values
    path: str = ''
    width: int = 0
    height: int = 0
    cell_width: int = 0
    cell_height: int = 0
    columns: int = 1
    rows: int = 1
    uid: str = ''
    parent_uid: str = ''
    is_shard: bool = False
    bboxes: Sequence[BBox] = field(default_factory=list)
    cell_offset_x: int = 0
    cell_offset_y: int = 0

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
