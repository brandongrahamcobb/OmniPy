''' role_manager.py The purpose of the program is to be backup and restore user roles if they leave and rejoin in 30 days.
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
from typing import List, Optional

import asyncpg
import asyncio
import discord
import time

EXPIRATION_TIME = 30 * 24 * 60 * 60

class RoleManager:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def close(self):
        if self.db_pool:
            await self.db_pool.close()

    async def backup_roles_for_member(self, member: discord.Member):
        if not self.db_pool:
            raise RuntimeError('Database pool is not initialized.')
        roles = [
            role.id for role in member.roles
            if not role.managed and role.name != '@everyone'
        ]
        timestamp = int(time.time())
        try:
            await self.db_pool.execute('''
                INSERT INTO roles_backup(user_id, role_ids, timestamp)
                VALUES($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET role_ids = EXCLUDED.role_ids,
                    timestamp = EXCLUDED.timestamp;
            ''', member.id, roles, timestamp)
        except Exception as e:
            print(f'Error backing up roles for {member}: {e}')

    async def restore_roles_for_member(self, member: discord.Member):
        if not self.db_pool:
            raise RuntimeError('Database pool is not initialized.')
        current_time = int(time.time())
        try:
            record = await self.db_pool.fetchrow('''
                SELECT role_ids, timestamp FROM roles_backup
                WHERE user_id = $1;
            ''', member.id)
            if record:
                backup_timestamp = record['timestamp']
                if (current_time - backup_timestamp) < EXPIRATION_TIME:
                    role_ids = record['role_ids']
                    guild = member.guild
                    valid_role_ids = [
                        role_id for role_id in role_ids
                        if guild.get_role(role_id) is not None
                    ]
                    roles_to_add = [guild.get_role(role_id) for role_id in valid_role_ids]
                    if roles_to_add:
                        await member.add_roles(*roles_to_add, reason='Role restoration upon rejoining.')
                await self.db_pool.execute('''
                    DELETE FROM roles_backup WHERE user_id = $1;
                ''', member.id)
        except Exception as e:
            print(f'Error restoring roles for {member}: {e}')

    async def clean_old_backups(self):
        if not self.db_pool:
            raise RuntimeError('Database pool is not initialized.')
        cutoff_timestamp = int(time.time()) - EXPIRATION_TIME
        try:
            result = await self.db_pool.execute('''
                DELETE FROM roles_backup
                WHERE timestamp < $1;
            ''', cutoff_timestamp)
        except Exception as e:
            print(f'Error cleaning old backups: {e}')
