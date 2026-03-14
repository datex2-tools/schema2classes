"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
import logging
from pathlib import Path
from urllib.request import urlopen

from schema2validataclass.common.helper import to_snake_case
from schema2validataclass.common.uri import URI, UriType
from schema2validataclass.config import Config
from schema2validataclass.generator.generator import Generator
from schema2validataclass.schema.models import BaseField, Object, Schema
from schema2validataclass.schema.outputs import EnumOutput, ObjectOutput

logger = logging.getLogger(__name__)


class App:
    config: Config
    generator: Generator

    def __init__(self):
        self.config = Config()
        self.generator = Generator(config=self.config)

    def generate(self, schema_uri: URI, output_path: Path):
        main_schema_dict = self.read_schema(schema_uri)

        main_schema = Schema(main_schema_dict, uri=schema_uri)
        schema_objects: dict[URI, Schema] = {schema_uri: main_schema}
        schemas_to_load: list[URI] = main_schema.get_reference_base_uris()
        while len(schemas_to_load):
            child_schema = schemas_to_load.pop()
            logger.info(f'parsing {child_schema} ...')
            child_schema_dict = self.read_schema(child_schema)
            child_schema_object = Schema(child_schema_dict, uri=child_schema)
            schema_objects[child_schema] = child_schema_object
            for reference_uri in child_schema_object.get_reference_base_uris():
                if reference_uri not in schema_objects:
                    schemas_to_load.append(reference_uri)

        # Check Reference Uniqueness and generate referencable fields
        referencable_fields: dict[URI, BaseField] = {}
        for schema_object in list(schema_objects.values()):
            for field in schema_object.properties + schema_object.definitions:
                if field.uri in referencable_fields:
                    logger.warning(f'Duplicate field: {field.uri}')
                    continue
                referencable_fields[field.uri] = field

        main_object_output = ObjectOutput(
            main_schema.contained_object,
            config=self.config,
            referencable_fields=referencable_fields,
        )

        object_outputs: list[ObjectOutput] = [main_object_output]
        for referencable_field in referencable_fields.values():
            if isinstance(referencable_field, Object):
                object_output = ObjectOutput(
                    referencable_field,
                    config=self.config,
                    referencable_fields=referencable_fields,
                )
                object_outputs.append(object_output)

        enum_outputs: list[EnumOutput] = []
        for object_output in object_outputs:
            enum_outputs += object_output.get_enum_outputs()

        init_path = Path(output_path, '__init__.py')
        with init_path.open('w') as init_file:
            init_file.write(self.generator.generate_init())

        for enum_output in enum_outputs:
            enum_path = Path(output_path, f'{to_snake_case(enum_output.name)}.py')
            with enum_path.open('w') as enum_file:
                enum_file.write(self.generator.generate_enum(enum_output))

        for object_output in object_outputs:
            object_path = Path(output_path, f'{to_snake_case(object_output.name)}.py')
            with object_path.open('w') as object_file:
                object_file.write(self.generator.generate_validataclass(object_output))

    @staticmethod
    def read_schema(uri: URI) -> dict:
        if uri.type == UriType.URL:
            with urlopen(uri.url) as response:  # noqa: S310
                response_data = response.read()
            return json.loads(response_data)

        with uri.file_path.open() as schema_file:
            return json.load(schema_file)
