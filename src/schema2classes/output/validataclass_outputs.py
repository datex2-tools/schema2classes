"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from schema2classes.common.helper import to_snake_case
from schema2classes.config import Config, UnsetValueOutput

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


class ValidataclassRenderMixin(ABC):
    """Mixin providing validataclass-specific rendering for BaseOutput subclasses."""

    key: str
    required: bool
    default: Any
    config: Config

    # Provided by BaseOutput subclasses
    get_type: Callable[[], str]
    _render_parameters: Callable[[dict[str, Any]], str]

    @abstractmethod
    def render_validator(self) -> str: ...

    def render(self) -> str:
        return self._add_render_default(self.render_validator())

    def _add_render_default(self, validator: str) -> str:
        type_output = self.get_type()
        if not self.required:
            type_output = f'{type_output} | {self.config.unset_value_output.to_type_output()}'
        result = f'{self.key}: {type_output} = {validator}'

        if self.default is None:
            if self.required:
                return result
            return f'{result}, Default({self.config.unset_value_output.to_output()})'

        if isinstance(self.default, str):
            return f"{result}, Default('{self.default}')"

        return f'{result}, Default({self.default})'

    def _get_base_imports(self) -> list[str]:
        if self.required:
            return []

        imports: list[str] = ['validataclass.dataclasses.Default']
        if self.config.unset_value_output == UnsetValueOutput.UNSET_VALUE:
            imports += [
                'validataclass.helpers.UnsetValue',
                'validataclass.helpers.UnsetValueType',
            ]
        return imports


@dataclass(kw_only=True, init=False)
class ValidataclassBooleanOutput(ValidataclassRenderMixin, BooleanBaseOutput):
    def render_validator(self) -> str:
        return 'BooleanValidator()'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.BooleanValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassIntegerOutput(ValidataclassRenderMixin, IntegerBaseOutput):
    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_value': self.minimum, 'max_value': self.maximum})
        return f'IntegerValidator({parameters})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.IntegerValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassFloatOutput(ValidataclassRenderMixin, FloatBaseOutput):
    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_value': self.minimum, 'max_value': self.maximum})
        return f'FloatValidator({parameters})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.FloatValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassStringOutput(ValidataclassRenderMixin, StringBaseOutput):
    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_length': self.minLength, 'max_length': self.maxLength})
        return f'StringValidator({parameters})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.StringValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassEnumOutput(ValidataclassRenderMixin, EnumBaseOutput):
    def render_validator(self) -> str:
        return f'EnumValidator({self.name})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + [
            'validataclass.validators.EnumValidator',
            f'.{to_snake_case(self.name)}.{self.name}',
        ]


@dataclass(kw_only=True, init=False)
class ValidataclassRegexOutput(ValidataclassRenderMixin, RegexBaseOutput):
    def render_validator(self) -> str:
        return f"RegexValidator(pattern=r'{self.pattern}')"

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.RegexValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassDateTimeOutput(ValidataclassRenderMixin, DateTimeBaseOutput):
    def render_validator(self) -> str:
        return 'DateTimeValidator()'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['datetime.datetime', 'validataclass.validators.DateTimeValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassTimeOutput(ValidataclassRenderMixin, TimeBaseOutput):
    def render_validator(self) -> str:
        return 'TimeValidator()'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['datetime.time', 'validataclass.validators.TimeValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassEmailOutput(ValidataclassRenderMixin, EmailBaseOutput):
    def render_validator(self) -> str:
        return 'EmailValidator()'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.EmailValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassUriOutput(ValidataclassRenderMixin, UriBaseOutput):
    def render_validator(self) -> str:
        return 'UrlValidator()'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.UrlValidator']


@dataclass(kw_only=True, init=False)
class ValidataclassListOutput(ValidataclassRenderMixin, ListBaseOutput):
    def render_validator(self) -> str:
        return f'ListValidator({self.output.render_validator()})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + ['validataclass.validators.ListValidator'] + self.output.get_imports()


@dataclass(kw_only=True, init=False)
class ValidataclassNestedObjectOutput(ValidataclassRenderMixin, NestedObjectBaseOutput):
    def render_validator(self) -> str:
        return f'DataclassValidator({self.name})'

    def get_imports(self) -> list[str]:
        return self._get_base_imports() + [
            'validataclass.validators.DataclassValidator',
            f'.{to_snake_case(self.name)}.{self.name}',
        ]


@dataclass(kw_only=True, init=False)
class ValidataclassObjectOutput(ObjectBaseOutput):
    def get_imports(self) -> list[str]:
        raw_imports: list[str] = ['validataclass.dataclasses.validataclass']
        for output in self.outputs:
            raw_imports += output.get_imports()
        return self._format_imports(raw_imports)


VALIDATACLASS_OUTPUT_CLASSES = {
    'boolean': ValidataclassBooleanOutput,
    'integer': ValidataclassIntegerOutput,
    'float': ValidataclassFloatOutput,
    'string': ValidataclassStringOutput,
    'datetime': ValidataclassDateTimeOutput,
    'time': ValidataclassTimeOutput,
    'email': ValidataclassEmailOutput,
    'uri': ValidataclassUriOutput,
    'enum': ValidataclassEnumOutput,
    'regex': ValidataclassRegexOutput,
    'list': ValidataclassListOutput,
    'nested_object': ValidataclassNestedObjectOutput,
}
