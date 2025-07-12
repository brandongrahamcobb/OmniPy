''' backup.py  The purpose of this program is to backup the PostgreSQL database.
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

import datetime
import os
import subprocess

def perform_backup(db_user: str, db_name: str, db_host: str, backup_dir: str) -> str:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
    dump_command = [
        'pg_dump',
        '-U', db_user,
        '-h', db_host,
        '-d', db_name,
        '-F', 'p',
        '-f', backup_file,
    ]
    result = subprocess.run(
        dump_command,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f'Backup failed: {result.stderr}')
    return backup_file

def setup_backup_directory(backup_dir: str) -> str:
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

