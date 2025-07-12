''' prompt_for_values.py  The purpose of this program is to prompt for new config values and present the old ones or keep the old ones.
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

def prompt_for_values(prompt: str, default_value: str) -> str:
    value = input(f'{prompt} [{default_value}]: ')
    return value.strip() if value.strip() else default_value
