"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re

CAMEL_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')


def get_class_name(name: str) -> str:
    name = clean_string(name)

    if '_' in name:
        name = upper_camel_case(name)

    return name


def get_enum_name(name: str) -> str:
    return clean_string(name).upper()


def clean_string(value: str) -> str:
    """
    Removes invalid characters
    """
    value = re.sub(r'[^a-zA-Z0-9_]', '', value)
    while len(value) and value[0].isdigit():
        value = value[1:]
    return value


def upper_camel_case(snake_str: str) -> str:
    return ''.join(x.capitalize() for x in snake_str.lower().split('_'))


def is_camel_case(value):
    return value != value.lower() and value != value.upper() and '_' not in value


def to_snake_case(value: str) -> str:
    return CAMEL_CASE_PATTERN.sub('_', value).lower()
