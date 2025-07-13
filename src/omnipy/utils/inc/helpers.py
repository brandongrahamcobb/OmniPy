''' helpers.py  The purpose of this program is to provide generic parameters.
    Copyright (C) 2024 github.com/brandongrahamcobb

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
from omnipy.utils.inc.load_contents import load_contents
from omnipy.utils.inc.setup_logging import logger
from os.path import dirname, abspath, expanduser, join

import discord

def parse_comma_number(s):
    return int(s.replace(",", ""))

#### DIRECTORIES
DIR_BASE = abspath(join(dirname(dirname(dirname(dirname(__file__))))))
DIR_HOME = expanduser('~')
DIR_TEMP = join(DIR_BASE, 'omnipy', 'temp')

#### PATHS
### Path: Root (Py_vyrtuous)
PATH_TOML = join(DIR_HOME, 'git', 'python', 'OmniPy', 'pyproject.toml')
## Path: Source (src)
# Path: Py_Py_vyrtuous (omnipy)
PATH_CONFIG = join(DIR_BASE, 'omnipy', 'config.py')
PATH_CONFIG_YAML = join(DIR_BASE, 'omnipy', '.config', 'config.yaml')
PATH_LOG = join(DIR_BASE, 'omnipy', '.log', 'discord.log')
PATH_MAIN = join(DIR_BASE, 'omnipy', 'main.py')
PATH_USERS = join(DIR_BASE, 'omnipy', '.users', 'users.yaml')
# Path: Bots (bots)
PATH_DISCORD_BOT = join(DIR_BASE, 'omnipy', 'bots', 'discord_bot.py')
# Path: Cogs (cogs)
PATH_EVENT_LISTENERS = join(DIR_BASE, 'omnipy', 'cogs', 'event_listeners.py')
PATH_OWNER_COMMANDS = join(DIR_BASE, 'omnipy', 'cogs', 'commands_extra.py')
PATH_PUBLIC_COMMANDS = join(DIR_BASE, 'omnipy', 'cogs', 'commands.py')
PATH_SCHEDULED_TASKS = join (DIR_BASE, 'omnipy', 'cogs', 'scheduled_tasks.py')
# Path: Drivers (drivers)
PATH_CHROMEDRIVER = join (DIR_BASE, 'omnipy', 'resources', 'drivers', 'chromedriver')
# Path: Fonts (fonts)
PATH_FONT = join(DIR_BASE, 'omnipy', 'resources', 'fonts', 'Roboto-Regular.ttf')
# Path: Handlers (handlers)
PATH_CHEMISTRY = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'chemistry_manager.py')
PATH_GAME = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'game_manager.py')
PATH_IMAGE = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'image_manager.py')
PATH_MESSAGE = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'message_manager.py')
PATH_PREDICATOR = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'predicator.py')
PATH_PDF_MANAGER = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'pdf_manager.py')
PATH_ROLE_MANAGER = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'role_manager.py')
PATH_TAG = join(DIR_BASE, 'omnipy', 'utils', 'handlers', 'tag_manager.py')
# Path: Include (inc)
PATH_AVERAGE_SCORE = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'average_score.py')
PATH_CLEAR_SCREEN = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'clear_screen.py')
PATH_FRAMES = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'frames.py')
PATH_GOOGLE = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'google.py')
PATH_HELPERS = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'helpers.py')
PATH_INCREMENT_VERSION = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'increment_version.py')
PATH_LOAD_CONTENTS = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'load_contents.py')
PATH_LOAD_YAML = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'load_yaml.py')
PATH_PROMPT_FOR_VALUES = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'prompt_for_values.py')
PATH_SCRIPT = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'script.py')
PATH_SETUP_LOGGING = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'setup_logging.py')
PATH_UNIQUE_PAIRS = join(DIR_BASE, 'omnipy', 'utils', 'inc', 'unique_pairs.py')
#### CONTENTS
# Path: Py_Py_vyrtuous (omnipy)
CONTENTS_CONFIG = load_contents(PATH_CONFIG)
CONTENTS_MAIN = load_contents(PATH_MAIN)
contents_main = [
    CONTENTS_CONFIG,
    CONTENTS_MAIN
]
# Path: Bots (bots)
CONTENTS_DISCORD_BOT = load_contents(PATH_DISCORD_BOT)
contents_bots = [
    CONTENTS_DISCORD_BOT,
]
CONTENTS_BOTS_SUM = " and ".join(contents_bots)
# Path: Cogs (cogs)
CONTENTS_EVENT_LISTENERS = load_contents(PATH_EVENT_LISTENERS)
CONTENTS_OWNER_COMMANDS = load_contents(PATH_OWNER_COMMANDS)
CONTENTS_PUBLIC_COMMANDS = load_contents(PATH_PUBLIC_COMMANDS)
CONTENTS_SCHEDULED_TASKS = load_contents(PATH_SCHEDULED_TASKS)
contents_cogs = [
    CONTENTS_EVENT_LISTENERS,
    CONTENTS_OWNER_COMMANDS,
    CONTENTS_PUBLIC_COMMANDS,
    CONTENTS_SCHEDULED_TASKS,
]
CONTENTS_COGS_SUM = " and ".join(contents_cogs)
# Path: Include (inc)
CONTENTS_AVERAGE_SCORE = load_contents(PATH_AVERAGE_SCORE)
CONTENTS_CLEAR_SCREEN = load_contents(PATH_CLEAR_SCREEN)
CONTENTS_FRAMES = load_contents(PATH_FRAMES)
CONTENTS_GOOGLE = load_contents(PATH_GOOGLE)
CONTENTS_HELPERS = load_contents(PATH_HELPERS)
CONTENTS_INCREMENT_VERSION = load_contents(PATH_INCREMENT_VERSION)
CONTENTS_LOAD_CONTENTS = load_contents(PATH_LOAD_CONTENTS)
CONTENTS_LOAD_YAML = load_contents(PATH_LOAD_YAML)
CONTENTS_PROMPT_FOR_VALUES = load_contents(PATH_PROMPT_FOR_VALUES)
CONTENTS_SCRIPT = load_contents(PATH_SCRIPT)
CONTENTS_SETUP_LOGGING = load_contents(PATH_SETUP_LOGGING)
CONTENTS_UNIQUE_PAIRS = load_contents(PATH_UNIQUE_PAIRS)
contents_inc = [
    CONTENTS_AVERAGE_SCORE,
    CONTENTS_CLEAR_SCREEN,
    CONTENTS_FRAMES,
    CONTENTS_GOOGLE,
    CONTENTS_HELPERS,
    CONTENTS_INCREMENT_VERSION,
    CONTENTS_LOAD_CONTENTS,
    CONTENTS_LOAD_YAML,
    CONTENTS_PROMPT_FOR_VALUES,
    CONTENTS_SCRIPT,
    CONTENTS_SETUP_LOGGING,
    CONTENTS_UNIQUE_PAIRS,
]
CONTENTS_INC_SUM = " and ".join(contents_inc)
# Path: Handlers (handlers)
CONTENTS_CHEMISTRY = load_contents(PATH_CHEMISTRY)
CONTENTS_CONFIG = load_contents(PATH_CONFIG)
CONTENTS_GAME = load_contents(PATH_GAME)
CONTENTS_IMAGE = load_contents(PATH_IMAGE)
CONTENTS_MESSAGE = load_contents(PATH_MESSAGE)
CONTENTS_PDF_MANAGER = load_contents(PATH_PDF_MANAGER)
CONTENTS_PREDICATOR = load_contents(PATH_PREDICATOR)
CONTENTS_ROLE_MANAGER = load_contents(PATH_ROLE_MANAGER)
CONTENTS_TAG = load_contents(PATH_TAG)
contents_handlers = [
    CONTENTS_CHEMISTRY,
    CONTENTS_CONFIG,
    CONTENTS_GAME,
    CONTENTS_IMAGE,
    CONTENTS_MESSAGE,
    CONTENTS_PDF_MANAGER,
    CONTENTS_PREDICATOR,
    CONTENTS_ROLE_MANAGER,
    CONTENTS_TAG,
]
CONTENTS_HANDLERS_SUM = " and ".join(contents_handlers)

#### DISCORD
DISCORD_CHARACTER_LIMITS = [2000, 4000]
DISCORD_CHARACTER_LIMIT = 2000
DISCORD_COGS = [
    'omnipy.cogs.commands',
    'omnipy.cogs.commands_extra',
    'omnipy.cogs.event_listeners',
    'omnipy.cogs.scheduled_tasks',
]
DISCORD_COMMAND_PREFIX = '!'
DISCORD_INTENTS = discord.Intents.all()
DISCORD_OWNER_ID = 154749533429956608
DISCORD_RELEASE_MODE = False
DISCORD_TESTING_GUILD_ID = 1300517536001036348

LOGGING_LEVEL = 'INFO'

#### SCRIPTURE
SCRIPTURE_HEADERS = {
    'User-Agent': 'brandongrahamcobb@icloud.com',
    'api-key': '2eb327f99245cd3d68da55370656d6e2'
}

USER_AGENT = 'https://github.com/brandongrahamcobb/Py_vyrtuous.git'
VERSION = '1.0.0'
