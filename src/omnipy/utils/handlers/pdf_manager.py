'''
pdf_manager.py

Provides PDF management functionality for the Discord bot.
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
from discord.ext import commands
from omnipy.utils.inc.setup_logging import logger
from typing import List, Optional, Dict

import discord
import io
import logging

class PDFManager:
    def __init__(self, db_pool):
        self.pool = db_pool

    async def upload_pdf(self, user_id: int, title: str, file_url: str, description: Optional[str], tags: Optional[List[str]]) -> int:
        query = '''
            INSERT INTO pdf_catalog (user_id, title, file_url, description, tags)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        '''
        try:
            async with self.pool.acquire() as conn:
                pdf_id = await conn.fetchval(query, user_id, title, file_url, description, tags)
                return pdf_id
        except Exception as e:
            logger.error(f'Error uploading PDF: {e}')
            raise

    async def list_pdfs(self, user_id: int, tags: Optional[List[str]] = None) -> List[Dict]:
        base_query = 'SELECT * FROM pdf_catalog WHERE user_id = $1'
        params = [user_id]
        if tags:
            base_query += ' AND tags && $2'
            params.append(tags)
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(base_query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f'Error listing PDFs: {e}')
            raise

    async def search_pdfs(self, user_id: int, query_text: str) -> List[Dict]:
        query = '''
            SELECT * FROM pdf_catalog
            WHERE user_id = $1
              AND (title ILIKE '%' || $2 || '%' OR $2 = ANY(tags))
        '''
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, user_id, query_text)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f'Error searching PDFs: {e}')
            raise

    async def view_pdf(self, pdf_id: int) -> Optional[Dict]:
        query = 'SELECT * FROM pdf_catalog WHERE id = $1'
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, pdf_id)
                return dict(row) if row else None
        except Exception as e:
            logger.error(f'Error viewing PDF: {e}')
            raise

    async def delete_pdf(self, pdf_id: int, user_id: int) -> bool:
        query = 'DELETE FROM pdf_catalog WHERE id = $1 AND user_id = $2'
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, pdf_id, user_id)
                return result.endswith('DELETE 1')
        except Exception as e:
            logger.error(f'Error deleting PDF: {e}')
            raise
