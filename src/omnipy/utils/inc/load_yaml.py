''' load_yaml.py  The purpose of this program is to load the config file.
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
from py_vyrtuous.utils.inc.setup_logging import logger

import os
import traceback
import yaml

def load_yaml(path_to_file):
    try:
        if not os.path.exists(path_to_file):
            return {}
        with open(path_to_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception as e:
        logger.error(f'An error occurred while loading the YAML file: {e}')
        logger.debug(traceback.format_exc())
        return {}
