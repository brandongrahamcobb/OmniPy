''' discord.py  This is essentially a stripped version of Rapptz advanced_startup.py.
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
import asyncpg
import discord

from discord.ext import commands
from omnipy.utils.inc.helpers import *
from omnipy.utils.inc.setup_logging import logger
from typing import List, Optional

class DiscordBot(commands.Bot):
    def __init__(self, *, config, db_pool: asyncpg.Pool, lock, oauth_token, **kwargs):
        try:
            intents = discord.Intents.all()
            super().__init__(command_prefix=config['discord_command_prefix'], intents=intents, **kwargs)

            self.config = config
            self.db_pool = db_pool
            self.lock = lock
            self.oauth_token = oauth_token
            self.api_key = self.config['api_keys']['Discord']['api_key']
            self.testing_guild_id = self.config['discord_testing_guild_id']
        except Exception as e:
            logger.error(f'Error during Discord bot initialization: {e}')

    async def process_commands(self, message):
            """Override process_commands to listen to bots."""
            ctx = await self.get_context(message)
            await self.invoke(ctx)
        
    async def setup_hook(self) -> None:
        try:
            cogs = DISCORD_COGS
            for cog in cogs:
                await self.load_extension(cog)
            if self.testing_guild_id:
                guild = discord.Object(id=self.testing_guild_id)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
        except Exception as e:
            logger.error(f'Error during Discord bot setup_hook: {e}')
