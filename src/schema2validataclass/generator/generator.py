"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from jinja2 import Environment, PackageLoader, select_autoescape

from schema2validataclass.config import Config
from schema2validataclass.schema.outputs import EnumOutput, ObjectOutput


class Generator:
    def __init__(self, config: Config):
        self.env = Environment(loader=PackageLoader('schema2validataclass'), autoescape=select_autoescape())
        self.config = config

    def generate_init(self) -> str:
        return self.env.get_template('init.jinja2').render(config=self.config)

    def generate_validataclass(self, model: ObjectOutput) -> str:
        return self.env.get_template('validataclass.jinja2').render(model=model, config=self.config)

    def generate_enum(self, model: EnumOutput) -> str:
        return self.env.get_template('enum.jinja2').render(model=model, config=self.config)
