"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from pathlib import Path

from .helper import to_snake_case


class UriType(Enum):
    FILE = 'FILE'
    URL = 'URL'


class URI:
    type: UriType
    json_path: str
    url: str | None = None
    file_path: Path | None = None

    def __init__(self, url: str | None = None, file_path: Path | None = None, json_path: str = ''):
        if url is None and file_path is None:
            raise ValueError('Either url or file_path must be provided')

        if file_path is not None:
            self.type = UriType.FILE
            self.file_path = file_path.absolute()
        else:
            self.type = UriType.URL
            self.url = url

        self.json_path = json_path

    @classmethod
    def from_uri(cls, uri: 'URI', append_path: str) -> 'URI':
        if not append_path.startswith('/'):
            append_path = f'/{append_path}'
        return cls(
            file_path=uri.file_path,
            url=uri.url,
            json_path=f'{uri.json_path}{append_path}',
        )

    @classmethod
    def from_uri_without_json_path(cls, uri: 'URI') -> 'URI':
        return cls(file_path=uri.file_path, url=uri.url)

    @classmethod
    def from_reference(cls, uri: 'URI', reference: str) -> 'URI':
        # TODO: how to determine the difference between a path within a file and a new files root object?
        if '#' in reference:
            location, json_path = reference.split('#')
        else:
            location = reference
            json_path = '/'

        if reference.startswith('http'):
            return cls(url=location, json_path=json_path)

        # TODO: local file path in a schema via URL
        if location.startswith('/'):
            return cls(file_path=Path(location), json_path=json_path)

        return cls(file_path=Path(uri.file_path.parent, location), json_path=json_path)

    @property
    def key(self) -> str:
        if self.json_path == '':
            if self.type == UriType.FILE:
                return to_snake_case(self.file_path.stem)
            return to_snake_case(self.url)

        return self.json_path.split('/')[-1]

    def __repr__(self) -> str:
        if self.type == UriType.FILE:
            result = f'{self.file_path.as_uri()}'
        else:
            result = self.url
        if self.json_path:
            return f'{result}#{self.json_path}'
        return result

    def __hash__(self) -> int:
        return hash((self.url if self.type == UriType.URL else self.file_path, self.json_path))

    def __eq__(self, other: 'URI') -> bool:
        if self.type != other.type:
            return False

        if self.json_path != other.json_path:
            return False

        if self.type == UriType.FILE:
            return self.file_path == other.file_path

        return self.url == other.url
