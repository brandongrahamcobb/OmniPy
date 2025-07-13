''' config.py  The purpose of this program is to provide my primary configuaration script.
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
from omnipy.utils.inc.load_yaml import load_yaml
from omnipy.utils.inc.prompt_for_values import prompt_for_values
from omnipy.utils.inc.setup_logging import logger
from os import makedirs
from os.path import dirname, isfile
from typing import Any, Dict

import yaml

class Config:

    _config = None

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        if cls._config is None:
            if isfile(PATH_CONFIG_YAML):
                config = load_yaml(PATH_CONFIG_YAML)
                if input('Do you want to change any settings? (yes/no): ').strip().lower() in ['yes', 'y']:
                    config['api_keys'] = config.get('api_keys', {})
                    cls._modify_api_keys(config)
                    config = cls._prompt_additional_config(config)
                    with open(PATH_CONFIG_YAML, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
            else:
                makedirs(dirname(PATH_CONFIG_YAML), exist_ok=True)
                config = {
                    'api_keys': {}
                }
                cls._create_api_keys(config)
                config = cls._prompt_additional_config(config, creating=True)
                with open(PATH_CONFIG_YAML, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
            cls._config = config
        return cls._config

    @staticmethod
    def _create_api_keys(config: Dict[str, Any]):
        try:
            num_keys = int(prompt_for_values('How many API keys do you want to set up? (1-20)', '1'))
            num_keys = min(max(num_keys, 1), 20)
        except ValueError:
            num_keys = 1
        for i in range(1, num_keys + 1):
            key_name = prompt_for_values(f'Enter a unique name for API key \#{i}', f'api_key_{i}')
            while key_name in config['api_keys']:
                key_name = prompt_for_values(f'Enter a unique name for API key \#{i}', f'api_key_{i}')
            config['api_keys'][key_name] = {
                'api_key': prompt_for_values(f'Enter API key for \'{key_name}\'', ''),
                'client_id': prompt_for_values(f'Enter client ID for \'{key_name}\'', ''),
                'client_secret': prompt_for_values(f'Enter client secret for \'{key_name}\'', ''),
                'redirect_uri': prompt_for_values(f'Enter redirect URI for \'{key_name}\'', '')
            }

    @staticmethod
    def _modify_api_keys(config: Dict[str, Any]):
        existing_keys = list(config['api_keys'].keys())
        for key_name in existing_keys:
            if input(f'Do you want to modify the API key \'{key_name}\'? (yes/no): ').strip().lower() in ['yes', 'y']:
                config['api_keys'][key_name]['api_key'] = prompt_for_values(
                    f'Enter API key for \'{key_name}\'',
                    config['api_keys'][key_name].get('api_key', '')
                )
                config['api_keys'][key_name]['client_id'] = prompt_for_values(
                    f'Enter client ID for \'{key_name}\'',
                    config['api_keys'][key_name].get('client_id', '')
                )
                config['api_keys'][key_name]['client_secret'] = prompt_for_values(
                    f'Enter client secret for \'{key_name}\'',
                    config['api_keys'][key_name].get('client_secret', '')
                )
                config['api_keys'][key_name]['redirect_uri'] = prompt_for_values(
                    f'Enter redirect URI for \'{key_name}\'',
                    config['api_keys'][key_name].get('redirect_uri', '')
                )
        if len(config['api_keys']) < 20:
            add_more = input('Do you want to add more API keys? (yes/no): ').strip().lower()
            if add_more in ['yes', 'y']:
                remaining = 20 - len(config['api_keys'])
                try:
                    num_new = int(prompt_for_values(f'How many more API keys do you want to add? (1-{remaining})', '1'))
                    num_new = min(max(num_new, 1), remaining)
                except ValueError:
                    num_new = 1
                for i in range(1, num_new + 1):
                    key_name = prompt_for_values(f'Enter a unique name for new API key \#{i}', f'api_key_{len(config['api_keys']) + 1}')
                    while key_name in config['api_keys']:
                        key_name = prompt_for_values(f'Enter a unique name for new API key \#{i}', f'api_key_{len(config['api_keys']) + 1}')
                    config['api_keys'][key_name] = {
                        'api_key': prompt_for_values(f'Enter API key for \'{key_name}\'', ''),
                        'client_id': prompt_for_values(f'Enter client ID for \'{key_name}\'', ''),
                        'client_secret': prompt_for_values(f'Enter client secret for \'{key_name}\'', ''),
                        'redirect_uri': prompt_for_values(f'Enter redirect URI for \'{key_name}\'', '')
                    }

    @staticmethod
    def _prompt_additional_config(config: Dict[str, Any], creating: bool = False) -> Dict[str, Any]:
        config_fields = {
            'discord_character_limit': ('Discord character limit?', DISCORD_CHARACTER_LIMIT),
            'discord_command_prefix': ('Discord command prefix?', DISCORD_COMMAND_PREFIX),
            'discord_owner_id': ('Discord Owner ID?', DISCORD_OWNER_ID),
            'discord_release_mode': ('Discord release mode?', DISCORD_RELEASE_MODE),
            'discord_testing_guild_id': ('What is the Discord testing guild ID?', DISCORD_TESTING_GUILD_ID),
            'discord_testing_guild_ids': ('Any extras?', DISCORD_TESTING_GUILD_ID),
            'logging_level': ('What is the logging level (DEBUG, INFO, etc.)?', LOGGING_LEVEL),
            'user_agent': ('What should be the User-Agent header?', USER_AGENT),
            'version': ('Would you like to override the bot version?', VERSION),
        }
        config['web_headers'] = config.get('web_headers', {})
        add_headers = input('Do you want to add custom header sets? (yes/no): ').strip().lower()
        while add_headers in ['yes', 'y']:
            header_name = prompt_for_values('Enter a name for this header set:', 'my_header')
            header_dict = {}
            try:
                num_fields = int(prompt_for_values('How many fields in this header?', '2'))
                num_fields = max(1, num_fields)
            except ValueError:
                num_fields = 1
            for i in range(num_fields):
                key = prompt_for_values(f'Enter field name #{i + 1}:', f'Header-Key-{i+1}')
                value = prompt_for_values(f'Enter value for "{key}":', '')
                header_dict[key.strip('\'"')] = value
            config['web_headers'][header_name] = header_dict
            add_headers = input('Do you want to add another header set? (yes/no): ').strip().lower()
        for key, (prompt_text, default_value) in config_fields.items():
            user_input = prompt_for_values(prompt_text, config.get(key, default_value))
            if key == 'discord_testing_guild_ids':
                try:
                    existing_ids = eval(user_input) if isinstance(user_input, str) else user_input
                    if not isinstance(existing_ids, list):
                        existing_ids = []
                except:
                    existing_ids = []
                new_default = [DISCORD_TESTING_GUILD_ID] + existing_ids
                config[key] = new_default
            else:
                config[key] = user_input
        return config

