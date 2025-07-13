''' load_content.py  The purpose of this program is to load the raw contents of files.
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
from omnipy.utils.inc.setup_logging import logger
from os.path import exists

import os

def load_contents(path_to_file):
    if not exists(path_to_file):
        raise FileNotFoundError(f'The file at `{path_to_file}` does not exist.')
    try:
        with open(path_to_file, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f'An error occurred while reading the file: {e}')
        raise IOError(f'An error occurred while reading the file: {e}')
