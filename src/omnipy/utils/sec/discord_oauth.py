''' discord_oauth.py  The purpose of this program is to host the Quart app for Discord OAuth 2.0.
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
from datetime import datetime, timedelta
from py_vyrtuous.utils.inc.setup_logging import logger
from quart import Quart, request, redirect

import aiohttp
import asyncio
import logging

discord_app = Quart(__name__)

class DiscordOAuth:
    def __init__(self, config):
        self.config = config
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.token_event = asyncio.Event()
        self.client_id = self.config['api_keys']['Discord']['client_id']
        self.client_secret = self.config['api_keys']['Discord']['client_secret']
        self.redirect_uri = self.config['api_keys']['Discord']['redirect_uri']

    def get_authorization_url(self):
        return (
            f'https://discord.com/api/oauth2/authorize'
            f'?client_id={self.client_id}'
            f'&redirect_uri={self.redirect_uri}'
            f'&response_type=code'
            f'&permissions=2141842833124'
            f'&integration_type=0'
            f'&scope=bot'
        )

    async def exchange_token(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'scope': 'identify email'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://discord.com/api/oauth2/token', data=data, headers=headers) as resp:
                token_data = await resp.json()
        if 'access_token' not in token_data:
            logger.error(f'Discord token exchange failed: {token_data}')
            return False
        self.access_token = token_data['access_token']
        self.refresh_token = token_data.get('refresh_token')
        self.expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        self.token_event.set()
        return True

    async def wait_for_token(self):
        await self.token_event.wait()

def setup_discord_routes(app, discord_oauth):
    @app.route('/discord_authorize')
    async def discord_authorize():
        auth_url = discord_oauth.get_authorization_url()
        logger.debug(f'Redirecting to Discord OAuth URL: {auth_url}')
        return redirect(auth_url)

    @app.route('/discord_callback')
    async def discord_callback():
        code = request.args.get('code')
        if not code:
            logger.error('Missing Discord authorization code in callback.')
            return 'Missing authorization code', 400
        logger.debug(f'Discord authorization code received: {code}')
        success = await discord_oauth.exchange_token(code)
        if not success:
            return 'Discord token exchange failed.', 400
        return 'Discord authentication successful! You can close this window.'
