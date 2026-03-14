"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from schema2validataclass.common.helper import get_class_name, get_enum_name, to_snake_case
from schema2validataclass.common.uri import URI
from schema2validataclass.config import Config, UnsetValueOutput

from .models import (
    Array,
    BaseField,
    Boolean,
    Enum,
    Integer,
    Number,
    Object,
    Reference,
    String,
)

logger = logging.getLogger(__name__)


@dataclass(kw_only=True, init=False)
class BaseOutput(ABC):
    field: BaseField
    config: Config
    key: str
    title: str | None = None
    description: str | None = None
    default: Any | None = None
    required: bool = True

    def __init__(self, field: BaseField, config: Config, references: list[Reference], **kwargs):
        self.field = field
        self.config = config
        self.apply_field(field)

        # We need to apply inheritance in reverse order
        for reference in reversed(references):
            self.apply_field(reference)

    def apply_field(self, field: BaseField) -> None:
        self.key = field.uri.key

        if field.default is not None:
            self.default = field.default
        if field.title is not None:
            self.title = field.title
        if field.description is not None:
            self.description = field.description
        if field.required is not None:
            self.required = field.required
            # Some schema set default values despite the fact that the value is required, so we unset it in output
            self.default = None

    def render(self) -> str:
        return self._add_render_default(self.render_validator())

    @abstractmethod
    def render_validator(self) -> str:
        """
        Renders the validator
        """

    @staticmethod
    def _render_parameters(parameters: dict[str, Any]) -> str:
        output: list[str] = []
        for key, value in parameters.items():
            if value is None:
                continue

            if isinstance(value, int) or isinstance(value, float):
                output.append(f'{key}={value}')
                continue

            output.append(f"{key}='{value}'")
        return ', '.join(output)

    @staticmethod
    def get_type() -> str:
        return 'Any'

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

    def get_imports(self) -> list[str]:
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
class BooleanOutput(BaseOutput):
    @staticmethod
    def get_type() -> str:
        return 'bool'

    def render_validator(self) -> str:
        return 'BooleanValidator()'

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.BooleanValidator']


@dataclass(kw_only=True, init=False)
class IntegerOutput(BaseOutput):
    minimum: int | None = None
    maximum: int | None = None

    def apply_field(self, field: Integer):
        super().apply_field(field)

        if field.minimum is not None:
            self.minimum = field.minimum
        if self.maximum:
            self.maximum = field.maximum

    @staticmethod
    def get_type() -> str:
        return 'int'

    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_value': self.minimum, 'max_value': self.maximum})

        return f'IntegerValidator({parameters})'

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.IntegerValidator']


@dataclass(kw_only=True, init=False)
class FloatOutput(BaseOutput):
    minimum: float | None = None
    maximum: float | None = None

    def apply_field(self, field: Number):
        super().apply_field(field)

        if field.minimum is not None:
            self.minimum = field.minimum
        if self.maximum:
            self.maximum = field.maximum

    @staticmethod
    def get_type() -> str:
        return 'int'

    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_value': self.minimum, 'max_value': self.maximum})

        return f'FloatValidator({parameters})'

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.FloatValidator']


@dataclass(kw_only=True, init=False)
class StringOutput(BaseOutput):
    minLength: int | None = None
    maxLength: int | None = None

    def apply_field(self, field: String):
        super().apply_field(field)
        if field.minLength is not None:
            self.minLength = field.minLength
        if field.maxLength is not None:
            self.maxLength = field.maxLength

    @staticmethod
    def get_type() -> str:
        return 'str'

    def render_validator(self) -> str:
        parameters = self._render_parameters({'min_length': self.minLength, 'max_length': self.maxLength})

        return f'StringValidator({parameters})'

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.StringValidator']


@dataclass(kw_only=True, init=False)
class EnumOutput(BaseOutput):
    name: str
    enum_values: list[str]

    def __init__(self, field: Enum, **kwargs):
        super().__init__(field, **kwargs)

        # We don't set this in apply_field by purpose, because this should just happen for the actuall Enum, not for
        # References
        self.enum_values = field.enum

        if field.title is not None:
            self.name = get_class_name(field.title)
        else:
            self.name = get_class_name(field.uri.key)

    def apply_field(self, field: Enum):
        super().apply_field(field)

        # TODO: overwriting enums is actually a new enum and will break thinks. Not sure how to handle that
        if isinstance(field, Reference) and field.enum is not None:
            raise ValueError('Enum is overwritten, which will break the output')

    def get_type(self) -> str:
        return self.name

    def render_validator(self) -> str:
        return f'EnumValidator({self.name})'

    def render_enum_values(self) -> list[str]:
        result: list[str] = []
        for enum_value in self.enum_values:
            result.append(f'{get_enum_name(enum_value)} = "{enum_value}"')
        return result

    def get_imports(self) -> list[str]:
        return super().get_imports() + [
            'validataclass.validators.EnumValidator',
            f'.{to_snake_case(self.name)}.{self.name}',
        ]


@dataclass(kw_only=True, init=False)
class RegexOutput(BaseOutput):
    pattern: str

    def apply_field(self, field: String) -> None:
        super().apply_field(field)
        if field.pattern is not None:
            self.pattern = field.pattern

    @staticmethod
    def get_type() -> str:
        return 'str'

    def render_validator(self) -> str:
        return f"RegexValidator(pattern=r'{self.pattern}')"

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.RegexValidator']


@dataclass(kw_only=True, init=False)
class ListOutput(BaseOutput):
    output: BaseOutput

    minItems: int | None = None
    maxItems: int | None = None

    def __init__(
        self,
        field: Array,
        config: Config,
        referencable_fields: dict[URI, BaseField],
        **kwargs,
    ):
        super().__init__(field, config=config, referencable_fields=referencable_fields, **kwargs)

        item_field = field.items

        # Original references are for applying inheritance
        references: list[Reference] = []

        while isinstance(item_field, Reference):
            references.append(item_field)
            item_field = follow_reference(item_field, referencable_fields=referencable_fields)

        output_type = determine_output(item_field)
        self.output = output_type(
            field=item_field,
            config=config,
            referencable_fields=referencable_fields,
            references=references,
        )

    def apply_field(self, field: Array) -> None:
        super().apply_field(field)
        if field.minItems is not None:
            self.minItems = field.minItems
        if field.maxItems is not None:
            self.maxItems = field.maxItems

    def get_type(self) -> str:
        return f'list[{self.output.get_type()}]'

    def render_validator(self) -> str:
        return f'ListValidator({self.output.render_validator()})'

    def get_imports(self) -> list[str]:
        return super().get_imports() + ['validataclass.validators.ListValidator'] + self.output.get_imports()


@dataclass(kw_only=True, init=False)
class DataclassOutput(BaseOutput):
    name: str

    def __init__(self, field: Object, config: Config, **kwargs):
        super().__init__(field, config=config, **kwargs)
        if field.title is not None:
            self.name = f'{get_class_name(field.title)}{self.config.object_postfix}'
        else:
            self.name = f'{get_class_name(field.uri.key)}{self.config.object_postfix}'

    def render_validator(self) -> str:
        return f'DataclassValidator({self.name})'

    def get_imports(self) -> list[str]:
        return super().get_imports() + [
            'validataclass.validators.DataclassValidator',
            f'.{to_snake_case(self.name)}.{self.name}',
        ]

    def get_type(self) -> str:
        return self.name


@dataclass(kw_only=True, init=False)
class ObjectOutput:
    name: str
    outputs: list[BaseOutput]
    config: Config

    def __init__(self, field: Object, config: Config, referencable_fields: dict[URI, BaseField]):
        self.config = config

        if field.title is not None:
            self.name = f'{get_class_name(field.title)}{self.config.object_postfix}'
        else:
            self.name = f'{get_class_name(field.uri.key)}{self.config.object_postfix}'

        self.outputs = []
        for field in field.properties:
            # Original references are for applying inheritance
            references: list[Reference] = []

            while isinstance(field, Reference):
                references.append(field)
                field = follow_reference(field, referencable_fields=referencable_fields)

            if str(field.uri.json_path) in self.config.ignored_uris:
                continue

            if field is None:
                continue

            output_type = determine_output(field)
            output = output_type(
                field=field,
                config=config,
                referencable_fields=referencable_fields,
                references=references,
            )

            self.outputs.append(output)

    def get_imports(self) -> list[str]:
        # Aggregate imports
        raw_imports: list[str] = ['validataclass.dataclasses.validataclass']
        for output in self.outputs:
            raw_imports += output.get_imports()

        # Make imports unique
        raw_imports = list(set(raw_imports))

        # Sort imports by base module
        main_exports: list[str] = []
        sub_imports: dict[str, list[str]] = defaultdict(list)
        for raw_import in raw_imports:
            splitted_imports = raw_import.split('.')
            if len(splitted_imports) == 1:
                main_exports.append(raw_import)
                continue

            sub_imports['.'.join(splitted_imports[:-1])].append(splitted_imports[-1])

        result_imports: list[str] = [*main_exports]
        for key, value in sub_imports.items():
            result_imports.append(f'from {key} import {", ".join(value)}')

        return result_imports

    def get_enum_outputs(self) -> list[EnumOutput]:
        enum_outputs: list[EnumOutput] = []

        for output in self.outputs:
            if isinstance(output, EnumOutput):
                enum_outputs.append(output)
            if isinstance(output, ListOutput) and isinstance(output.output, EnumOutput):
                enum_outputs.append(output.output)
            if isinstance(output, ObjectOutput):
                enum_outputs += output.get_enum_outputs()

        return enum_outputs


def follow_reference(reference: Reference, referencable_fields: dict[URI, BaseField]) -> BaseField | None:
    if reference.to not in referencable_fields:
        logger.warning(f'Could not find referenced field: {reference.to}')
        return None

    return referencable_fields[reference.to]


def determine_output(field: BaseField) -> type[BaseOutput]:
    if isinstance(field, Boolean):
        return BooleanOutput
    if isinstance(field, Integer):
        return IntegerOutput
    if isinstance(field, Number):
        return FloatOutput
    if isinstance(field, String) and field.pattern is not None:
        return RegexOutput
    if isinstance(field, String) and field.pattern is None:
        return StringOutput
    if isinstance(field, Enum):
        return EnumOutput
    if isinstance(field, Array):
        return ListOutput
    if isinstance(field, Object):
        return DataclassOutput
    raise ValueError(f'Unsupported field type: {field}')
