''' average_score.py  The purpose of this program is present the average score of an OpenAI training.jsonl file.
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
from py_vyrtuous.utils.inc.helpers import *
from py_vyrtuous.utils.inc.setup_logging import logger

import asyncio
import json
import os

def average_score():
    home = os.path.expanduser('~')
    path_training = os.path.join(PATH_TRAINING)
    with open(path_training, 'r') as file:
        training_data = json.load(file)
        sum = 0
        for arg in training_data:
            sum += arg['messages'][1]['content']['sentiment_score']
        average = sum / len(training_data)
        return average
    file.close()

