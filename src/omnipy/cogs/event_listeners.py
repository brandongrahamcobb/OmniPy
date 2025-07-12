''' indica.py The purpose of the program is to be an extension for a Discord bot for listeners.
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
from py_vyrtuous.utils.handlers.game_manager import Game
from py_vyrtuous.utils.handlers.message_manager import Message
from py_vyrtuous.utils.handlers.predicator import Predicator
from py_vyrtuous.utils.handlers.role_manager import RoleManager
from py_vyrtuous.utils.inc.helpers import *
from py_vyrtuous.utils.inc.setup_logging import logger

import discord
import json
import os
import py_vyrtuous.utils.inc.handle_users
import shutil
import time
import traceback
import uuid

class Indica(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db_pool = bot.db_pool
        self.handler = Message(self.bot, self.config,  self.db_pool)
        self.predicator = Predicator(self.bot)
        self.user_messages = {}
        self.role_manager = RoleManager(self.db_pool)

    @commands.after_invoke
    async def after_invoke(ctx):
        if hasattr(bot, 'db_pool'):
            await bot.db_pool.close()

    @commands.Cog.listener()
    async def on_member_remove(member):
        await role_manager.backup_roles_for_member(member)

    @commands.Cog.listener()
    async def on_member_join(member):
        await role_manager.restore_roles_for_member(member)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            if ctx.command:
                await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.id == 1318597210119864385: #bot or message.is_system():
                return
            ctx = await self.bot.get_context(message)
            author = ctx.author.name
            #await self.bot.process_commands(message)
            #handle_users(author)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            try:
                shutil.rmtree(DIR_TEMP)
                os.makedirs(DIR_TEMP, exist_ok=True)
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temporary files: {cleanup_error}")

    @commands.Cog.listener()
    async def on_ready(self):
        bot_user = self.bot.user
        bot_name = bot_user.name
        bot_id = bot_user.id
        guild_count = len(self.bot.guilds)
        info = (
            f'\n=============================\n'
            f'bot Name: {bot_name}\n'
            f'bot ID: {bot_id}\n'
            f'Connected Guilds: {guild_count}\n'
            f'============================='
        )
        guild_info = '\n'.join(
            [f'- {guild.name} (ID: {guild.id})' for guild in self.bot.guilds]
        )
        stats_message = f'{info}\n\nGuilds:\n{guild_info}'
        print(stats_message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Indica(bot))
