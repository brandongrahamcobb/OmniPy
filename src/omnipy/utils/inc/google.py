''' google.py  The purpose of this program is to search using the Google Custom Search Restricted API.
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
from discord.ext import commands
from googleapiclient.discovery import build
from py_vyrtuous.config import Config
from py_vyrtuous.utils.inc.setup_logging import logger
import discord

def google(query: str, num_results: int = 5):
    try:
        service = build("customsearch", "v1", developerKey=Config.get_config()['api_keys']['Google']['api_key'])
        result = service.cse().list(q=query, cx=Config.get_config()['api_keys']['Google']['client_id'], num=num_results).execute()
        search_results = [
            {"title": item["title"], "link": item["link"]}
            for item in result.get("items", [])
        ]
        return search_results
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []
