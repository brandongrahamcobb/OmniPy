''' hybrid.py The purpose of this program is to be an extension to a Discord
    bot to provide the command functionality to Py_vyrtuous.
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
from discord import Embed, File, app_commands
from discord.ext import commands
from googletrans import Translator, LANGUAGES
from py_vyrtuous.utils.handlers.chemistry_manager import construct_helm_from_peptide, draw_fingerprint, draw_watermarked_molecule, get_mol, get_molecule_name, get_proximity, gsrs, manual_helm_to_smiles
from py_vyrtuous.utils.handlers.game_manager import Game
from py_vyrtuous.utils.handlers.image_manager import add_watermark, combine_gallery
from py_vyrtuous.utils.handlers.message_manager import Message
from py_vyrtuous.utils.handlers.predicator import Predicator
from py_vyrtuous.utils.handlers.tag_manager import TagManager
from py_vyrtuous.utils.inc.helpers import *
from py_vyrtuous.utils.inc.frames import extract_random_frames
from py_vyrtuous.utils.inc.google import google
from py_vyrtuous.utils.inc.script import script
from py_vyrtuous.utils.inc.unique_pairs import unique_pairs
from rdkit import Chem
from rdkit.Chem import AllChem, Crippen
from random import choice
from typing import Dict, List, Optional

import aiohttp
import asyncio
import datetime
import discord
import io
import json
import openai
import os
import pubchempy as pcp
import re
import shlex
import time
import traceback
import uuid
import requests

async def fetch_smiles_from_pubchem(cid: int) -> str | None:
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/SMILES/JSON"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning("PubChem request failed for CID %s with status %s", cid, resp.status)
                    return None
                data = await resp.json()
                return data["PropertyTable"]["Properties"][0]["SMILES"]
    except Exception as e:
        logger.exception("Error retrieving SMILES for CID %s: %s", cid, str(e))
        return None
        
class Hybrid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.game = Game(self.bot)
        self.predicator = Predicator(self.bot)
        self.tag_manager = TagManager(self.bot.db_pool)
        self.handler = Message(self.bot, self.config, self.bot.db_pool)
        self.loop_task: Optional[str] = None
        self.uploads_dir = "uploads"  # Directory to save uploaded files

        # Create uploads directory if it doesn't exist
        if not os.path.exists(self.uploads_dir):
            os.makedirs(self.uploads_dir)

    @commands.hybrid_command(name='colorize', description=f'Usage: between `lcolorize 0 0 0` and `lcolorize 255 255 255` or `l colorize <color>`')
    #@commands.has_permissions(manage_roles=True) # Do you have manage_roles permissions?
    async def colorize(self, ctx: commands.Context, r: str = commands.parameter(default='blurple', description='Anything between 0 and 255 or a color.'), g: str = commands.parameter(default='147', description='Anything betwen 0 and 255.'), b: str = commands.parameter(default='165', description='Anything between 0 and 255.')):
        if ctx.interaction:
            async with ctx.typing():
                await ctx.interaction.response.defer(ephemeral=True)
        if not await self.predicator.is_at_home_func(ctx.guild.id):
            return
        if not self.predicator.is_release_mode_func(ctx):
            return
        r = int(r)
        g = int(g)
        b = int(b)
        guildroles = await ctx.guild.fetch_roles()
        bot_top_role = max(ctx.guild.me.roles, key=lambda r: r.position)
        position = bot_top_role.position - 1 if bot_top_role.position > 1 else 1
        for arg in ctx.author.roles:
            if arg.name.isnumeric():
                await ctx.author.remove_roles(arg)
        for arg in guildroles:
            if arg.name.lower() == f'{r}{g}{b}':
                await ctx.author.add_roles(arg)
                await arg.edit(position=position)
                await ctx.send(f'I successfully changed your role color to {r}, {g}, {b}')
                return
        newrole = await ctx.guild.create_role(name=f'{r}{g}{b}', color=discord.Color.from_rgb(r, g, b), reason='new color')
        await newrole.edit(position=position)
        await ctx.author.add_roles(newrole)
        await ctx.send(f'I successfully changed your role color to {r}, {g}, {b}')
        
    def get_language_name_from_role(role_name: str) -> str:
        """
        Extracts the language name from a role name with either "original-" or "target-" prefix.
    
        Args:
            role_name: The role name (e.g., "original-french" or "target-spanish").
    
        Returns:
            The language name (e.g., "french" or "spanish").
            Returns None if the role name doesn't start with the expected prefixes.
        """
        if role_name.startswith("original-"):
            return role_name[len("original-"):]
        elif role_name.startswith("target-"):
            return role_name[len("target-"):]
        else:
            return None
    
    def get_original_language_name(ctx: discord.ext.commands.Context) -> str | None:
        """
        Gets the original language name from the user's roles.
    
        Args:
            ctx: The command context.
    
        Returns:
            The original language name (e.g., "french") if the user has an "original-" role,
            None otherwise.
        """
        for role in ctx.guild.roles:
            if role.name.startswith("original-"):
                return get_language_name_from_role(role.name)
        return None
    
    def get_target_language_name(ctx: discord.ext.commands.Context) -> str | None:
        """
        Gets the target language name from the user's roles.
    
        Args:
            ctx: The command context.
    
        Returns:
            The target language name (e.g., "spanish") if the user has a "target-" role,
            None otherwise.
        """
        for role in ctx.guild.roles:
            if role.name.startswith("target-"):
                return get_language_name_from_role(role.name)
        return None
        
    async def loop_tags(self, channel: discord.TextChannel):
        while True:
            try:
                loop_tags = await self.tag_manager.list_tags(channel.guild.id, tag_type='loop')
                if loop_tags:
                    random_tag = choice(loop_tags)
                    content_value = random_tag.get('content')
                    attachment_url_value = random_tag.get('attachment_url')
                    if content_value and attachment_url_value:
                        await channel.send(content_value)
                        await channel.send(attachment_url_value)
                    elif content_value:
                        await channel.send(content_value)
                    elif attachment_url_value:
                       await channel.send(attachment_url_value)
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error during loop_tags: {e}')

    def start_loop_task(self, channel: discord.TextChannel):
        if self.loop_task is None or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.loop_tags(channel))

    def stop_loop_task(self):
        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
            self.loop_task = None

    def get_language_code(self, language_name):
        language_name = language_name.lower()
        for lang_code, lang_name in LANGUAGES.items():
            if lang_name.lower() == language_name:
                return lang_code
        return None

    def has_translate_on(self, ctx: commands.Context) -> bool:
        target_roles = [role for role in ctx.guild.roles if role.name.startswith("target-")]
        original_roles = [role for role in ctx.guild.roles if role.name.startswith("original-")]
        if len(target_roles) == 1 and len(original_roles) == 1:
            return True
        else:
            return False
            
    def translate(ctx: discord.ext.commands.Context, text_to_translate: str, target_lang: str) -> str:
        translator = Translator()
    
        try:
            # Check if the target language is valid
            if target_lang not in LANGUAGES:
                return f"'{target_lang}' is not a supported language.  See available languages with !languages."
    
            translation = translator.translate(text_to_translate, dest=target_lang)
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return "An error occurred during translation. Please try again later."
            
    @commands.command(name='join')
    async def join(self, ctx):
        """Join the voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined {channel}')
        else:
            await ctx.send('You are not connected to a voice channel.')

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Disconnected from the voice channel.')
        else:
            await ctx.send('I am not in a voice channel.')

    @commands.command(name='play')
    async def play(self, ctx, *, file_name: str):
        """Play a music file from the computer."""
        if ctx.voice_client is None:
            await ctx.send('I need to be in a voice channel to play music.')
            return

        file_path = os.path.join(self.uploads_dir, file_name)
        # Check if the file exists
        if not os.path.isfile(file_path):
            await ctx.send('File not found. Please provide a valid file path.')
            return

        # Play the audio file
        ctx.voice_client.play(discord.FFmpegPCMAudio(file_name), after=lambda e: print(f'Finished playing: {e}'))
        await ctx.send(f'Now playing: {file_name}')

    @commands.command(name='upload')
    async def upload(self, ctx):
        """Upload a WAV file for playback."""
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.filename.endswith('.wav'):
                    file_path = os.path.join(self.uploads_dir, attachment.filename)
                    await attachment.save(file_path)
                    await ctx.send(f'Uploaded: {attachment.filename}')
                else:
                    await ctx.send('Please upload a WAV file.')
        else:
            await ctx.send('Please attach a file.')

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop playing music."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Stopped the music.')
        else:
            await ctx.send('No music is currently playing.')

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the music."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('Paused the music.')
        else:
            await ctx.send('No music is currently playing.')

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume playing music."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('Resumed the music.')
        else:
            await ctx.send('The music is not paused.')


    @commands.hybrid_command(
        name='d',
        description='Usage: d 2 <mol> <mol> or d glow <mol> or d gsrs <mol> or d shadow <mol>.'
    )
    async def d(
        self,
        ctx: commands.Context,
        option: str = commands.parameter(default='glow'),
        *,
        chems: str = commands.parameter(default=None),
        dupes: int = commands.parameter(default=1),
        backwards: bool = commands.parameter(default=False),
        linearity: bool = commands.parameter(default=False),
        rdkit_coords: bool = commands.parameter(default=True),
        r: int = commands.parameter(default=0)
    ):
        logger.info("Command `d` invoked by %s with option='%s'", ctx.author, option)
    
        if not self.predicator.is_release_mode_func(ctx):
            logger.warning("Blocked execution for %s: not in release mode", ctx.author)
            return
    
        # Type guards
        reverse = backwards if isinstance(backwards, bool) else False
        linearity = linearity if isinstance(linearity, bool) else False
        rdkit_bool = rdkit_coords if isinstance(rdkit_coords, bool) else True
        quantity = dupes if isinstance(dupes, int) else 1
        rotation = r if isinstance(r, int) else 0
    
        logger.debug("Parsed flags: reverse=%s, linearity=%s, rdkit=%s, quantity=%d, rotation=%d", reverse, linearity, rdkit_bool, quantity, rotation)
    
        async def function(linearity):
            logger.info("Executing drawing function with linearity=%s", linearity)
    
            async def get_attachment_text(ctx):
                logger.debug("Checking for attachments")
                if ctx.message.attachments:
                    logger.info("Attachment detected; reading content")
                    content = await ctx.message.attachments[0].read()
                    text = content.decode('utf-8')
                    logger.debug("Attachment content preview: %s", text[:100])
                    return text
                return None
    
            async def get_molecules(molecules):
                logger.info("Parsing molecule input: %s", molecules)
    
                if not molecules:
                    logger.warning("No molecules provided")
                    await self.handler.send_message(ctx, content='No molecules provided.')
                    return None, None, None
    
                name_match = re.search(r'"([^"]+)"$', molecules)
                name = name_match.group(1) if name_match else "Untitled"
                molecule_list = molecules[:name_match.start()].strip() if name_match else molecules
    
                molecule_parts = re.split(r'(?<!")\.(?!")', molecule_list) if '.' in molecule_list else [molecule_list]
                logger.debug("Molecule name: %s, Parts: %s", name, molecule_parts)
    
                converted_smiles = []
                for mol in molecule_parts:
                    logger.info("Processing molecule token: %s", mol)
                    mol_obj = Chem.MolFromSmiles(mol)
                    if mol_obj:
                        converted_smiles.append(mol)
                        logger.debug("Valid SMILES directly: %s", mol)
                        continue
    
                    logger.info("SMILES failed; trying PubChem")
                    compounds = pcp.get_compounds(mol, 'name')
                    logger.info(compounds)
                    smiles = await fetch_smiles_from_pubchem(compounds[0].cid)
                    logger.info(smiles)
    
                    if not smiles and self.has_translate_on(ctx):
                        logger.info("Trying translation fallback for: %s", mol)
                        try:
                            mol_translated = translate(mol, get_original_language_name(), get_target_language_name())
                            mol_obj = Chem.MolFromSmiles(mol_translated)
                            smiles = mol_translated if mol_obj else None
                        except Exception as e:
                            logger.exception("Translation failed: %s", str(e))
    
                    if not smiles:
                        logger.info("Trying HELM fallback for: %s", mol)
                        try:
                            helm = construct_helm_from_peptide(mol)
                            smiles = manual_helm_to_smiles(helm)
                        except Exception as e:
                            logger.exception("HELM conversion failed: %s", str(e))
    
                    if not smiles:
                        logger.error("Could not resolve molecule: %s", mol)
                        embed = discord.Embed(description=f'Invalid molecule: {mol}')
                        await self.handler.send_message(ctx, embed=embed)
                        return None, None, None
    
                    converted_smiles.append(smiles)
    
                molecule_objects = [get_mol(s, reverse=reverse) for s in converted_smiles]
                logger.debug("Converted SMILES: %s", converted_smiles)
                return molecule_objects, molecule_parts, name
    
            # Read molecule data
            molecules = chems or (await get_attachment_text(ctx) if ctx.message.attachments else None)
            logger.debug("Final molecule input: %s", molecules)
    
            if option == '2':
                molecule_objects, names, name = await get_molecules(molecules)
                if not molecule_objects:
                    return
    
                pairs = unique_pairs(names)
                if not pairs:
                    logger.warning("No valid pairs found")
                    embed = discord.Embed(description='No valid pairs found.')
                    await self.handler.send_message(ctx, embed=embed)
                    return
    
                for pair in pairs:
                    mol, refmol = molecule_objects[0], molecule_objects[1]
                    if not mol or not refmol:
                        embed = discord.Embed(description=f'{pair[0]} or {pair[1]} is invalid.')
                        await self.handler.send_message(ctx, embed=embed)
                        continue
    
                    fingerprints = [
                        draw_fingerprint([mol, refmol], rdkit_bool),
                        draw_fingerprint([refmol, mol], rdkit_bool, rotation)
                    ]
                    if len(fingerprints) >= 2:
                        linearity = True
                    combined = combine_gallery(fingerprints, names, name, 1, linearity)
                    await self.handler.send_message(ctx, file=discord.File(combined, 'molecule_comparison.png'))
    
            elif option == 'glow':
                molecule_objects, names, name = await get_molecules(molecules)
                if not molecule_objects:
                    return
                fingerprints = [draw_fingerprint([m, m], rdkit_bool, rotation) for m in molecule_objects]
                combined = combine_gallery(fingerprints, names, name, quantity, linearity)
                await self.handler.send_message(ctx, file=discord.File(combined, 'molecule_comparison.png'))
    
            elif option == 'gsrs':
                if not molecules:
                    await self.handler.send_message(ctx, content='No molecules provided.')
                    return
                args = shlex.split(molecules)
                for molecule_name in args:
                    if not molecule_name:
                        await self.handler.send_message(ctx, content='Invalid molecule.')
                        return
                    if self.has_translate_on(ctx):
                        molecule_name = translate(molecule_name, get_original_language_name(), get_target_language_name())
                    watermarked_image = gsrs(molecule_name)
                    with io.BytesIO() as bio:
                        watermarked_image.save(bio, format='PNG')
                        bio.seek(0)
                        await self.handler.send_message(ctx, file=discord.File(fp=bio, filename='watermarked_image.png'))
    
            elif option == 'shadow':
                molecule_objects, names, name = await get_molecules(molecules)
                if not molecule_objects:
                    return
                molecule_images = [draw_watermarked_molecule(m, rdkit_bool) for m in molecule_objects]
                if len(molecule_images) in [2, 3]:
                    linearity = True
                combined = combine_gallery(molecule_images, names, name, quantity, linearity)
                await self.handler.send_message(ctx, file=discord.File(combined, 'molecule_comparison.png'))
    
            else:
                logger.warning("Unknown option: %s", option)
                await self.handler.send_message(ctx, content='Invalid option. Use `2`, `glow`, `gsrs`, or `shadow`.')
    
        # Respond via interaction or typing indicator
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer(ephemeral=True)
            else:
                if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                    perms = ctx.channel.permissions_for(ctx.guild.me)
                    if perms.send_messages:
                        async with ctx.typing():
                            await function(linearity)
                            return
            await function(linearity)
        except Exception as e:
            logger.exception("Unhandled error in command `d`: %s", str(e))

    @commands.hybrid_command()
    async def faction(self, ctx, action: str, *, faction_name: str = None):
        if not self.predicator.is_release_mode_func(ctx):
            return
        faction_input = str(faction_name) if faction_name is not None else None  # ✅ Moved outside
        async def function():
            user_id = ctx.author.id
            act = action.lower()
            user = await self.game.get_user(user_id)
            if not user:
                await self.handler.send_message(ctx, content="You have not interacted with the bot yet. Earn XP first!")
                return
            if act == "create":
                if not faction_input:
                    await self.handler.send_message(ctx, content="You must specify a faction name!")
                    return
                if user["faction_name"]:
                    await self.handler.send_message(ctx, content="You are already in a faction!")
                    return
                existing_faction = await self.game.get_faction(faction_input)
                if existing_faction:
                    await self.handler.send_message(ctx, content=f"Faction **{faction_input}** already exists!")
                    return
                success = await self.game.create_faction(faction_input, user_id)
                if success:
                    await self.handler.send_message(ctx, content=f"Faction **{faction_input}** has been created! 🎉")
                else:
                    await self.handler.send_message(ctx, content="There was an error creating the faction.")
                return
            elif act == "join":
                if not faction_input:
                    await self.handler.send_message(ctx, content="You must specify a faction to join!")
                    return
                if user["faction_name"]:
                    await self.handler.send_message(ctx, content="You are already in a faction!")
                    return
                response = await self.game.join_faction(faction_input, user_id)
                await self.handler.send_message(ctx, content=f"{ctx.author.mention}, {response}")
                return
            elif act == "leave":
                current_faction = user.get("faction_name")
                if not current_faction:
                    await self.handler.send_message(ctx, content="You are not in a faction!")
                    return
                await self.game.leave_faction(user_id, current_faction)
                await self.handler.send_message(ctx, content="You have left your faction and are now factionless.")
                return
            elif act == "switch":
                if not faction_input:
                    await self.handler.send_message(ctx, content="You must specify a faction to switch to!")
                    return
                if user["faction_name"] == faction_input:
                    await self.handler.send_message(ctx, content="You are already in that faction!")
                    return
                new_faction = await self.game.get_faction(faction_input)
                if not new_faction:
                    await self.handler.send_message(ctx, content="The faction you want to switch to does not exist!")
                    return
                if user["faction_name"]:
                    await self.game.leave_faction(user_id, user["faction_name"])
                response = await self.game.join_faction(faction_input, user_id)
                await self.handler.send_message(ctx, content=f"{ctx.author.mention}, you have switched to faction **{faction_input}**.")
                return
            elif act == "info":
                faction_to_use = faction_input or user.get("faction_name")
                if not faction_to_use:
                    await self.handler.send_message(ctx, content="You are not in a faction, and no faction name was provided!")
                    return
                faction_data = await self.game.get_faction(faction_to_use)
                if not faction_data:
                    await self.handler.send_message(ctx, content="Faction not found!")
                    return
                members = await self.game.get_faction_members(faction_to_use)
                members_count = len(members)
                await self.handler.send_message(ctx, content=
                    f"**Faction: {faction_to_use}**\n"
                    f"🔹 Level: {faction_data['level']}\n"
                    f"🔹 XP: {faction_data['xp']}\n"
                    f"🔹 Members: {members_count}"
                )
                return
            elif act == "leaderboard":
                factions = await self.game.get_faction_leaderboard()
                if not factions:
                    await self.handler.send_message(ctx, content="No factions found.")
                    return
                leaderboard = "**🏆 Faction Leaderboard:**\n"
                for i, faction in enumerate(factions[:10], start=1):
                    leaderboard += f"{i}. **{faction['name']}** - Level {faction['level']}, XP: {faction['xp']}\n"
                await self.handler.send_message(ctx, content=leaderboard)
                return
            else:
                await self.handler.send_message(ctx, content="Invalid action! Use `create`, `join`, `switch`, `info`, or `leaderboard`.")
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='frame', description='Sends a frame from a number of animal cruelty footage sources.')
    async def frame(self, ctx: commands.Context):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            await ctx.interaction.response.defer(ephemeral=True)
            video_path = 'frogs.mov'
            output_dir = 'frames'
            frames = extract_random_frames(video_path, output_dir)
            for frame in frames:
                await self.handler.send_message(ctx, content=None, file=discord.File(frame))
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='logp')
    async def logp(self, ctx: commands.Context, *, molecules: str):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            args = shlex.split(molecules)
            for arg in args:
                compounds = pcp.get_compounds(arg, 'name')
                compound_data = compounds[0].to_dict(properties=['isomeric_smiles'])
                mol = Chem.MolFromSmiles(compound_data['isomeric_smiles'])
                log_p = Crippen.MolLogP(mol)
                await self.handler.send_message(ctx, content=f'Your octanol:water coefficient is: {log_p}')
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.command(name='script', description=f'Usage: lscript <NIV/ESV/Quran> <Book>.<Chapter>.<Verse>')
    async def script(self, ctx: commands.Context, version: str, *, reference: str):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            async with ctx.typing():
                await self.handler.send_message(ctx, content=script(version, reference))
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='search', description=f'Usage: lsearch <query>. Search Google.')
    async def search(self, ctx: commands.Context, *, query: str = commands.parameter(default=None, description='Google search a query.')):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            results = google(query)
            embed = discord.Embed(title=f'Search Results for \"{query}\"', color=discord.Color.blue())
            for result in results:
                title, link = result.get("title", "No Title"), result.get("link", "No Link")
                embed.add_field(name=title, value=link, inline=False)
            await self.handler.send_message(ctx, content=None, file=None, embed=embed)
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='sim')
    async def sim(self, ctx: commands.Context, *, molecules: str):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            args = shlex.split(molecules)
            similarity = get_proximity(get_mol(args[0]), get_mol(args[1]))
            await self.handler.send_message(ctx, content=similarity)
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='smiles')
    async def smiles(self, ctx: commands.Context, *, molecules: str, reverse: bool = True):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            args = shlex.split(molecules)
            output = []
            for arg in args:
                compounds = pcp.get_compounds(arg, 'name')
                if compounds:
                    smiles_str = compounds[0].isomeric_smiles
                    output.append(f"{arg}: {smiles_str}")
                    continue
                else:
                    mol = Chem.MolFromSmiles(arg)
                    if mol:
                        smiles_str = Chem.MolToSmiles(mol, canonical=False)
                        output.append(f"{arg}: {smiles_str}")
                        continue
                try:
                    helm = construct_helm_from_peptide(arg)
                    smiles_str = manual_helm_to_smiles(helm)
                    output.append(f"{arg}: {smiles_str}")
                except Exception as e:
                    output.append(f"{arg}: Failed to generate molecule.")
                try:
                     mol = get_mol(arg, reverse=reverse)
                except Exception as e:
                    output.append(f"{arg}: Failed to generate molecule.")
            result = "\n".join(output)
            if len(result) > 2000:
                with open(f"smiles_{ctx.author.name}.txt", "w") as f:
                    f.write(result)
                await self.handler.send_message(ctx, content=None, file=discord.File(f"smiles_{ctx.author.name}.txt"))
            else:
                await self.handler.send_message(ctx, content=f"SMILES:\n```\n{result}\n```")
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()

    @commands.hybrid_command(name='tag', description='Manage or retrieve tags. Sub-actions: add, borrow, list, loop, rename, remove, update')
    async def tag_command(
        self,
        ctx: commands.Context,
        action: str = commands.parameter(default=None, description='Action: add, update, remove, list, loop.'),
        name: Optional[str] = commands.parameter(default=None, description='Name of the tag.'),
        content: Optional[str] = commands.parameter(default=None, description='Content for the tag (if applicable).'),
        tag_type: Optional[str] = commands.parameter(default=None, description='Optional tag type: default or loop.')
    ):
        if not self.predicator.is_release_mode_func(ctx):
            return
        async def function():
            attachment_url = None
            array = None
            if content and ctx.message.attachments:
                attachment_url = ctx.message.attachments[0].url
                array = await self.handler.process_array(content, attachments=ctx.message.attachments)
            elif content:
                array = await self.handler.process_array(content)
            elif ctx.message.attachments:
                attachment_url = ctx.message.attachments[0].url
                array = await self.handler.process_attachments(ctx.message.attachments)
            if array:
                async for flagged, reasons in self.handler.completion_prep(array):
                    if flagged:
                        return
            act = action.lower() if action else None
            if act == 'add':
                resolved_tag_type = 'loop' if (tag_type and tag_type.lower() == 'loop') else 'default'
                if not name:
                    return await self.handler.send_message(ctx, content=f'Usage: \"{self.bot.command_prefix}tag add <name> \"content\" [loop]`')
                try:
                    await self.tag_manager.add_tag(
                        name=name,
                        location_id=ctx.guild.id,
                        owner_id=ctx.author.id,
                        content=content,
                        attachment_url=attachment_url,
                        tag_type=resolved_tag_type
                    )
                    await self.handler.send_message(ctx, content=f'Tag \"{name}\" (type: {resolved_tag_type}) added successfully.')
                except ValueError as ve:
                    await self.handler.send_message(ctx, content=str(ve))
                except Exception as e:
                    logger.error(f'Error adding tag: {e}')
                    await self.handler.send_message(ctx, content='An error occurred while adding the tag.')
            if act == 'borrow':
                if not name:
                    return await self.handler.send_message(ctx, content=
                        f'Usage: `{self.bot.command_prefix}tag borrow <tag_name> [@owner]`'
                    )
                mentioned_users = ctx.message.mentions
                if mentioned_users:
                    owner = mentioned_users[0]
                    owner_id = owner.id
                else:
                    owner = None
                    owner_id = None
                try:
                    await self.tag_manager.borrow_tag(
                        tag_name=name,
                        location_id=ctx.guild.id,
                        borrower_id=ctx.author.id,
                        owner_id=owner_id,
                    )
                    if owner:
                        owner_display = owner.display_name
                        await self.handler.send_message(ctx, content=
                            f'You have successfully borrowed the tag "{name}" from {owner_display}.'
                        )
                    else:
                        await self.handler.send_message(ctx, content=
                            f'You have successfully borrowed the tag "{name}".'
                        )
                except ValueError as ve:
                    await self.handler.send_message(ctx, content=str(ve))
                except RuntimeError as re:
                    await self.handler.send_message(ctx, content=str(re))
                except Exception as e:
                    logger.error(f'Unexpected error during tag borrowing: {e}')
                    await self.handler.send_message(ctx, content=
                        'An unexpected error occurred while borrowing the tag.'
                    )
            elif act == 'list':
                filter_tag_type = name.lower() if name and name.lower() in ('loop', 'default') else None
                try:
                    tags = await self.tag_manager.list_tags(
                        location_id=ctx.guild.id,
                        owner_id=ctx.author.id,
                        tag_type=filter_tag_type
                    )
                    if not tags:
                        await self.handler.send_message(ctx, content='No tags found.')
                    else:
                        tag_list = '\n'.join(f'**{t["name"]}**' for t in tags)
                        await self.handler.send_message(ctx, content=f'Tags:\n{tag_list}')
                except Exception as e:
                    logger.error(f'Error listing tags: {e}')
                    await self.handler.send_message(ctx, content='An error occurred while listing your tags.')
            elif act == 'remove':
                if not name:
                    return await self.handler.send_message(ctx, content=f'Usage: \"{self.bot.command_prefix}tag remove <name>`')
                try:
                    result = await self.tag_manager.delete_tag(
                        name=name,
                        location_id=ctx.guild.id,
                        owner_id=ctx.author.id
                    )
                    if result > 0:
                        await self.handler.send_message(ctx, content=f'Tag \"{name}\" removed.')
                    else:
                        await self.handler.send_message(ctx, content=f'Tag \"{name}\" not found or you do not own it.')
                except Exception as e:
                    logger.error(f'Error removing tag: {e}')
                    await self.handler.send_message(ctx, content='An error occurred while removing the tag.')
            elif act == 'loop':
                 if not name:
                     return await self.handler.send_message(ctx, content=f'Usage: \"{self.bot.command_prefix}tag loop on <#channel>` or \"{self.bot.command_prefix}tag loop off`')
                 if name.lower() == 'on':
                     channel = ctx.channel
                     if content and content.startswith('<#') and content.endswith('>'):
                         channel_id = int(content.strip('<#>'))
                         maybe_chan = self.bot.get_channel(channel_id)
                         if maybe_chan is not None:
                             channel = maybe_chan
                     try:
                         await self.tag_manager.set_loop_config(ctx.guild.id, channel.id, True)
                         self.start_loop_task(channel)
                         await self.handler.send_message(ctx, content=f'Looping enabled in {channel.mention}.')
                     except Exception as e:
                         logger.error(f'Error enabling loop: {e}')
                         await self.handler.send_message(ctx, content='Could not enable loop.')
                 elif name.lower() == 'off':
                     try:
                         await self.tag_manager.set_loop_config(ctx.guild.id, None, False)
                         self.stop_loop_task()
                         await self.handler.send_message(ctx, content='Looping disabled.')
                     except Exception as e:
                         logger.error(f'Error disabling loop: {e}')
                         await self.handler.send_message(ctx, content='Could not disable loop.')
            elif action == 'rename':
                if not name or not content:
                    return await self.handler.send_message(ctx, content=f'Usage: \"{self.bot.command_prefix}tag rename <old_name> <new_name>`')
                old_name = name
                new_name = content
                try:
                    row_count = await self.tag_manager.rename_tag(
                        old_name=old_name,
                        new_name=new_name,
                        location_id=ctx.guild.id,
                        owner_id=ctx.author.id
                    )
                    if row_count > 0:
                        await self.handler.send_message(ctx, content=f'Tag \"{old_name}\" renamed to \"{new_name}\".')
                    else:
                        await self.handler.send_message(ctx, content=f'Tag \"{old_name}\" not found or you do not own it.')
                except ValueError as ve:
                    await self.handler.send_message(ctx, content=str(ve))
                except Exception as e:
                    logger.error(f'Error renaming tag: {e}')
                    await self.handler.send_message(ctx, content='An error occurred while renaming the tag.')
            elif action == 'update':
                if not name:
                    return await self.handler.send_message(ctx, content=f'Usage: {self.bot.command_prefix}tag update <name> \"new content\" [loop|default]`')
                resolved_tag_type = (
                    tag_type.lower() if tag_type and tag_type.lower() in ('default', 'loop') else None
                )
                updates = {}
                if content is not None:
                    updates['content'] = content
                if attachment_url is not None:
                    updates['attachment_url'] = attachment_url
                if resolved_tag_type is not None:
                    updates['tag_type'] = resolved_tag_type
                try:
                    result = await self.tag_manager.update_tag(
                        name=name,
                        location_id=ctx.guild.id,
                        owner_id=ctx.author.id,
                        updates=updates
                     )
                    if result > 0:
                        await self.handler.send_message(ctx, content=f'Tag \"{name}\" updated.')
                    else:
                        await self.handler.send_message(ctx, content=f'Tag \"{name}\" not found or you do not own it.')
                except Exception as e:
                    await self.handler.send_message(ctx, content='An error occurred while updating the tag.')
            else:
                try:
                    tag = await self.tag_manager.get_tag(ctx.guild.id, act)
                    if tag:
                        content_value = tag.get('content')
                        attachment_url_value = tag.get('attachment_url')
                        if content_value and attachment_url_value:
                            await self.handler.send_message(ctx, content=content_value)
                            await self.handler.send_message(ctx, content=attachment_url_value)
                        elif content_value:
                            await self.handler.send_message(ctx, content=content_value)
                        elif attachment_url_value:
                            await self.handler.send_message(ctx, content=attachment_url_value)
                        else:
                            await self.handler.send_message(ctx, content=f'Tag \"{act}\" has no content.')
                    else:
                        await self.handler.send_message(ctx, content=f'Tag \"{act}\" not found.')
                except Exception as e:
                    logger.error(f'Error fetching tag \"{act}\": {e}')
                    await self.handler.send_message(ctx, content=f'An error occurred while fetching tag \"{act}\".')
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)
            await function()
        else:
            if ctx.channel and isinstance(ctx.channel, discord.abc.GuildChannel):
                permissions = ctx.channel.permissions_for(ctx.guild.me)
                if permissions.send_messages:
                    async with ctx.typing():
                        await function()
                else:
                    await function()
            else:
                async with ctx.typing():
                    await function()


    @commands.command(name='language', description=f'Usage: <command-prefix>language on <your-language> <target-language>')
    async def language(self, ctx, toggle: str, target_lang: str = 'english', source_lang: str = 'auto'):
        """
        Enables or disables translation preferences for a user.  Dynamically creates roles based on language.
        """
    
        if toggle.lower() == 'on':
            target_lang_code = self.get_language_code(target_lang)
            source_lang_code = self.get_language_code(source_lang)
    
            if target_lang_code is None or source_lang_code is None:
                await self.handler.send_message(ctx, content=f'{ctx.author.mention}, please specify valid language names.')
                return
    
            # Create/Get Target Language Role
            target_role_name = f"target-{target_lang}"
            target_role = None
            for role in ctx.guild.roles:
                if role.name == target_role_name:
                    target_role = role
                    break
    
            if not target_role:
                try:
                    target_role = await ctx.guild.create_role(name=target_role_name, permissions=discord.Permissions(manage_messages=True)) #Adjust permissions as needed
                    await ctx.message.guild.me.add_roles(target_role)
                except discord.Forbidden:
                    await self.handler.send_message(ctx, content=f'{ctx.author.mention}, I don\'t have permission to create roles.')
                    return
                except discord.HTTPException as e:
                    await self.handler.send_message(ctx, content=f'{ctx.author.mention}, An error occurred creating the target role: {e}')
                    return
    
            # Create/Get Source Language Role
            original_role_name = f"original-{source_lang}"
            original_role = None
            for role in ctx.guild.roles:
                if role.name == original_role_name:
                    original_role = role
                    break
    
            if not original_role:
                try:
                    original_role = await ctx.guild.create_role(name=original_role_name, permissions=discord.Permissions(manage_messages=True)) #Adjust permissions as needed
                    await ctx.message.guild.me.add_roles(original_role)
                except discord.Forbidden:
                    await self.handler.send_message(ctx, content=f'{ctx.author.mention}, I don\'t have permission to create roles.')
                    return
                except discord.HTTPException as e:
                    await self.handler.send_message(ctx, content=f'{ctx.author.mention}, An error occurred creating the original role: {e}')
                    return
    
            # Assign/Remove Roles
            try:
                if not ctx.author.get_role(target_role.id):
                    await ctx.author.add_roles(target_role)
                if ctx.author.get_role(original_role.id):
                    await ctx.author.remove_roles(original_role)
            except discord.Forbidden:
                await self.handler.send_message(ctx, content=f'{ctx.author.mention}, I don\'t have permission to manage your roles.')
                return
    
            await self.handler.send_message(ctx, content=f'{ctx.author.mention}, translation enabled from {source_lang} to {target_lang}.')
    
        elif toggle.lower() == 'off':
            # Remove target role and potentially add original role back (adjust as needed)
            target_lang_code = self.get_language_code(target_lang)
            target_role_name = f"target-{target_lang}"
            target_role = None
            for role in ctx.guild.roles:
                if role.name == target_role_name:
                    target_role = role
                    break
    
            if target_role:
                try:
                    await ctx.author.remove_roles(target_role)
                except discord.Forbidden:
                    await self.handler.send_message(ctx, content=f'{ctx.author.mention}, I don\'t have permission to manage your roles.')
                    return
    
                await self.handler.send_message(ctx, content=f'{ctx.author.mention}, translation disabled.')
            else:
                await self.handler.send_message(ctx, content=f'{ctx.author.mention}, target role not found.')
    
        else:
            await self.handler.send_message(ctx, content=f'{ctx.author.mention}, please specify \'on\' or \'off\'.')

async def setup(bot: commands.Bot):
    await bot.add_cog(Hybrid(bot))
