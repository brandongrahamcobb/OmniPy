''' setup_logging.py  The purpose of this program is to setup_logging for Py_Py_vyrtuous, the Discord bot.
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

from os import makedirs
from os.path import dirname, exists
from typing import Any, Dict

global logger

import logging
import logging.handlers

logger = logging.getLogger(__name__)

def setup_logging(config: Dict[str, Any], path_log) -> None:
    logging_level = config['logging_level'].upper()
    logging.basicConfig(level=getattr(logging, logging_level))
    if not exists(dirname(path_log)):
        makedirs(dirname(path_log))
    file_handler = logging.FileHandler(path_log)
    file_handler.setLevel(logging_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.setLevel(logging_level)
    logger.addHandler(file_handler)
    return logger
