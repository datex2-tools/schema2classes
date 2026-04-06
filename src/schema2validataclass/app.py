"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
import logging
import subprocess  # noqa: S404
from pathlib import Path
from typing import Callable
from urllib.request import urlopen

from schema2validataclass.common.helper import to_snake_case
from schema2validataclass.common.uri import URI, UriType
from schema2validataclass.config import Config, OutputFormat, PostProcessing
from schema2validataclass.generator.generator import Generator
from schema2validataclass.output.base_outputs import (
    BaseOutput,
    EnumBaseOutput,
    ListBaseOutput,
    NestedObjectBaseOutput,
    ObjectBaseOutput,
)
from schema2validataclass.output.dataclass_outputs import DATACLASS_OUTPUT_CLASSES, DataclassObjectOutput
from schema2validataclass.output.pydantic_outputs import PYDANTIC_OUTPUT_CLASSES, PydanticObjectOutput
from schema2validataclass.output.validataclass_outputs import VALIDATACLASS_OUTPUT_CLASSES, ValidataclassObjectOutput
from schema2validataclass.schema.models import Array, BaseField, Object, Reference, Schema, get_reference_uris

logger = logging.getLogger(__name__)


class App:
    config: Config
    generator: Generator

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.generator = Generator(config=self.config)

    def generate(self, schema_uri: URI, output_path: Path):
        output_format_map = {
            OutputFormat.VALIDATACLASS: (ValidataclassObjectOutput, VALIDATACLASS_OUTPUT_CLASSES),
            OutputFormat.DATACLASS: (DataclassObjectOutput, DATACLASS_OUTPUT_CLASSES),
            OutputFormat.PYDANTIC: (PydanticObjectOutput, PYDANTIC_OUTPUT_CLASSES),
        }
        object_output_class, output_classes = output_format_map[self.config.output_format]

        # Schema file cache: each file is read and parsed only once
        schema_cache: dict[URI, Schema] = {}

        main_schema = self.get_or_load_schema(schema_cache, schema_uri)

        # Build referencable_fields by walking the reference tree from the main schema
        referencable_fields: dict[URI, BaseField] = {}

        # Main schema's contained_object properties are always included
        for field in main_schema.properties:
            referencable_fields[field.uri] = field

        # Tree traversal: follow references starting from the main schema's properties
        refs_to_process: list[URI] = get_reference_uris(main_schema.properties)
        processed_refs: set[URI] = set()

        while refs_to_process:
            ref_uri = refs_to_process.pop()
            if ref_uri in processed_refs:
                continue
            processed_refs.add(ref_uri)

            base_uri = URI.from_uri_without_json_path(ref_uri)
            schema = self.get_or_load_schema(schema_cache, base_uri)

            field = schema.get_field_by_uri(ref_uri)
            if field is None:
                logger.warning(f'Referenced field not found: {ref_uri}')
                continue

            if ref_uri in referencable_fields:
                logger.warning(f'Duplicate field: {ref_uri}')
                continue
            referencable_fields[ref_uri] = field

            # Discover further references from this field
            refs_to_process.extend(get_reference_uris([field]))

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

    def _is_ignored_reference(self, ref_uri: URI) -> bool:
        ref_str = str(ref_uri)
        for pattern in self.config.ignore_references:
            if ref_str.endswith(pattern):
                return True
        return False

    def get_or_load_schema(self, schema_cache: dict[URI, Schema], base_uri: URI) -> Schema:
        if base_uri not in schema_cache:
            logger.info(f'parsing {base_uri} ...')
            schema_dict = self.read_schema(base_uri)
            schema = Schema(schema_dict, uri=base_uri)
            self._apply_ignore_paths(schema)
            self._apply_ignore_references(schema)
            schema_cache[base_uri] = schema
        return schema_cache[base_uri]

    def _apply_ignore_paths(self, schema: Schema) -> None:
        if not self.config.ignore_paths:
            return
        if schema.contained_object:
            self._filter_object_properties(schema.contained_object, self._is_ignored_path)
        for definition in schema.definitions:
            if isinstance(definition, Object):
                self._filter_object_properties(definition, self._is_ignored_path)

    def _apply_ignore_references(self, schema: Schema) -> None:
        if not self.config.ignore_references:
            return
        if schema.contained_object:
            self._filter_object_properties(schema.contained_object, self._is_ignored_reference_property)
        for definition in schema.definitions:
            if isinstance(definition, Object):
                self._filter_object_properties(definition, self._is_ignored_reference_property)

    def _filter_object_properties(self, obj: Object, predicate: Callable) -> None:
        obj.properties = [prop for prop in obj.properties if not predicate(prop)]
        for prop in obj.properties:
            if isinstance(prop, Object):
                self._filter_object_properties(prop, predicate)
            if isinstance(prop, Array) and isinstance(prop.items, Object):
                self._filter_object_properties(prop.items, predicate)

    def _is_ignored_path(self, field: BaseField) -> bool:
        uri_str = str(field.uri)
        for pattern in self.config.ignore_paths:
            if uri_str.endswith(pattern):
                logger.info(f'skipping ignored path {field.uri}')
                return True
        return False

    def _is_ignored_reference_property(self, field: BaseField) -> bool:
        ref = field
        if isinstance(ref, Array):
            ref = ref.items
        if not isinstance(ref, Reference):
            return False
        return self._is_ignored_reference(ref.to)

    @staticmethod
    def _get_referenced_object_name(output: BaseOutput) -> str | None:
        if isinstance(output, NestedObjectBaseOutput):
            return output.name
        if isinstance(output, ListBaseOutput) and isinstance(output.output, NestedObjectBaseOutput):
            return output.output.name
        return None

    @staticmethod
    def _remove_looping_references(object_outputs: list[ObjectBaseOutput]) -> None:
        # Build import graph: object_name → set of referenced object_names
        import_graph: dict[str, set[str]] = {}
        for object_output in object_outputs:
            referenced_names: set[str] = set()
            for output in object_output.outputs:
                ref_name = App._get_referenced_object_name(output)
                if ref_name is not None:
                    referenced_names.add(ref_name)
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
                if (ref_name := App._get_referenced_object_name(output)) is not None
                and (object_output.name, ref_name) in back_edges
            ]
            for output in outputs_to_remove:
                ref_name = App._get_referenced_object_name(output)
                logger.warning(f'removing looping reference {ref_name} from {object_output.name}')
                object_output.outputs.remove(output)

    def _run_post_processing(self, output_path: Path) -> None:
        post_processing_commands = {
            PostProcessing.RUFF_FORMAT: ['ruff', 'format'],
            PostProcessing.RUFF_CHECK: ['ruff', 'check', '--fix'],
        }
        for step in self.config.post_processing:
            command = post_processing_commands[step]
            try:
                subprocess.run(  # noqa: S603
                    [*command, str(output_path)],
                    check=True,
                    capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.warning(f'post-processing {step.value} failed: {e}')

    @staticmethod
    def read_schema(uri: URI) -> dict:
        if uri.type == UriType.URL:
            with urlopen(uri.url) as response:  # noqa: S310
                response_data = response.read()
            return json.loads(response_data)

        with uri.file_path.open() as schema_file:
            return json.load(schema_file)
