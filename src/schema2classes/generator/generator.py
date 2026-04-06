"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from jinja2 import Environment, PackageLoader, select_autoescape

from schema2classes.config import Config, OutputFormat
from schema2classes.output.base_outputs import EnumBaseOutput, ObjectBaseOutput


class Generator:
    def __init__(self, config: Config):
        self.env = Environment(loader=PackageLoader('schema2classes'), autoescape=select_autoescape())
        self.config = config

    def generate_init(self) -> str:
        return self.env.get_template('init.jinja2').render(config=self.config)

    def generate_object(self, model: ObjectBaseOutput) -> str:
        templates = {
            OutputFormat.VALIDATACLASS: 'validataclass.jinja2',
            OutputFormat.DATACLASS: 'dataclass.jinja2',
            OutputFormat.PYDANTIC: 'pydantic.jinja2',
        }
        template = templates[self.config.output_format]
        return self.env.get_template(template).render(model=model, config=self.config)

    def generate_enum(self, model: EnumBaseOutput) -> str:
        return self.env.get_template('enum.jinja2').render(model=model, config=self.config)
