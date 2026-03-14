"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
import logging
import subprocess  # noqa: S404
from pathlib import Path
from urllib.request import urlopen

from schema2validataclass.common.helper import to_snake_case
from schema2validataclass.common.uri import URI, UriType
from schema2validataclass.config import Config, OutputFormat, PostProcessing
from schema2validataclass.generator.generator import Generator
from schema2validataclass.schema.base_outputs import EnumBaseOutput, NestedObjectBaseOutput, ObjectBaseOutput
from schema2validataclass.schema.dataclass_outputs import DATACLASS_OUTPUT_CLASSES, DataclassObjectOutput
from schema2validataclass.schema.models import BaseField, Object, Schema
from schema2validataclass.schema.validataclass_outputs import VALIDATACLASS_OUTPUT_CLASSES, ValidataclassObjectOutput

logger = logging.getLogger(__name__)


class App:
    config: Config
    generator: Generator

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.generator = Generator(config=self.config)

    def generate(self, schema_uri: URI, output_path: Path):
        if self.config.output_format == OutputFormat.DATACLASS:
            object_output_class = DataclassObjectOutput
            output_classes = DATACLASS_OUTPUT_CLASSES
        else:
            object_output_class = ValidataclassObjectOutput
            output_classes = VALIDATACLASS_OUTPUT_CLASSES

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

        main_object_output = object_output_class(
            main_schema.contained_object,
            config=self.config,
            referencable_fields=referencable_fields,
            output_classes=output_classes,
        )

        object_outputs: list[ObjectBaseOutput] = [main_object_output]
        for referencable_field in referencable_fields.values():
            if isinstance(referencable_field, Object):
                object_output = object_output_class(
                    referencable_field,
                    config=self.config,
                    referencable_fields=referencable_fields,
                    output_classes=output_classes,
                )
                object_outputs.append(object_output)

        if self.config.detect_looping_references:
            self._remove_looping_references(object_outputs)

        enum_outputs: list[EnumBaseOutput] = []
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
                object_file.write(self.generator.generate_object(object_output))

        self._run_post_processing(output_path)

    @staticmethod
    def _remove_looping_references(object_outputs: list[ObjectBaseOutput]) -> None:
        # Build import graph: object_name → set of referenced object_names
        import_graph: dict[str, set[str]] = {}
        for object_output in object_outputs:
            referenced_names: set[str] = set()
            for output in object_output.outputs:
                if isinstance(output, NestedObjectBaseOutput):
                    referenced_names.add(output.name)
            import_graph[object_output.name] = referenced_names

        # Detect back-edges via DFS
        back_edges: set[tuple[str, str]] = set()
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            in_stack.add(node)
            for neighbor in import_graph.get(node, set()):
                if neighbor in in_stack:
                    back_edges.add((node, neighbor))
                elif neighbor not in visited:
                    dfs(node=neighbor)
            in_stack.discard(node)

        for name in import_graph:
            if name not in visited:
                dfs(node=name)

        # Remove outputs that create back-edges
        for object_output in object_outputs:
            outputs_to_remove = [
                output
                for output in object_output.outputs
                if isinstance(output, NestedObjectBaseOutput) and (object_output.name, output.name) in back_edges
            ]
            for output in outputs_to_remove:
                logger.warning(f'removing looping reference {output.name} from {object_output.name}')
                object_output.outputs.remove(output)

    def _run_post_processing(self, output_path: Path) -> None:
        post_processing_commands = {
            PostProcessing.RUFF_FORMAT: ['ruff', 'format'],
            PostProcessing.RUFF_CHECK: ['ruff', 'check', '--fix'],
        }
        for step in self.config.post_processing:
            command = post_processing_commands[step]
            for file_path in output_path.glob('*.py'):
                try:
                    subprocess.run(  # noqa: S603
                        [*command, str(file_path)],
                        check=True,
                        capture_output=True,
                    )
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    logger.warning(f'post-processing {step.value} failed on {file_path.name}: {e}')

    @staticmethod
    def read_schema(uri: URI) -> dict:
        if uri.type == UriType.URL:
            with urlopen(uri.url) as response:  # noqa: S310
                response_data = response.read()
            return json.loads(response_data)

        with uri.file_path.open() as schema_file:
            return json.load(schema_file)
