# tag.py
'''
The purpose of this program is to provide tagging and database functionality.
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

from omnipy.utils.inc.setup_logging import logger
from typing import Dict, List, Optional

class TagManager:
    def __init__(self, db_pool):
        self.pool = db_pool

    async def add_tag(
        self,
        name: str,
        location_id: int,
        owner_id: int,
        content: Optional[str] = None,
        attachment_url: Optional[str] = None,
        tag_type: str = 'default'
    ):
        query_check = '''
            SELECT 1
            FROM tags
            WHERE name = $1 AND location_id = $2 AND owner_id = $3
        '''
        query_insert = '''
            INSERT INTO tags (name, location_id, content, attachment_url, owner_id, tag_type)
            VALUES ($1, $2, $3, $4, $5, $6)
        '''
        try:
            async with self.pool.acquire() as conn:
                existing_tag = await conn.fetchval(query_check, name, location_id, owner_id)
                if existing_tag:
                    raise ValueError(f'A tag with the name \'{name}\' already exists for you in this location.')
                await conn.execute(query_insert, name, location_id, content, attachment_url, owner_id, tag_type)
        except Exception as e:
            logger.error(f'Failed to add tag: {e}')
            raise

    async def borrow_tag(
        self,
        tag_name: str,
        location_id: int,
        borrower_id: int,
        owner_id: Optional[int] = None
    ):
        query_fetch = '''
            SELECT content, attachment_url, tag_type, owner_id
            FROM tags
            WHERE LOWER(name) = LOWER($1) AND location_id = $2
        '''
        if owner_id:
            query_fetch += ' AND owner_id = $3'
            params_fetch = (tag_name, location_id, owner_id)
        else:
            query_fetch += ' LIMIT 1'
            params_fetch = (tag_name, location_id)
        query_insert = '''
            INSERT INTO tags (name, location_id, content, attachment_url, owner_id, tag_type)
            VALUES ($1, $2, $3, $4, $5, $6)
        '''
        query_check_borrower = '''
            SELECT 1
            FROM tags
            WHERE LOWER(name) = LOWER($1) AND location_id = $2 AND owner_id = $3
        '''
        try:
            async with self.pool.acquire() as conn:
                existing = await conn.fetchval(
                    query_check_borrower, tag_name, location_id, borrower_id
                )
                if existing:
                    raise ValueError(
                        f'You already have a tag named \'{tag_name}\' in this server.'
                    )
                tag = await conn.fetchrow(query_fetch, *params_fetch)
                if not tag:
                    if owner_id:
                        raise ValueError(
                            f'Tag \'{tag_name}\' does not exist for the specified user.'
                        )
                    else:
                        raise ValueError(
                            f'Tag \'{tag_name}\' does not exist in this server.'
                        )
                await conn.execute(
                    query_insert,
                    tag_name,
                    location_id,
                    tag['content'],
                    tag['attachment_url'],
                    borrower_id,
                    tag['tag_type'],
                )
        except ValueError as ve:
            logger.warning(f'Borrowing failed: {ve}')
            raise ve
        except Exception as e:
            logger.error(f'Failed to borrow tag: {e}')
            raise RuntimeError('An error occurred while borrowing the tag.')

    async def get_tag(self, location_id: int, name: str) -> Optional[Dict]:
        query = '''
            SELECT name, content, attachment_url, tag_type, created_at
            FROM tags
            WHERE location_id = $1
              AND LOWER(name) = LOWER($2)
        '''
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, location_id, name)
                if row:
                    logger.info(f'Tag \'{name}\' fetched successfully.')
                    return dict(row)
                else:
                    logger.info(f'Tag \'{name}\' not found in location {location_id}.')
                    return None
        except Exception as e:
            logger.error(f'Failed to fetch tag: {e}')
            raise

    async def rename_tag(self, old_name: str, new_name: str, location_id: int, owner_id: int) -> int:
        query_check = '''
            SELECT 1
            FROM tags
            WHERE LOWER(name) = LOWER($1)
              AND location_id = $2
              AND owner_id = $3
        '''
        query_rename = '''
            UPDATE tags
            SET name = $1
            WHERE LOWER(name) = LOWER($2)
              AND location_id = $3
              AND owner_id = $4
        '''
        try:
            async with self.pool.acquire() as conn:
                existing = await conn.fetchval(query_check, new_name, location_id, owner_id)
                if existing:
                    raise ValueError(f'A tag named \'{new_name}\' already exists for you in this location.')
                result = await conn.execute(query_rename, new_name, old_name, location_id, owner_id)
                row_count = int(result.split()[-1])  # e.g., 'UPDATE 1' → 1
                return row_count
        except Exception as e:
            logger.error(f'Failed to rename tag: {e}')
            raise

    async def update_tag(
        self,
        name: str,
        location_id: int,
        owner_id: int,
        updates: dict
    ) -> int:
        if not updates:
            return 0
        fields_to_update = []
        params = []
        i = 1
        for field, value in updates.items():
            if field not in {'name', 'location_id', 'owner_id'}:  # Prevent updating PKs
                fields_to_update.append(f'{field} = ${i}')
                params.append(value)
                i += 1
        if not fields_to_update:
            return 0
        query = f'''
            UPDATE tags
            SET {', '.join(fields_to_update)}
            WHERE LOWER(name) = LOWER(${i})
              AND location_id = ${i+1}
              AND owner_id = ${i+2}
        '''
        params.extend([name, location_id, owner_id])

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *params)
                row_count = int(result.split()[-1])
                if row_count > 0:
                    logger.info(f'Tag \'{name}\' updated successfully.')
                else:
                    logger.warning(f'No tag updated. Tag \'{name}\' may not exist.')
                return row_count
        except Exception as e:
            logger.error(f'Failed to update tag: {e}')
            raise RuntimeError('An error occurred while updating the tag.')

    async def delete_tag(self, name: str, location_id: int, owner_id: int) -> int:
        '''
        Deletes a tag from the database.

        :return: The number of rows deleted.
        '''
        query = '''
            DELETE FROM tags
            WHERE LOWER(name) = LOWER($1)
              AND location_id = $2
              AND owner_id = $3
        '''
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, name, location_id, owner_id)
                row_count = int(result.split()[-1])
                return row_count
        except Exception as e:
            logger.error(f'Failed to delete tag: {e}')
            raise

    async def list_tags(self, location_id: int, owner_id: Optional[int] = None, tag_type: Optional[str] = None) -> List[dict]:
        query = 'SELECT name, content, attachment_url, tag_type, created_at FROM tags WHERE location_id = $1'
        params = [location_id]
        idx = 2
        if owner_id is not None:
            query += f' AND owner_id = ${idx}'
            params.append(owner_id)
            idx += 1
        if tag_type is not None:
            query += f' AND tag_type = ${idx}'
            params.append(tag_type)
            idx += 1
        query += ' ORDER BY created_at DESC'
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                logger.info(f'Listed {len(rows)} tags for location {location_id}.')
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f'Failed to list tags: {e}')
            raise

    async def set_loop_config(self, guild_id: int, channel_id: Optional[int], enabled: bool):
        query = '''
            INSERT INTO loop_configs (guild_id, channel_id, enabled)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id)
            DO UPDATE SET
                channel_id = EXCLUDED.channel_id,
                enabled = EXCLUDED.enabled
        '''
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, guild_id, channel_id, enabled)
        except Exception as e:
            logger.error(f'Failed to set loop config: {e}')
            raise

    async def get_loop_config(self, guild_id: int) -> Optional[dict]:
        query = '''
            SELECT guild_id, channel_id, enabled
            FROM loop_configs
            WHERE guild_id = $1
        '''
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, guild_id)
                if row:
                    return dict(row)
                else:
                    return None
        except Exception as e:
            logger.error(f'Failed to get loop config: {e}')
            raise
