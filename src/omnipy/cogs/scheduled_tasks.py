from collections import defaultdict
from discord.ext import commands, tasks
from omnipy.utils.handlers.sql_manager import perform_backup, setup_backup_directory
from omnipy.utils.inc.helpers import *
from omnipy.utils.handlers.role_manager import RoleManager
from omnipy.utils.handlers.tag_manager import TagManager

import asyncio
import datetime
import discord
import os
import pytz
import traceback

class Ruderalis(commands.Cog):

    def __init__(self, bot):
        self.backup_database.start()
        self.bot = bot
        self.channel_guild_map: Dict[int, int] = {
            787738272616808509: 730907954345279591,
            730907954877956179: 730907954345279591,
            1315735859848544378: 1300517536001036348,
            1347284827350630591: 1347284828894265398
        }
        self.config = bot.config
        self.guild_loops_index = defaultdict(int)
        self.tag_manager = TagManager(self.bot.db_pool)
        self.tags_loop.start()
        self.role_manager = RoleManager(self.bot.db_pool)
        self.role_backup_task.start()

    @tasks.loop(hours=24)  # This will run every 24 hours
    async def role_backup_task(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                await self.role_manager.backup_roles_for_member(member)
                await self.role_manager.restore_roles_for_member(member)
        await self.role_manager.clean_old_backups()

    @commands.after_invoke
    async def after_invoke(self, ctx):
        if hasattr(bot, 'db_pool'):
            await bot.db_pool.close()

    @tasks.loop(hours=24)
    async def backup_database(self):
        try:
            backup_dir = setup_backup_directory('./backups')
            backup_file = perform_backup(
                db_user='postgres',
                db_name='omnipy',
                db_host='localhost',
                backup_dir=backup_dir
            )
            logger.info(f'Backup completed successfully: {backup_file}')
        except Exception as e:
            logger.error(f'Error during database backup: {e}')

    @backup_database.before_loop
    async def before_backup(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def tags_loop(self):
        await self.bot.wait_until_ready()
        est_tz = pytz.timezone('US/Eastern')
        now_est = datetime.datetime.now(est_tz)
        if now_est.hour == 10 and now_est.minute == 0:
            guild_channels_map = {}
            for channel_id, guild_id in self.channel_guild_map.items():
                guild_channels_map.setdefault(guild_id, []).append(channel_id)
            for guild_id, channel_ids in guild_channels_map.items():
                loop_tags = await self.tag_manager.list_tags(
                    location_id=guild_id,
                    tag_type='loop'
                )
                loop_tags = [
                    t for t in loop_tags
                    if t.get('content') or t.get('attachment_url')
                ]
                if not loop_tags:
                    for cid in channel_ids:
                        channel = self.bot.get_channel(cid)
                        if channel:
                            await channel.send('No loop tags found for this guild.')
                    continue
                for cid in channel_ids:
                    channel = self.bot.get_channel(cid)
                    if channel:
                        current_index = self.channel_loops_index[cid]
                        tag = loop_tags[current_index % len(loop_tags)]
                        msg = tag.get('content') or tag.get('attachment_url')
                        if msg:
                            await channel.send(msg)
                        self.channel_loops_index[cid] = (current_index + 1) % len(loop_tags)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ruderalis(bot))

