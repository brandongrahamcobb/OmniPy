''' sativa.py  The purpose of this program is to provide permission-restricted commands to a Discord bot from cd ../../..
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
from discord.ext import commands, tasks
from omnipy.utils.handlers.message_manager import Paginator
from omnipy.utils.handlers.pdf_manager import PDFManager
from omnipy.utils.handlers.predicator import Predicator
from omnipy.utils.handlers.sql_manager import perform_backup, setup_backup_directory
from omnipy.utils.inc.helpers import *
from typing import Dict, List, Literal, Optional

import asyncio
import discord

class Sativa(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pdf_manager = PDFManager(self.bot.db_pool)
        self.predicator = Predicator(self.bot)

    @staticmethod
    def at_home(bot):
        async def predicate(ctx):
            return ctx.guild is not None and ctx.guild.id == bot.config.get("discord_testing_guild_id")
        return commands.check(predicate)

    @staticmethod
    def is_owner(bot):
        async def predicate(ctx):
            return ctx.guild is not None and (ctx.guild.owner_id == ctx.author.id or ctx.guild.owner_id == bot.config['discord_owner_id'])
        return commands.check(predicate)

    @commands.hybrid_command(name='backup', hidden=True)
    @commands.check(is_owner)
    async def backup_task(self, ctx: commands.Context):
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


    @commands.hybrid_command(name="uploadpdf", description="Upload a PDF to your catalog.", hidden=True)
    @discord.app_commands.describe(
        title="Title of the PDF.",
        description="Description of the PDF (optional).",
        tags="Tags associated with the PDF, separated by commas (optional).",
        file="The PDF file to upload."
    )
    @commands.check(at_home)
    async def upload_pdf(self, ctx: commands.Context, title: str, file: discord.Attachment, description: Optional[str] = None, tags: Optional[str] = None):
        if not self.predicator.is_spawd(ctx):
            return
        user_id = ctx.author.id

        # Ensure the file is a PDF
        if not file.filename.lower().endswith(".pdf"):
            await ctx.send("❌ Only PDF files are allowed.")
            return

        tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
        try:
            file_url = file.url
            pdf_id = await self.pdf_manager.upload_pdf(user_id, title, file_url, description, tags_list)
            await ctx.send(f"✅ PDF uploaded with ID: `{pdf_id}`.")
        except Exception as e:
            logger.error(f"Error uploading PDF: {e}")
            await ctx.send("❌ Failed to upload PDF.")

    @commands.hybrid_command(name="listpdfs", description="List all your uploaded PDFs.", hidden=True)
    @discord.app_commands.describe(tags="Filter by tags, separated by commas (optional).")
    @commands.check(at_home)
    async def list_pdfs(self, ctx: commands.Context, tags: Optional[str] = None):
        user_id = ctx.author.id
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
        try:
            pdfs = await self.pdf_manager.list_pdfs(user_id, tags_list)
            if not pdfs:
                await ctx.send("📭 No PDFs found.")
                return
            pages = []
            for i in range(0, len(pdfs), 5):
                embed = discord.Embed(title="📂 Your PDFs", color=discord.Color.blue())
                for pdf in pdfs[i:i + 5]:
                    title = pdf['title'] if pdf['title'] else "Untitled"
                    if len(title) > 200:
                        title = title[:197] + "..."
                    field_name = f"ID `{pdf['id']}`: {title}"
                    if len(field_name) > 256:
                        field_name = field_name[:253] + "..."
                    description = (pdf['description'] or 'N/A')
                    if len(description) > 500:
                        description = description[:497] + "..."
                    tags = ', '.join(pdf['tags']) if pdf['tags'] else 'N/A'
                    if len(tags) > 500:
                        tags = tags[:497] + "..."
                    embed.add_field(
                        name=field_name,
                        value=(
                            f"**Description:** {description}\n"
                            f"**Tags:** {tags}\n"
                            f"[Download PDF]({pdf['file_url']})"
                        ),
                        inline=False
                    )
                embed.set_footer(text=f"Page {len(pages) + 1} of {((len(pdfs) - 1) // 5) + 1}")
                pages.append(embed)
            paginator = Paginator(self.bot, ctx, pages)
            await paginator.start()
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.hybrid_command(name="searchpdfs", description="Search PDFs in your catalog.", hidden=True)
    @discord.app_commands.describe(query_text="Search term for title or tags.")
    @commands.check(at_home)
    async def search_pdfs(self, ctx: commands.Context, query_text: str):
        if not self.predicator.is_spawd(ctx):
            return
        user_id = ctx.author.id
        try:
            pdfs = await self.pdf_manager.search_pdfs(user_id, query_text)
            if not pdfs:
                await ctx.send("🔍 No matching PDFs found.")
                return

            embed = discord.Embed(title="🔎 Search Results", color=discord.Color.green())
            for pdf in pdfs:
                embed.add_field(
                    name=f"ID `{pdf['id']}`: {pdf['title']}",
                    value=(
                        f"**Description:** {pdf['description'] or 'N/A'}\n"
                        f"**Tags:** {', '.join(pdf['tags']) if pdf['tags'] else 'N/A'}\n"
                        f"[Download PDF]({pdf['file_url']})"
                    ),
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error searching PDFs: {e}")
            await ctx.send("❌ Failed to search PDFs.")

    @commands.hybrid_command(name="viewpdf", description="View details about a PDF.", hidden=True)
    @discord.app_commands.describe(pdf_id="ID of the PDF to view.")
    @commands.check(at_home)
    async def view_pdf(self, ctx: commands.Context, pdf_id: int):
        if not self.predicator.is_spawd(ctx):
            return
        try:
            pdf = await self.pdf_manager.view_pdf(pdf_id)
            if not pdf:
                await ctx.send("❌ PDF not found.")
                return

            embed = discord.Embed(title=f"📄 PDF ID: {pdf_id}", color=discord.Color.gold())
            embed.add_field(name="📂 Title", value=pdf["title"], inline=False)
            embed.add_field(name="📜 Description", value=pdf["description"] or "N/A", inline=False)
            embed.add_field(name="🏷️ Tags", value=", ".join(pdf["tags"]) if pdf["tags"] else "N/A", inline=False)
            embed.add_field(name="📂 Uploaded At", value=pdf["uploaded_at"], inline=False)
            embed.add_field(name="🔗 File URL", value=f"[Download PDF]({pdf['file_url']})", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error viewing PDF: {e}")
            await ctx.send("❌ Failed to retrieve PDF details.")

    @commands.hybrid_command(name="deletepdf", description="Delete a PDF from your catalog.", hidden=True)
    @discord.app_commands.describe(pdf_id="ID of the PDF to delete.")
    @commands.check(at_home)
    async def delete_pdf(self, ctx: commands.Context, pdf_id: int):
        if not self.predicator.is_spawd(ctx):
            return
        user_id = ctx.author.id
        try:
            success = await self.pdf_manager.delete_pdf(pdf_id, user_id)
            response = (
                f"✅ PDF with ID `{pdf_id}` deleted."
                if success else f"❌ PDF with ID `{pdf_id}` not found or not owned by you."
            )
            await ctx.send(response)
        except Exception as e:
            logger.error(f"Error deleting PDF: {e}")
            await ctx.send("❌ Failed to delete PDF.")

    def _format_reference_list(self, references: List[Dict]) -> str:
        if not references:
            return "📭 No references found."
        return "\n".join(
            f"ID `{ref['id']}`: {ref['title']} by {', '.join(ref['authors'])}" for ref in references
        )

    def _handle_large_response(self, content: str) -> str:
        if len(content) > 2000:
            buffer = io.StringIO(content)
            file = discord.File(fp=buffer, filename="output.txt")
            return file
        return content

    async def send_response(self, ctx: commands.Context, content: str, file: discord.File = None):
        """Sends a response to the context, handling both slash and text commands."""
        if isinstance(ctx, commands.Context):
            if ctx.interaction:
                await ctx.interaction.followup.send(content, file=file, ephemeral=True)
            else:
                await ctx.send(content, file=file)
        else:
            await ctx.send(content, file=file)

    async def send_embed_response(self, ctx: commands.Context, embed: discord.Embed):
        """Sends an embed as a response, handling both slash and text commands."""
        if isinstance(ctx, commands.Context):
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='load', hidden=True)
    @commands.check(at_home)
    async def load(self, ctx: commands.Context, *, module: str):
        try:
            await ctx.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')


    @commands.hybrid_command(name='reload', hidden=True)
    @commands.check(at_home)
    async def reload(self, ctx: commands.Context, *, module: str):
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer(ephemeral=True)
            await ctx.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='sync', hidden=True)
    @commands.check(is_owner)
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal['~', '*', '^']] = None) -> None:
        if not guilds:
            if spec == '~':
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '*':
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '^':
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            await ctx.send(
                f'Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}'
            )
            return
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f'Synced the tree to {ret}/{len(guilds)}.')


async def setup(bot: commands.bot):
    await bot.add_cog(Sativa(bot))
