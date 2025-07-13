''' predicator.py  The purpose of this program is to provide checks for predication.
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
from discord.utils import get
from omnipy.utils.inc.setup_logging import logger
import discord
import logging

class Predicator:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    def at_home(self):
        async def predicate(ctx):
            return ctx.guild is not None and ctx.guild.id == self.config['discord_testing_guild_id']
        return commands.check(predicate)

    def release_mode(self):
        async def predicate(ctx):
            return (
                ctx.author.id == 154749533429956608 or 
                self.config.get('discord_release_mode', False) or 
                isinstance(ctx.channel, discord.DMChannel)
            )
        return commands.check(predicate)

    async def is_at_home_func(self, guild_id: int) -> bool:
        if guild_id == self.config['discord_testing_guild_id'] or (guild_id in self.config['discord_testing_guild_ids']):
            return True

    def is_developer(self, member: discord.Member) -> bool:
        if member is not None:
            return member.id == self.config['discord_owner_id']
        else:
            return False

    async def is_vegan_user(self, user: discord.User) -> bool:
        guild_ids = self.config['discord_testing_guild_ids']
        for guild_id in guild_ids:
            guild = self.bot.get_guild(guild_id)
            if guild:
                vegan_role = get(guild.roles, name='vegan')
                if vegan_role and vegan_role in user.roles:
                    return True
        return False

    def is_release_mode_func(self, ctx: commands.Context) -> bool:
        return (
            ctx.author.id == 154749533429956608 or
            self.config.get('discord_release_mode', False) or
            isinstance(ctx.channel, discord.DMChannel)
        )
