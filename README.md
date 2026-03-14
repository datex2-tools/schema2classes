# schema2validataclass

A Python code generator that transforms [JSON Schema](https://json-schema.org/) definitions into Python dataclasses with [`@validataclass`](https://github.com/binary-butterfly/validataclass) decorators and Enum classes.

## Features

- Parses JSON Schema files, including `$ref` references across multiple files and remote schemas (HTTP)
- Generates `@validataclass`-decorated dataclasses with typed validator fields
- Generates Python `Enum` classes for JSON Schema `enum` types
- Supports nested objects, arrays, references with property overrides, and schema inheritance
- Handles required vs. optional fields with configurable `UnsetValue` / `None` defaults
- Resolves schema dependency graphs automatically by following `$ref` chains

## Requirements

- Python >= 3.12
- [Jinja2](https://jinja.palletsprojects.com/) (runtime)
- [validataclass](https://github.com/binary-butterfly/validataclass) (used in generated code)

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

## Configuration

The generator is configured via the `Config` dataclass in `src/schema2validataclass/config.py`. Key options:

| Option                    | Default          | Description                                                                                            |
|---------------------------|------------------|--------------------------------------------------------------------------------------------------------|
| `unset_value_output`      | `UNSET_VALUE`    | How optional fields are represented: `UNSET_VALUE` (uses `UnsetValue`) or `NONE` (uses `None`)         |
| `object_postfix`          | `'Input'`        | Suffix appended to generated class names (e.g. `ClosureInformation` becomes `ClosureInformationInput`) |
| `set_validataclass_mixin` | `True`           | Whether generated classes inherit from `ValidataclassMixin`                                            |
| `ignored_uris`            | `[]`             | List of field URI paths to skip during generation                                                      |
| `header`                  | Copyright header | Python file header prepended to every generated file                                                   |

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
