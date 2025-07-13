''' increment_version.py  The purpose of this program is to provide persistent versioning from cd ../.
    Copyright (C) 2024  github.com/brandongrahamcobb

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
from omnipy.utils.inc.helpers import *
from omnipy.utils.inc.setup_logging import logger
from typing import Any, Dict

import toml
import yaml

def increment_version(toml_path: str = PATH_TOML):
    try:
        with open(toml_path, 'r') as file:
            pyproject = toml.load(file)
        current_version = pyproject.get('tool', {}).get('poetry', {}).get('version', '0.0.0')
        major, minor, patch = map(int, current_version.split('.'))
        patch += 1
        if patch >= 10:
            patch = 0
            minor += 1
        if minor >= 10:
            minor = 0
            major += 1
        new_version = f'{major}.{minor}.{patch}'
        pyproject['tool']['poetry']['version'] = new_version
        with open(toml_path, 'w') as file:
            toml.dump(pyproject, file)
    except Exception as e:
        logger.error(f'An error occurred during version increment: {e}')
        raise
