# schema2validataclass

A Python code generator that transforms [JSON Schema](https://json-schema.org/) definitions into Python [`@validataclass`](https://github.com/binary-butterfly/validataclass)-decorated dataclasses or plain `@dataclass` classes, along with Enum classes.

## Features

- Parses JSON Schema files, including `$ref` references across multiple files and remote schemas (HTTP)
- Generates `@validataclass`-decorated dataclasses with typed validator fields, or plain `@dataclass` classes
- Generates Python `Enum` classes for JSON Schema `enum` types
- Supports nested objects, arrays, references with property overrides, and schema inheritance
- Handles required vs. optional fields with configurable `UnsetValue` / `None` defaults
- Resolves schema dependency graphs automatically by following `$ref` chains
- Detects and breaks circular `$ref` references to prevent import cycles
- Configurable via YAML configuration file

## Requirements

- Python >= 3.12
- [Jinja2](https://jinja.palletsprojects.com/) (template rendering)
- [PyYAML](https://pyyaml.org/) (configuration file parsing)
- [Ruff](https://docs.astral.sh/ruff/) (post-processing of generated files)
- [validataclass](https://github.com/binary-butterfly/validataclass) (used in generated code, not needed for `@dataclass` output)

## Installation

```bash
pip install schema2validataclass
```

## Usage

```bash
schema2validataclass <schema_path> <output_path>
```

**Arguments:**

| Argument      | Description                                            |
|---------------|--------------------------------------------------------|
| `schema_path` | Path to the root JSON Schema file                      |
| `output_path` | Directory where generated Python files will be written |

**Example:**

```bash
schema2validataclass input/schema.json output/
```

This reads the schema, recursively resolves all `$ref` references to other schema files, and generates:

- An `__init__.py` file
- One Python file per `enum` type (e.g. `day_enum.py`)
- One Python file per `object` type (e.g. `closure_information_input.py`)

### Generated output example

Given a JSON Schema object with optional boolean and string fields, the generator produces:

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

For enum schemas:

```python
from enum import Enum

class DayEnum(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
```

### `@dataclass` output

Instead of generating `@validataclass`-decorated classes, the generator can produce plain Python `@dataclass` classes. This is useful when you don't need runtime validation and want lightweight data containers with no external dependencies beyond the standard library.

Set `output_format: dataclass` in your config file (see [Configuration](#configuration) below):

```yaml
output_format: dataclass
```

The same schema that produces the validataclass example above generates:

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class ClosureInformationInput:
    permananentlyClosed: bool | None = None
    temporarilyClosed: bool | None = None
    closedFrom: str | None = None
```

Key differences from `@validataclass` output:

- Uses Python's built-in `@dataclass(kw_only=True)` decorator
- Fields are plain type annotations without validators
- Optional fields default to `None` instead of `UnsetValue`
- Required fields are bare type annotations (e.g. `name: str`)
- No dependency on the `validataclass` package
- `set_validataclass_mixin` and `unset_value_output` config options have no effect

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
schema2validataclass input/schema.json output/ -c config.yaml
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
ignored_uris: []
header: |
  """
  Custom copyright header.
  """
```

### Options

| Option                      | Default                     | Description                                                                                            |
|-----------------------------|-----------------------------|--------------------------------------------------------------------------------------------------------|
| `output_format`             | `validataclass`             | Output style: `validataclass` (with validators) or `dataclass` (plain Python dataclasses)              |
| `unset_value_output`        | `UNSET_VALUE`               | How optional fields are represented: `UNSET_VALUE` (uses `UnsetValue`) or `NONE` (uses `None`)         |
| `object_postfix`            | `'Input'`                   | Suffix appended to generated class names (e.g. `ClosureInformation` becomes `ClosureInformationInput`) |
| `set_validataclass_mixin`   | `true`                      | Whether generated validataclass classes inherit from `ValidataclassMixin`                              |
| `detect_looping_references` | `true`                      | Detect and remove circular `$ref` chains to prevent import cycles                                      |
| `post_processing`           | `[ruff-format, ruff-check]` | Post-processing steps to run on generated files                                                        |
| `ignored_uris`              | `[]`                        | List of field URI paths to skip during generation                                                      |
| `header`                    | Copyright header            | Python file header prepended to every generated file                                                   |

## Supported JSON Schema types

| JSON Schema type        | Generated validator                                             |
|-------------------------|-----------------------------------------------------------------|
| `boolean`               | `BooleanValidator()`                                            |
| `integer`               | `IntegerValidator(min_value=..., max_value=...)`                |
| `number`                | `FloatValidator(min_value=..., max_value=...)`                  |
| `string`                | `StringValidator(min_length=..., max_length=...)`               |
| `string` with `pattern` | `RegexValidator(pattern=r'...')`                                |
| `enum`                  | `EnumValidator(EnumClassName)`                                  |
| `array`                 | `ListValidator(inner_validator)`                                |
| `object`                | `DataclassValidator(ClassName)`                                 |
| `$ref`                  | Resolved to the referenced type with property overrides applied |

## Development

```bash
# Install with development dependencies
pip install -e ".[testing]"
```

For running without installing, use the development script which adds `src/` to the Python path:

```bash
python dev/run.py <schema_path> <output_path>
```

```bash
# Lint
ruff check .

# Format
ruff format .

# Run pre-commit hooks
pre-commit run --all-files

# Run tests
pytest
```

## License

MIT - see LICENSE.txt for details.

Copyright 2025-2026 [binary butterfly GmbH](https://binary-butterfly.de)
