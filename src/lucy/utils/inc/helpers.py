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
from lucy.utils.inc.load_contents import load_contents
from lucy.utils.inc.setup_logging import logger
from os.path import dirname, abspath, expanduser, join

import discord

def parse_comma_number(s):
    return int(s.replace(",", ""))

#### DIRECTORIES
DIR_BASE = abspath(join(dirname(dirname(dirname(dirname(__file__))))))
DIR_HOME = expanduser('~')
DIR_TEMP = join(DIR_BASE, 'lucy', 'temp')

#### PATHS
### Path: Root (Vyrtuous)
PATH_TOML = join(DIR_HOME, 'Vyrtuous', 'pyproject.toml')
## Path: Source (src)
# Path: Lucy (lucy)
PATH_CONFIG = join(DIR_BASE, 'lucy', 'config.py')
PATH_CONFIG_YAML = join(DIR_BASE, 'lucy', '.config', 'config.yaml')
PATH_LOG = join(DIR_BASE, 'lucy', '.log', 'discord.log')
PATH_MAIN = join(DIR_BASE, 'lucy', 'main.py')
PATH_USERS = join(DIR_BASE, 'lucy', '.users', 'users.yaml')
# Path: Bots (bots)
PATH_DISCORD_BOT = join(DIR_BASE, 'lucy', 'bots', 'discord_bot.py')
PATH_LINKEDIN_BOT = join(DIR_BASE, 'lucy', 'bots', 'linkedin_bot.py')
PATH_TWITCH_BOT = join(DIR_BASE, 'lucy', 'bots', 'twitch_bot.py')
# Path: Cogs (cogs)
PATH_EVENT_LISTENERS = join(DIR_BASE, 'lucy', 'cogs', 'event_listeners.py')
PATH_OWNER_COMMANDS = join(DIR_BASE, 'lucy', 'cogs', 'commands_extra.py')
PATH_PUBLIC_COMMANDS = join(DIR_BASE, 'lucy', 'cogs', 'commands.py')
PATH_SCHEDULED_TASKS = join (DIR_BASE, 'lucy', 'cogs', 'scheduled_tasks.py')
# Path: Drivers (drivers)
PATH_CHROMEDRIVER = join (DIR_BASE, 'lucy', 'resources', 'drivers', 'chromedriver')
# Path: Fonts (fonts)
PATH_FONT = join(DIR_HOME, 'lucy', 'resources', 'fonts', 'Roboto-Regular.ttf')
# Path: Handlers (handlers)
PATH_CHEMISTRY = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'chemistry_manager.py')
PATH_GAME = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'game_manager.py')
PATH_IMAGE = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'image_manager.py')
PATH_MESSAGE = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'message_manager.py')
PATH_PREDICATOR = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'predicator.py')
PATH_PDF_MANAGER = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'pdf_manager.py')
PATH_ROLE_MANAGER = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'role_manager.py')
PATH_TAG = join(DIR_BASE, 'lucy', 'utils', 'handlers', 'tag_manager.py')
# Path: Include (inc)
PATH_AVERAGE_SCORE = join(DIR_BASE, 'lucy', 'utils', 'inc', 'average_score.py')
PATH_CLEAR_SCREEN = join(DIR_BASE, 'lucy', 'utils', 'inc', 'clear_screen.py')
PATH_FRAMES = join(DIR_BASE, 'lucy', 'utils', 'inc', 'frames.py')
PATH_GOOGLE = join(DIR_BASE, 'lucy', 'utils', 'inc', 'google.py')
PATH_HELPERS = join(DIR_BASE, 'lucy', 'utils', 'inc', 'helpers.py')
PATH_INCREMENT_VERSION = join(DIR_BASE, 'lucy', 'utils', 'inc', 'increment_version.py')
PATH_LOAD_CONTENTS = join(DIR_BASE, 'lucy', 'utils', 'inc', 'load_contents.py')
PATH_LOAD_YAML = join(DIR_BASE, 'lucy', 'utils', 'inc', 'load_yaml.py')
PATH_PROMPT_FOR_VALUES = join(DIR_BASE, 'lucy', 'utils', 'inc', 'prompt_for_values.py')
PATH_SCRIPT = join(DIR_BASE, 'lucy', 'utils', 'inc', 'script.py')
PATH_SETUP_LOGGING = join(DIR_BASE, 'lucy', 'utils', 'inc', 'setup_logging.py')
PATH_UNIQUE_PAIRS = join(DIR_BASE, 'lucy', 'utils', 'inc', 'unique_pairs.py')
# Path: Security (sec)
PATH_DISCORD_OAUTH = join(DIR_BASE, 'lucy', 'utils', 'sec', 'discord_oauth.py')
PATH_LINKEDIN_OAUTH = join(DIR_BASE, 'lucy', 'utils', 'sec', 'linkedin_oauth.py')
PATH_PATREON_OAUTH = join(DIR_BASE, 'lucy', 'utils', 'sec','patreon_oauth.py')
PATH_TWITCH_OAUTH = join(DIR_BASE, 'lucy', 'utils', 'sec', 'twitch_oauth.py')
# Path: Temporary (temp)
PATH_OPENAI_REQUESTS = join(DIR_BASE, 'lucy', 'temp', 'queued_requests.json')
PATH_OPENAI_RESULTS = join(DIR_BASE, 'lucy', 'temp', 'processed_results.json')

#### CONTENTS
### Path: Root (Vyrtuous)
## Path: Source (src)
# Path: Lucy (lucy)
CONTENTS_CONFIG = load_contents(PATH_CONFIG)
CONTENTS_MAIN = load_contents(PATH_MAIN)
contents_main = [
    CONTENTS_CONFIG,
    CONTENTS_MAIN
]
# Path: Bots (bots)
CONTENTS_DISCORD_BOT = load_contents(PATH_DISCORD_BOT)
CONTENTS_LINKEDIN_BOT = load_contents(PATH_LINKEDIN_BOT)
CONTENTS_TWITCH_BOT = load_contents(PATH_TWITCH_BOT)
contents_bots = [
    CONTENTS_DISCORD_BOT,
    CONTENTS_LINKEDIN_BOT,
    CONTENTS_TWITCH_BOT,
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
# Path: Security (sec)
CONTENTS_DISCORD_OAUTH = load_contents(PATH_DISCORD_OAUTH)
CONTENTS_LINKEDIN_OAUTH = load_contents(PATH_LINKEDIN_OAUTH)
CONTENTS_PATREON_OAUTH = load_contents(PATH_PATREON_OAUTH)
CONTENTS_TWITCH_OAUTH = load_contents(PATH_TWITCH_OAUTH)
contents_sec = [
    CONTENTS_DISCORD_OAUTH,
    CONTENTS_LINKEDIN_OAUTH,
    CONTENTS_PATREON_OAUTH,
    CONTENTS_TWITCH_OAUTH,
]
CONTENTS_SEC_SUM = " and ".join(contents_sec)

#### DISCORD
DISCORD_CHARACTER_LIMITS = [2000, 4000]
DISCORD_CHARACTER_LIMIT = 2000
DISCORD_COGS = [
    'lucy.cogs.commands',
    'lucy.cogs.commands_extra',
    'lucy.cogs.event_listeners',
    'lucy.cogs.scheduled_tasks',
]
DISCORD_COMMAND_PREFIX = '!'
DISCORD_INTENTS = discord.Intents.all()
DISCORD_MODERATION_WARNING = 'You have been warned.'
DISCORD_OWNER_ID = 154749533429956608
DISCORD_RELEASE_MODE = False
DISCORD_ROLE_PASS = 1308689505158565918
DISCORD_TESTING_GUILD_ID = 1300517536001036348

LOGGING_LEVEL = 'INFO'

#### OPENAI
### Completions
OPENAI_CHAT_ADD_COMPLETION_TO_HISTORY = True
OPENAI_CHAT_COLORIZE_RESPONSE_FORMAT = {
'type': 'json_schema',
'json_schema': {
    'name': 'colorize',
    'description': 'A function that returns color values for a given request.',
    'schema': {
      'type': 'object',
      'properties': {
        'r': {
          'type': 'integer',
          'minimum': 0,
          'maximum': 255
        },
        'g': {
          'type': 'integer',
          'minimum': 0,
          'maximum': 255
        },
        'b': {
          'type': 'integer',
          'minimum': 0,
          'maximum': 255
        }
      },
      'required': ['r', 'g', 'b'],
      'additionalProperties': False
    }
  }
}
OPENAI_CHAT_COMPLETION = True
OPENAI_CHAT_HEADERS = {
    'Content-Type': 'application/json',
    'OpenAI-Organization': 'org-3LYwtg7DSFJ7RLn9bfk4hATf',
    'User-Agent': 'brandongrahamcobb@icloud.com',
    'OpenAI-Project': 'proj_u5htBCWX0LSHxkw45po1Vfz9',
}
OPENAI_CHAT_MODELS = {
    'current': ['chatgpt-4o-mini-latest', 'gpt-4.1', 'gpt-4.1-nano', 'gpt-4o-audio', 'o1-mini', 'o1-preview', 'o3-mini', 'o4-mini'],
    'deprecated': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k', 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'chatgpt-4o-latest'],
}
### Moderations
OPENAI_CHAT_MODERATION = True
OPENAI_CHAT_MODERATION_N = 1
OPENAI_CHAT_MODERATION_MODEL = 'gpt-4o-mini'
OPENAI_CHAT_MODERATION_RESPONSE_FORMAT = {
'type': 'json_schema',
'json_schema': {
    'name': 'moderation',
    'description': 'A function that returns moderation results according to a specified schema.',
    'schema': {
      'type': 'object',
      'properties': {
        'id': {'type': 'string'},
        'model': {'type': 'string'},
        'results': {
          'type': 'array',
          'items': {
            'type': 'object',
            'properties': {
              'flagged': {'type': 'boolean'},
              'categories': {
                'type': 'object',
                'properties': {
                  'sexual': {'type': 'boolean'},
                  'hate': {'type': 'boolean'},
                  'harassment': {'type': 'boolean'},
                  'self-harm': {'type': 'boolean'},
                  'sexual/minors': {'type': 'boolean'},
                  'hate/threatening': {'type': 'boolean'},
                  'violence/graphic': {'type': 'boolean'},
                  'self-harm/intent': {'type': 'boolean'},
                  'self-harm/instructions': {'type': 'boolean'},
                  'harassment/threatening': {'type': 'boolean'},
                  'violence': {'type': 'boolean'},
                  'academic-dishonesty': {'type': 'boolean'},
                  'animal-derived-technology': {'type': 'boolean'}
                },
                'required': [
                  'sexual',
                  'hate',
                  'harassment',
                  'self-harm',
                  'sexual/minors',
                  'hate/threatening',
                  'violence/graphic',
                  'self-harm/intent',
                  'self-harm/instructions',
                  'harassment/threatening',
                  'violence',
                  'academic-dishonesty',
                  'animal-derived-technology'
                ]
              },
              'category_scores': {
                'type': 'object',
                'properties': {
                  'sexual': {'type': 'number'},
                  'hate': {'type': 'number'},
                  'harassment': {'type': 'number'},
                  'self-harm': {'type': 'number'},
                  'sexual/minors': {'type': 'number'},
                  'hate/threatening': {'type': 'number'},
                  'violence/graphic': {'type': 'number'},
                  'self-harm/intent': {'type': 'number'},
                  'self-harm/instructions': {'type': 'number'},
                  'harassment/threatening': {'type': 'number'},
                  'violence': {'type': 'number'},
                  'academic-dishonesty': {'type': 'number'},
                  'animal-derived-technology': {'type': 'boolean'}
                },
                'required': [
                  'sexual',
                  'hate',
                  'harassment',
                  'self-harm',
                  'sexual/minors',
                  'hate/threatening',
                  'violence/graphic',
                  'self-harm/intent',
                  'self-harm/instructions',
                  'harassment/threatening',
                  'violence',
                  'academic-dishonesty',
                  'animal-derived-technology'
                ]
              }
            },
            'required': ['flagged', 'categories', 'category_scores']
          }
        }
      },
      'additionalProperties': False,
      'required': ['id', 'model', 'results']
    }
  }
}
OPENAI_CHAT_MODERATION_STOP = ''
OPENAI_CHAT_MODERATION_STORE = False
OPENAI_CHAT_MODERATION_STREAM = False
OPENAI_CHAT_MODERATION_SYS_INPUT = 'You are a JSON moderation assistant.'
OPENAI_CHAT_MODERATION_TEMPERATURE = 1.0
OPENAI_CHAT_MODERATION_TOP_P = 1.0
OPENAI_CHAT_MODERATION_USE_HISTORY = False
OPENAI_CHAT_MODEL = 'gpt-4.1-nano'
OPENAI_CHAT_N = 1
OPENAI_CHAT_RESPONSE_FORMAT = None
OPENAI_CHAT_MODERATION_USE_HISTORY = False
OPENAI_CHAT_MODERATION_ADD_COMPLETION_TO_HISTORY = False
OPENAI_CHAT_STOP = ''
OPENAI_CHAT_STORE = False
OPENAI_CHAT_STREAM = False
OPENAI_CHAT_SYS_INPUT = f'You are Vyrtuous.'
OPENAI_CHAT_TOP_P = 1
OPENAI_CHAT_DEPRECATED_TEMPERATURE = 0.7
OPENAI_CHAT_TEMPERATURE = 1.0
OPENAI_CHAT_USE_HISTORY = True
OPENAI_CHAT_USER = 'Brandon Graham Cobb'
OPENAI_ENDPOINT_URLS = {
    'audio': 'https://api.openai.com/v1/audio/speech',
    'batch': 'https://api.openai.com/v1/audio/batches',
    'chat': 'https://api.openai.com/v1/chat/completions',
    'embeddings': 'https://api.openai.com/v1/embeddings',
    'files': 'https://api.openai.com/v1/files',
    'fine-tuning': 'https://api.openai.com/v1/fine_tuning/jobs',
    'images': 'https://api.openai.com/v1/images/generations',
    'models': 'https://api.openai.com/v1/models',
    'moderations': 'https://api.openai.com/v1/moderations',
    'uploads': 'https://api.openai.com/v1/uploads',
}
OPENAI_FINE_TUNING_RESPONSE_FORMAT = {
  'type': 'json_schema',
  'json_schema': {
    'name': 'animal_rights_identification',
    'description': 'A schema to identify if content qualifies as animal rights activism',
    'schema': {
      'type': 'object',
      'properties': {
        'id': {
          'type': 'string',
          'description': 'Unique identifier for the content being evaluated'
        },
        'results': {
          'type': 'boolean',
          'description': 'Indicates whether the content qualifies as animal rights activism',
          'enum': [True]
        }
      },
      'required': ['id', 'results']
    }
  }
}
OPENAI_MODEL_CONTEXT_LIMITS = {
    'ft:gpt-4o-mini-2024-07-18:spawd:vyrtuous:AjZpTNN2': parse_comma_number("16,384"),
    'gpt-3.5-turbo': parse_comma_number("4,096"),
    'gpt-4': parse_comma_number("8,192"),
    'gpt-4-32k': parse_comma_number("32,768"),
    'gpt-4o': parse_comma_number("128,000"),
    'gpt-4o-mini': parse_comma_number("128,000"),
    'gpt-4-turbo': parse_comma_number("128,000"),
    'gpt-4.1': parse_comma_number("32,768"),
    'gpt-4.1-nano': parse_comma_number("1,047,576"),
    'gpt-4o-audio': parse_comma_number("128,000"),
    'o1-preview': parse_comma_number("128,000"),
    'o1-mini': parse_comma_number("128,000"),
    'o3-mini': parse_comma_number("200,000"),
    'o4-mini': parse_comma_number("200,000")
}
OPENAI_MODEL_OUTPUT_LIMITS = {
    'ft:gpt-4o-mini-2024-07-18:spawd:vyrtuous:AjZpTNN2': parse_comma_number("128,000"),
    'gpt-3.5-turbo': parse_comma_number("4,096"),
    'gpt-4': parse_comma_number("8,192"),
    'gpt-4-32k': parse_comma_number("32,768"),
    'gpt-4o': parse_comma_number("4,096"),         # Initially capped at 4"),096; updated to 16"),384 in later versions
    'gpt-4o-mini': parse_comma_number("16,384"),
    'gpt-4-turbo': parse_comma_number("4,096"),
    'gpt-4.1': parse_comma_number("300,000"),
    'gpt-4.1-nano': parse_comma_number("32,768"),
    'gpt-4o-audio': parse_comma_number("16,384"),
    'o1-preview': parse_comma_number("32,768"),
    'o1-mini': parse_comma_number("16,384"),
    'o3-mini': parse_comma_number("100,000"),
    'o4-mini': parse_comma_number("100,000")
}
OPENAI_MODERATION_MODEL = 'omni-moderation-latest'
OPENAI_MODERATION_IMAGE = True

#### SCRIPTURE
SCRIPTURE_HEADERS = {
    'User-Agent': 'brandongrahamcobb@icloud.com',
    'api-key': '2eb327f99245cd3d68da55370656d6e2'
}

USER_AGENT = 'https://github.com/brandongrahamcobb/Vyrtuous.git'
VERSION = '1.0.0'
