"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from schema2classes.common.helper import get_class_name, get_enum_name
from schema2classes.common.uri import URI
from schema2classes.config import Config
from schema2classes.schema.models import (
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
    original_key: str | None = None
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

        # Rename properties that conflict with Python reserved words
        if self.key in self.config.renamed_properties:
            self.original_key = self.key
            self.key = f'{self.key}_'
        else:
            self.original_key = None

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

    @abstractmethod
    def render(self) -> str:
        """Renders the full field line."""

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

    @abstractmethod
    def get_imports(self) -> list[str]:
        """Returns list of imports needed for this output."""


@dataclass(kw_only=True, init=False)
class BooleanBaseOutput(BaseOutput, ABC):
    @staticmethod
    def get_type() -> str:
        return 'bool'


@dataclass(kw_only=True, init=False)
class IntegerBaseOutput(BaseOutput, ABC):
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


@dataclass(kw_only=True, init=False)
class FloatBaseOutput(BaseOutput, ABC):
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
        return 'float'


@dataclass(kw_only=True, init=False)
class StringBaseOutput(BaseOutput, ABC):
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


@dataclass(kw_only=True, init=False)
class EnumBaseOutput(BaseOutput, ABC):
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

    def render_enum_values(self) -> list[str]:
        result: list[str] = []
        for enum_value in self.enum_values:
            result.append(f"{get_enum_name(enum_value)} = '{enum_value}'")
        return result


@dataclass(kw_only=True, init=False)
class RegexBaseOutput(BaseOutput, ABC):
    pattern: str

    def apply_field(self, field: String) -> None:
        super().apply_field(field)
        if field.pattern is not None:
            self.pattern = field.pattern

    @staticmethod
    def get_type() -> str:
        return 'str'


@dataclass(kw_only=True, init=False)
class ListBaseOutput(BaseOutput, ABC):
    output: BaseOutput

    minItems: int | None = None
    maxItems: int | None = None

    def __init__(
        self,
        field: Array,
        config: Config,
        referencable_fields: dict[URI, BaseField],
        output_classes: dict,
        **kwargs,
    ):
        super().__init__(
            field, config=config, referencable_fields=referencable_fields, output_classes=output_classes, **kwargs
        )

        item_field = field.items

        # Original references are for applying inheritance
        references: list[Reference] = []

        while isinstance(item_field, Reference):
            references.append(item_field)
            item_field = follow_reference(item_field, referencable_fields=referencable_fields)

        output_type = determine_output(item_field, output_classes)
        self.output = output_type(
            field=item_field,
            config=config,
            referencable_fields=referencable_fields,
            output_classes=output_classes,
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


@dataclass(kw_only=True, init=False)
class NestedObjectBaseOutput(BaseOutput, ABC):
    name: str

    def __init__(self, field: Object, config: Config, **kwargs):
        super().__init__(field, config=config, **kwargs)
        if field.title is not None:
            self.name = f'{get_class_name(field.title)}{self.config.object_postfix}'
        else:
            self.name = f'{get_class_name(field.uri.key)}{self.config.object_postfix}'

    def get_type(self) -> str:
        return self.name


@dataclass(kw_only=True, init=False)
class ObjectBaseOutput(ABC):
    name: str
    description: str | None
    outputs: list[BaseOutput]
    config: Config

    def __init__(self, field: Object, config: Config, referencable_fields: dict[URI, BaseField], output_classes: dict):
        self.config = config
        self.description = field.description

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

            if field is None:
                continue

            output_type = determine_output(field, output_classes)
            output = output_type(
                field=field,
                config=config,
                referencable_fields=referencable_fields,
                output_classes=output_classes,
                references=references,
            )

            self.outputs.append(output)

    @abstractmethod
    def get_imports(self) -> list[str]:
        """Returns formatted import lines."""

    @staticmethod
    def _format_imports(raw_imports: list[str]) -> list[str]:
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

    def get_field_mapping(self) -> dict[str, str]:
        mapping = {}
        for output in self.outputs:
            if output.original_key is not None:
                mapping[output.original_key] = output.key
        return mapping

    def get_enum_outputs(self) -> list[EnumBaseOutput]:
        enum_outputs: list[EnumBaseOutput] = []

        for output in self.outputs:
            if isinstance(output, EnumBaseOutput):
                enum_outputs.append(output)
            if isinstance(output, ListBaseOutput) and isinstance(output.output, EnumBaseOutput):
                enum_outputs.append(output.output)
            if isinstance(output, ObjectBaseOutput):
                enum_outputs += output.get_enum_outputs()

        return enum_outputs


def follow_reference(reference: Reference, referencable_fields: dict[URI, BaseField]) -> BaseField | None:
    if reference.to not in referencable_fields:
        logger.warning(f'Could not find referenced field: {reference.to}')
        return None

    return referencable_fields[reference.to]


def determine_output(field: BaseField, output_classes: dict) -> type[BaseOutput]:
    if isinstance(field, Boolean):
        return output_classes['boolean']
    if isinstance(field, Integer):
        return output_classes['integer']
    if isinstance(field, Number):
        return output_classes['float']
    if isinstance(field, String) and field.pattern is not None:
        return output_classes['regex']
    if isinstance(field, String) and field.pattern is None:
        return output_classes['string']
    if isinstance(field, Enum):
        return output_classes['enum']
    if isinstance(field, Array):
        return output_classes['list']
    if isinstance(field, Object):
        return output_classes['nested_object']
    raise ValueError(f'Unsupported field type: {field}')
