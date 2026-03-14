"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml


class UnsetValueOutput(Enum):
    NONE = 'NONE'
    UNSET_VALUE = 'UNSET_VALUE'

    def to_type_output(self) -> str:
        return {self.NONE: 'None', self.UNSET_VALUE: 'UnsetValueType'}.get(self)

    def to_output(self) -> str:
        return {self.NONE: 'None', self.UNSET_VALUE: 'UnsetValue'}.get(self)


class OutputFormat(Enum):
    VALIDATACLASS = 'validataclass'
    DATACLASS = 'dataclass'


class PostProcessing(Enum):
    RUFF_FORMAT = 'ruff-format'
    RUFF_CHECK = 'ruff-check'


@dataclass(kw_only=True)
class Config:
    unset_value_output: UnsetValueOutput = UnsetValueOutput.UNSET_VALUE
    object_postfix: str = 'Input'
    ignored_uris: list[str] = field(
        default_factory=list,
    )
    output_format: OutputFormat = OutputFormat.VALIDATACLASS
    set_validataclass_mixin: bool = True
    post_processing: list[PostProcessing] = field(
        default_factory=lambda: [PostProcessing.RUFF_FORMAT, PostProcessing.RUFF_CHECK],
    )
    header: str = '''"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
    '''

    @classmethod
    def from_yaml(cls, path: Path) -> 'Config':
        with path.open() as f:
            data = yaml.safe_load(f) or {}

        if 'unset_value_output' in data:
            data['unset_value_output'] = UnsetValueOutput(data['unset_value_output'])
        if 'output_format' in data:
            data['output_format'] = OutputFormat(data['output_format'])
        if 'post_processing' in data:
            data['post_processing'] = [PostProcessing(v) for v in data['post_processing']]

        return cls(**data)
