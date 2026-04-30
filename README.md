# schema2classes

A Python code generator that transforms [JSON Schema](https://json-schema.org/) definitions into Python [`@validataclass`](https://github.com/binary-butterfly/validataclass)-decorated dataclasses, plain `@dataclass` classes, or [Pydantic](https://docs.pydantic.dev/) `BaseModel` classes, along with Enum classes.


## Features

- Parses JSON Schema files, including `$ref` references across multiple files and remote schemas (HTTP)
- Three output formats: `@validataclass` (with validators), plain `@dataclass`, or Pydantic `BaseModel`
- Generates Python `Enum` classes for JSON Schema `enum` types
- Supports nested objects, arrays, references with property overrides, and schema inheritance
- Handles required vs. optional fields with configurable `UnsetValue` / `None` defaults
- Resolves schema dependency graphs automatically by following `$ref` chains
- Detects and breaks circular `$ref` references to prevent import cycles
- Ignore specific references or schema paths to exclude unwanted types from output
- Configurable via YAML configuration file

## Requirements

- Python >= 3.12
- [Jinja2](https://jinja.palletsprojects.com/) (template rendering)
- [PyYAML](https://pyyaml.org/) (configuration file parsing)
- [Ruff](https://docs.astral.sh/ruff/) (post-processing of generated files)
- [validataclass](https://github.com/binary-butterfly/validataclass) (used in generated code, only needed for `validataclass` output)
- [Pydantic](https://docs.pydantic.dev/) (used in generated code, only needed for `pydantic` output)


## Installation

```bash
uv add schema2classes
```

Or with pip:

```bash
pip install schema2classes
```


## Usage

```bash
schema2classes <schema_path> <output_path>
```

**Arguments:**

| Argument      | Description                                            |
|---------------|--------------------------------------------------------|
| `schema_path` | Path to the root JSON Schema file                      |
| `output_path` | Directory where generated Python files will be written |

**Example:**

```bash
schema2classes input/schema.json output/
```

This reads the schema, recursively resolves all `$ref` references to other schema files, and generates:

- An `__init__.py` file
- One Python file per `enum` type (e.g. `day_enum.py`)
- One Python file per `object` type (e.g. `closure_information_input.py`)


### Generated output examples

Given a JSON Schema object with optional boolean and string fields, the generator produces different output depending on the configured `output_format`.

For enum schemas, the output is the same across all formats:

```python
from enum import Enum

class DayEnum(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
```


#### `validataclass` output (default)

```python
from validataclass.validators import StringValidator, BooleanValidator
from validataclass.helpers import UnsetValue, UnsetValueType
from validataclass.dataclasses import Default, validataclass
from validataclass.dataclasses import ValidataclassMixin

@validataclass
class ClosureInformationInput(ValidataclassMixin):
    permananentlyClosed: bool | UnsetValueType = BooleanValidator(), Default(UnsetValue)
    temporarilyClosed: bool | UnsetValueType = BooleanValidator(), Default(UnsetValue)
    closedFrom: str | UnsetValueType = StringValidator(), Default(UnsetValue)
```

This is the default output format. It uses the [`validataclass`](https://github.com/binary-butterfly/validataclass) library for runtime validation. Optional fields use `UnsetValue` by default (configurable via `unset_value_output`). Classes optionally inherit from `ValidataclassMixin` (configurable via `set_validataclass_mixin`).


#### `dataclass` output

Set `output_format: dataclass` in your config file (see [Configuration](#configuration) below):

```yaml
output_format: dataclass
```

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class ClosureInformationInput:
    permananentlyClosed: bool | None = None
    temporarilyClosed: bool | None = None
    closedFrom: str | None = None
```

This produces plain Python `@dataclass` classes with no external dependencies. Optional fields default to `None`, required fields are bare type annotations. The `set_validataclass_mixin` and `unset_value_output` config options have no effect.


#### `pydantic` output

Set `output_format: pydantic` in your config file:

```yaml
output_format: pydantic
```

```python
from pydantic import BaseModel

class ClosureInformationInput(BaseModel):
    permananentlyClosed: bool | None = None
    temporarilyClosed: bool | None = None
    closedFrom: str | None = None
```

This produces [Pydantic V2](https://docs.pydantic.dev/) `BaseModel` classes. Constraints like `minimum`, `maximum`, `minLength`, `maxLength`, and `pattern` are rendered using `Annotated[type, Field(...)]`. Properties that conflict with Python reserved words are renamed with a trailing underscore and a `@model_validator(mode='before')` is generated to map the original names. The `set_validataclass_mixin` and `unset_value_output` config options have no effect.

### Loop detection

JSON Schemas can contain circular `$ref` references (e.g. `A → B → C → A`). Without intervention, this would produce Python files with circular imports that fail at runtime.

The generator automatically detects and breaks these cycles. It builds a directed import graph of all generated classes, then runs a depth-first search to find back-edges (the references that close a cycle). When a back-edge is found, the offending field is removed from the generated class and a warning is logged.

For example, given schemas where `SecondObject` references `ThirdObject` and `ThirdObject` references back to `SecondObject`, the generator removes the back-reference from `ThirdObject` to break the cycle.

This works for both direct object references and references inside arrays (lists).

Loop detection is enabled by default. To disable it:

```yaml
detect_looping_references: false
```


## Configuration

The generator can be configured via a YAML file passed with the `-c` / `--config` flag:

```bash
schema2classes input/schema.json output/ -c config.yaml
```

All options have sensible defaults and are optional. Example `config.yaml`:

```yaml
output_format: validataclass
object_postfix: Input
unset_value_output: UNSET_VALUE
set_validataclass_mixin: true
detect_looping_references: true
post_processing:
  - ruff-format
  - ruff-check
ignore_references: []
ignore_paths: []
renamed_properties: []
header: |
  """
  Custom copyright header.
  """
```


### Options

| Option                      | Default                     | Description                                                                                                         |
|-----------------------------|-----------------------------|---------------------------------------------------------------------------------------------------------------------|
| `output_format`             | `validataclass`             | Output style: `validataclass`, `dataclass`, or `pydantic`                                                           |
| `unset_value_output`        | `UNSET_VALUE`               | How optional fields are represented: `UNSET_VALUE` (uses `UnsetValue`) or `NONE` (uses `None`). Validataclass only. |
| `object_postfix`            | `'Input'`                   | Suffix appended to generated class names (e.g. `ClosureInformation` becomes `ClosureInformationInput`)              |
| `set_validataclass_mixin`   | `true`                      | Whether generated validataclass classes inherit from `ValidataclassMixin`. Validataclass only.                      |
| `detect_looping_references` | `true`                      | Detect and remove circular `$ref` chains to prevent import cycles                                                   |
| `post_processing`           | `[ruff-format, ruff-check]` | Post-processing steps to run on generated files                                                                     |
| `ignore_references`         | `[]`                        | List of `$ref` target URIs to ignore (suffix match). Properties referencing these are removed from their parent.    |
| `ignore_paths`              | `[]`                        | List of schema paths to ignore (suffix match). The property at the given path is removed during loading.            |
| `renamed_properties`        | Python keywords             | List of property names that get a trailing `_` to avoid conflicts. Defaults to all Python reserved keywords.        |
| `header`                    | Copyright header            | Python file header prepended to every generated file                                                                |


### `ignore_references` vs `ignore_paths`

Both options remove properties from the generated output, but they match differently:

- **`ignore_references`** matches the **target** of a `$ref`. For example, `third_schema.json#/definitions/IgnoredObject` removes every property that references that definition, regardless of where the property appears.
- **`ignore_paths`** matches the **location** of a property in the schema. For example, `second_schema.json#/definitions/SecondObject/properties/IgnoredObject` removes only that specific property from `SecondObject`, even if other objects also reference the same definition.

Both use suffix matching, so you can omit leading path components.


## Supported JSON Schema types

| JSON Schema type              | validataclass                                                   | dataclass                                            | pydantic                                             |
|-------------------------------|-----------------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| `boolean`                     | `BooleanValidator()`                                            | `bool`                                               | `bool`                                               |
| `integer`                     | `IntegerValidator(min_value=..., ...)`                          | `int`                                                | `int` / `Annotated[int, Field(ge=..., ...)]`         |
| `number`                      | `FloatValidator(min_value=..., ...)`                            | `float`                                              | `float` / `Annotated[float, Field(ge=..., ...)]`     |
| `string`                      | `StringValidator(min_length=..., ...)`                          | `str`                                                | `str` / `Annotated[str, Field(min_length=..., ...)]` |
| `string` with `pattern`       | `RegexValidator(pattern=r'...')`                                | `str`                                                | `Annotated[str, Field(pattern=r'...')]`              |
| `string` format `date-time`   | `DateTimeValidator()`                                           | `datetime`                                           | `datetime`                                           |
| `string` format `time`        | `TimeValidator()`                                               | `time`                                               | `time`                                               |
| `string` format `email`       | `EmailValidator()`                                              | `str`                                                | `EmailStr`                                           |
| `string` format `uri`         | `UrlValidator()`                                                | `str`                                                | `AnyUrl`                                             |
| `enum`                        | `EnumValidator(EnumClassName)`                                  | `EnumClassName`                                      | `EnumClassName`                                      |
| `array`                       | `ListValidator(inner_validator)`                                | `list[inner_type]`                                   | `list[inner_type]`                                   |
| `object`                      | `DataclassValidator(ClassName)`                                 | `ClassName`                                          | `ClassName`                                          |
| `$ref`                        | Resolved to the referenced type with property overrides applied |


## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Sync project with dev dependencies
uv sync --group dev
```

For running without installing, use the development script which adds `src/` to the Python path:

```bash
uv run python dev/run.py <schema_path> <output_path>
```

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run pre-commit hooks
pre-commit run --all-files

# Run tests
uv run pytest
```


## License

MIT - see LICENSE.txt for details.

Copyright 2025-2026 [binary butterfly GmbH](https://binary-butterfly.de)
