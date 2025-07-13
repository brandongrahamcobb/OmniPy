''' game_cog.py
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

from decimal import Decimal
from discord.ext import commands
from omnipy.utils.handlers.predicator import Predicator
from omnipy.utils.inc.helpers import *
from os import makedirs
from os.path import exists
import asyncpg
import asyncio
import discord
import json
import os
import random
import yaml

class Game:
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.users = {}
        self.factions = {}
        self.db_pool = self.bot.db_pool
        self.xp_table = [1, 15, 34, 57, 92, 135, 372, 560, 840, 1242, 1144, 1573, 2144, 2800, 3640, 4700, 5893, 7360, 9144, 11120,
                         13477, 16268, 19320, 22880, 27008, 31477, 36600, 42444, 48720, 55813, 63800, 86784, 98208, 110932, 124432,
                         139372, 155865, 173280, 192400, 213345, 235372, 259392, 285532, 312928, 342624, 374760, 408336, 445544,
                         483532, 524160, 567772, 598886, 631704, 666321, 702836, 741351, 781976, 824828, 870028, 917625, 967995,
                         1021041, 1076994, 1136013, 1198266, 1263930, 1333194, 1406252, 1483314, 1564600, 1650340, 1740778, 1836173,
                         1936794, 2042930, 2154882, 2272970, 2397528, 2528912, 2667496, 2813674, 2967863, 3130502, 3302053, 3483005,
                         3673873, 3875201, 4087562, 4311559, 4547832, 4797053, 5059931, 5337215, 5629694, 5938202, 6263614, 6606860,
                         6968915, 7350811, 7753635, 8178534, 8626718, 9099462, 9598112, 10124088, 10678888, 11264090, 11881362,
                         12532461, 13219239, 13943653, 14707765, 15513750, 16363902, 17260644, 18206527, 19204245, 20256637, 21366700,
                         22537594, 23772654, 25075395, 26449526, 27898960, 29427822, 31040466, 32741483, 34535716, 36428273, 38424542,
                         40530206, 42751262, 45094030, 47565183, 50171755, 52921167, 55821246, 58880250, 62106888, 65510344, 69100311,
                         72887008, 76881216, 81094306, 85594273, 90225770, 95170142, 100385466, 105886589, 111689174, 117809740,
                         124265714, 131075474, 138258410, 145834970, 153826726, 162256430, 171148082, 180526997, 190419876, 200854885,
                         211861732, 223471711, 223471711, 248635353, 262260570, 276632449, 291791906, 307782102, 324648562, 342439302,
                         361204976, 380999008, 401877754, 423900654, 447130410, 471633156, 497478653, 524740482, 553496261, 583827855,
                         615821622, 649568646, 685165008, 722712050, 762316670, 804091623, 848155844, 894634784, 943660770, 995373379,
                         1049919840, 1107455447, 1168144006, 1232158297, 1299680571, 1370903066, 1446028554, 1525246918, 1608855764,
                         1697021059]
        self.predicator = Predicator(self.bot)

    async def get_user(self, user_id):
        async with self.db_pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)

    async def get_faction(self, faction_name):
        async with self.db_pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM factions WHERE name = $1', faction_name)

    async def get_faction_members(self, faction_name):
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('SELECT user_id FROM faction_members WHERE faction_name = $1', faction_name)
            return [row['user_id'] for row in rows]

    async def get_faction_leaderboard(self):
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch('SELECT name, xp, level FROM factions ORDER BY xp DESC LIMIT 10')
            return [dict(row) for row in rows]

    async def get_xp_for_level(self, level):
        return sum(self.xp_table[:level])

    async def get_xp_per_interaction(self, current_level):
        xp_for_next_level = self.xp_table[current_level]
        daily_xp_required = xp_for_next_level / (365 / 200)
        return daily_xp_required / 200

    async def distribute_xp(self, user_id):
        async with self.db_pool.acquire() as conn:
            user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
            if not user:
                # Fetch Discord username for insertion.
                discord_user = self.bot.get_user(user_id)
                username = discord_user.name if discord_user else f'User_{user_id}'
                await conn.execute(
                    'INSERT INTO users (id, name, level, exp, faction_name) VALUES ($1, $2, 1, 0, NULL)',
                    user_id, username
                )
                level, xp, faction_name = 1, Decimal('0'), None
            else:
                level, xp, faction_name = user['level'], user['exp'], user['faction_name']
            xp_per_interaction = await self.get_xp_per_interaction(level)
            xp_gain = random.uniform(0.8 * xp_per_interaction, 1.2 * xp_per_interaction)
            xp_gain = Decimal(str(xp_gain))
            new_xp = xp + xp_gain
            if new_xp >= await self.get_xp_for_level(level + 1):
                level += 1
            await conn.execute(
                'UPDATE users SET level = $1, exp = $2 WHERE id = $3',
                level, new_xp, user_id
            )
            if faction_name:
                await conn.execute(
                    'UPDATE factions SET xp = xp + $1 WHERE name = $2',
                    xp_gain, faction_name
                )
                faction_row = await conn.fetchrow(
                    'SELECT xp, level FROM factions WHERE name = $1', faction_name
                )
                faction_xp = faction_row['xp']
                faction_level = faction_row['level']
                required_xp = await self.get_xp_for_level(faction_level + 1)
                if faction_xp >= required_xp:
                    faction_level += 1
                    await conn.execute(
                        'UPDATE factions SET level = $1 WHERE name = $2',
                        faction_level, faction_name
                    )

    async def create_faction(self, faction_name, creator_id, ctx=None):
        if await self.moderate_name(ctx, faction_name):
            return False
        async with self.db_pool.acquire() as conn:
            faction_exists = await conn.fetchrow('SELECT name FROM factions WHERE name = $1', faction_name)
            if faction_exists:
                return False
            await conn.execute(
                'INSERT INTO factions (name, xp, level) VALUES ($1, 0, 1)', faction_name
            )
            await conn.execute(
                'UPDATE users SET faction_name = $1 WHERE id = $2', faction_name, creator_id
            )
            await conn.execute(
                'INSERT INTO faction_members (user_id, faction_name) VALUES ($1, $2)', creator_id, faction_name
            )
        guild = discord.utils.get(self.bot.guilds)
        member = guild.get_member(creator_id)
        if member:
            try:
                new_nick = f'[{faction_name}] {member.name}'
                await member.edit(nick=new_nick)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
        return True

    async def join_faction(self, faction_name, user_id):
        async with self.db_pool.acquire() as conn:
            faction_exists = await conn.fetchrow('SELECT name FROM factions WHERE name = $1', faction_name)
            if not faction_exists:
                return 'Faction not found'
            already_member = await conn.fetchrow(
                'SELECT * FROM faction_members WHERE user_id = $1 AND faction_name = $2',
                user_id, faction_name
            )
            if already_member:
                return 'Already a member'
            await conn.execute(
                'INSERT INTO faction_members (user_id, faction_name) VALUES ($1, $2)', user_id, faction_name
            )
            await conn.execute(
                'UPDATE users SET faction_name = $1 WHERE id = $2', faction_name, user_id
            )
            return 'Joined successfully'

    async def get_leaderboard(self):
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                'SELECT id, name, level, exp FROM users ORDER BY level DESC, exp DESC LIMIT 10'
            )
            return rows

    async def leave_faction(self, user_id, current_faction):
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                'DELETE FROM faction_members WHERE user_id = $1 AND faction_name = $2',
                user_id, current_faction
            )
            await conn.execute(
                'UPDATE users SET faction_name = NULL WHERE id = $1',
                user_id
            )
            row = await conn.fetchrow(
                'SELECT COUNT(*) AS count FROM faction_members WHERE faction_name = $1',
                current_faction
            )
            if row and row['count'] == 0:
                await conn.execute(
                    'DELETE FROM factions WHERE name = $1',
                    current_faction
                )

