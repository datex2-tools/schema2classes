"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from schema2validataclass.common.helper import to_snake_case

from .base_outputs import (
    BooleanBaseOutput,
    EnumBaseOutput,
    FloatBaseOutput,
    IntegerBaseOutput,
    ListBaseOutput,
    NestedObjectBaseOutput,
    ObjectBaseOutput,
    RegexBaseOutput,
    StringBaseOutput,
)


class PydanticRenderMixin(ABC):
    """Mixin providing Pydantic V2-specific rendering for BaseOutput subclasses."""

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
class PydanticBooleanOutput(PydanticRenderMixin, BooleanBaseOutput):
    pass


@dataclass(kw_only=True, init=False)
class PydanticIntegerOutput(PydanticRenderMixin, IntegerBaseOutput):
    def render(self) -> str:
        constraints = self._build_constraints()
        if constraints:
            return self._render_annotated('int', constraints)
        return super().render()

    def _build_constraints(self) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        if self.minimum is not None:
            constraints['ge'] = self.minimum
        if self.maximum is not None:
            constraints['le'] = self.maximum
        return constraints

    def _render_annotated(self, base_type: str, constraints: dict[str, Any]) -> str:
        params = ', '.join(f'{k}={v}' for k, v in constraints.items())
        type_output = f'Annotated[{base_type}, Field({params})]'
        if not self.required:
            type_output = f'{type_output} | None'
            return f'{self.key}: {type_output} = None'
        return f'{self.key}: {type_output}'

    def get_imports(self) -> list[str]:
        if self._build_constraints():
            return ['typing.Annotated', 'pydantic.Field']
        return []


@dataclass(kw_only=True, init=False)
class PydanticFloatOutput(PydanticRenderMixin, FloatBaseOutput):
    def render(self) -> str:
        constraints = self._build_constraints()
        if constraints:
            return self._render_annotated('float', constraints)
        return super().render()

    def _build_constraints(self) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        if self.minimum is not None:
            constraints['ge'] = self.minimum
        if self.maximum is not None:
            constraints['le'] = self.maximum
        return constraints

    def _render_annotated(self, base_type: str, constraints: dict[str, Any]) -> str:
        params = ', '.join(f'{k}={v}' for k, v in constraints.items())
        type_output = f'Annotated[{base_type}, Field({params})]'
        if not self.required:
            type_output = f'{type_output} | None'
            return f'{self.key}: {type_output} = None'
        return f'{self.key}: {type_output}'

    def get_imports(self) -> list[str]:
        if self._build_constraints():
            return ['typing.Annotated', 'pydantic.Field']
        return []


@dataclass(kw_only=True, init=False)
class PydanticStringOutput(PydanticRenderMixin, StringBaseOutput):
    def render(self) -> str:
        constraints = self._build_constraints()
        if constraints:
            return self._render_annotated(constraints)
        return super().render()

    def _build_constraints(self) -> dict[str, Any]:
        constraints: dict[str, Any] = {}
        if self.minLength is not None:
            constraints['min_length'] = self.minLength
        if self.maxLength is not None:
            constraints['max_length'] = self.maxLength
        return constraints

    def _render_annotated(self, constraints: dict[str, Any]) -> str:
        params = ', '.join(f'{k}={v}' for k, v in constraints.items())
        type_output = f'Annotated[str, Field({params})]'
        if not self.required:
            type_output = f'{type_output} | None'
            return f'{self.key}: {type_output} = None'
        return f'{self.key}: {type_output}'

    def get_imports(self) -> list[str]:
        if self._build_constraints():
            return ['typing.Annotated', 'pydantic.Field']
        return []


@dataclass(kw_only=True, init=False)
class PydanticEnumOutput(PydanticRenderMixin, EnumBaseOutput):
    def get_imports(self) -> list[str]:
        return [f'.{to_snake_case(self.name)}.{self.name}']


@dataclass(kw_only=True, init=False)
class PydanticRegexOutput(PydanticRenderMixin, RegexBaseOutput):
    def render(self) -> str:
        type_output = f"Annotated[str, Field(pattern=r'{self.pattern}')]"
        if not self.required:
            type_output = f'{type_output} | None'
            return f'{self.key}: {type_output} = None'
        return f'{self.key}: {type_output}'

    def get_imports(self) -> list[str]:
        return ['typing.Annotated', 'pydantic.Field']


@dataclass(kw_only=True, init=False)
class PydanticListOutput(PydanticRenderMixin, ListBaseOutput):
    def get_imports(self) -> list[str]:
        return self.output.get_imports()


@dataclass(kw_only=True, init=False)
class PydanticNestedObjectOutput(PydanticRenderMixin, NestedObjectBaseOutput):
    def get_imports(self) -> list[str]:
        return [f'.{to_snake_case(self.name)}.{self.name}']


@dataclass(kw_only=True, init=False)
class PydanticObjectOutput(ObjectBaseOutput):
    def get_imports(self) -> list[str]:
        raw_imports: list[str] = ['pydantic.BaseModel']
        if self.get_field_mapping():
            raw_imports += ['pydantic.model_validator', 'typing.Any']
        for output in self.outputs:
            raw_imports += output.get_imports()
        return self._format_imports(raw_imports)


PYDANTIC_OUTPUT_CLASSES = {
    'boolean': PydanticBooleanOutput,
    'integer': PydanticIntegerOutput,
    'float': PydanticFloatOutput,
    'string': PydanticStringOutput,
    'enum': PydanticEnumOutput,
    'regex': PydanticRegexOutput,
    'list': PydanticListOutput,
    'nested_object': PydanticNestedObjectOutput,
}
