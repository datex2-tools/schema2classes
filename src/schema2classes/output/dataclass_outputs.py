"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from schema2classes.common.helper import to_snake_case

from .base_outputs import (
    BooleanBaseOutput,
    DateTimeBaseOutput,
    EmailBaseOutput,
    EnumBaseOutput,
    FloatBaseOutput,
    IntegerBaseOutput,
    ListBaseOutput,
    NestedObjectBaseOutput,
    ObjectBaseOutput,
    RegexBaseOutput,
    StringBaseOutput,
    TimeBaseOutput,
    UriBaseOutput,
)


class DataclassRenderMixin(ABC):
    """Mixin providing dataclass-specific rendering for BaseOutput subclasses."""

    key: str
    required: bool
    default: Any

    # Provided by BaseOutput subclasses
    get_type: Callable[[], str]

    def render(self) -> str:
        type_output = self.get_type()
        if self.required:
            return f'{self.key}: {type_output}'
        type_output = f'{type_output} | None'
        if self.default is None:
            return f'{self.key}: {type_output} = None'
        if isinstance(self.default, str):
            return f"{self.key}: {type_output} = '{self.default}'"
        return f'{self.key}: {type_output} = {self.default}'

    def get_imports(self) -> list[str]:
        return []


@dataclass(kw_only=True, init=False)
class DataclassBooleanOutput(DataclassRenderMixin, BooleanBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassIntegerOutput(DataclassRenderMixin, IntegerBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassFloatOutput(DataclassRenderMixin, FloatBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassStringOutput(DataclassRenderMixin, StringBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassEnumOutput(DataclassRenderMixin, EnumBaseOutput):
    def get_imports(self) -> list[str]:
        return [f'.{to_snake_case(self.name)}.{self.name}']


@dataclass(kw_only=True, init=False)
class DataclassRegexOutput(DataclassRenderMixin, RegexBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassDateTimeOutput(DataclassRenderMixin, DateTimeBaseOutput):
    def get_imports(self) -> list[str]:
        return ['datetime.datetime']


@dataclass(kw_only=True, init=False)
class DataclassTimeOutput(DataclassRenderMixin, TimeBaseOutput):
    def get_imports(self) -> list[str]:
        return ['datetime.time']


@dataclass(kw_only=True, init=False)
class DataclassEmailOutput(DataclassRenderMixin, EmailBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassUriOutput(DataclassRenderMixin, UriBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class DataclassListOutput(DataclassRenderMixin, ListBaseOutput):
    def get_imports(self) -> list[str]:
        return self.output.get_imports()


@dataclass(kw_only=True, init=False)
class DataclassNestedObjectOutput(DataclassRenderMixin, NestedObjectBaseOutput):
    def get_imports(self) -> list[str]:
        return [f'.{to_snake_case(self.name)}.{self.name}']


@dataclass(kw_only=True, init=False)
class DataclassObjectOutput(ObjectBaseOutput):
    def get_imports(self) -> list[str]:
        raw_imports: list[str] = ['dataclasses.dataclass']
        for output in self.outputs:
            raw_imports += output.get_imports()
        return self._format_imports(raw_imports)


DATACLASS_OUTPUT_CLASSES = {
    'boolean': DataclassBooleanOutput,
    'integer': DataclassIntegerOutput,
    'float': DataclassFloatOutput,
    'string': DataclassStringOutput,
    'datetime': DataclassDateTimeOutput,
    'time': DataclassTimeOutput,
    'email': DataclassEmailOutput,
    'uri': DataclassUriOutput,
    'enum': DataclassEnumOutput,
    'regex': DataclassRegexOutput,
    'list': DataclassListOutput,
    'nested_object': DataclassNestedObjectOutput,
}
