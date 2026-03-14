"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass, field
from enum import Enum


class UnsetValueOutput(Enum):
    NONE = 'NONE'
    UNSET_VALUE = 'UNSET_VALUE'

    def to_type_output(self) -> str:
        return {self.NONE: 'None', self.UNSET_VALUE: 'UnsetValueType'}.get(self)

    def to_output(self) -> str:
        return {self.NONE: 'None', self.UNSET_VALUE: 'UnsetValue'}.get(self)


@dataclass(kw_only=True)
class Config:
    unset_value_output: UnsetValueOutput = UnsetValueOutput.UNSET_VALUE
    object_postfix: str = 'Input'
    ignored_uris: list[str] = field(
        default_factory=list,
    )
    set_validataclass_mixin: bool = True
    header: str = '''"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
    '''
