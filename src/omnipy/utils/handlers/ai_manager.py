''' ai_manager.py

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
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from lucy.utils.inc.helpers import *
from lucy.utils.inc.load_yaml import load_yaml
from lucy.utils.inc.setup_logging import logger
from openai import AsyncOpenAI
from typing import List, Optional, Any, Dict, Union

import aiohttp
import argparse  # for running script from command line
import asyncio
import datetime
import json
import numpy as np
import openai
import os
import re  # for matching endpoint from request URL
import tiktoken  # for counting tokens
import time  # for sleeping after rate limit is hit
import traceback
