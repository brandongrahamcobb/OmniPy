**py\_vyrtuous** is a multipurpose Discord bot in Python. It brings together:

* Chemistry tools (structure rendering, comparison, logP prediction)
* Scripture lookup (Bible & Quran)
* Moderation (message wiping)
* Tagging & routine posts
* PDF-based research management

## Features

Chemistry
• `d <compound1> <compound2>` —  Render a molecule or peptide by name and/or get side-by-side comparison
• In-bot help: `help d`
• `logp <name>` — Predict octanol–water partition coefficient
• `smiles <name>` — Return the SMILES string for a given molecule

Scripture
• `script ESV <book>.<chapter>.<verse>`
• `script quran <sura>.<ayah>`

Moderation & Tagging
• `wipe <count>` — Bulk-delete last `<count>` messages
• In-bot help: `help wipe`
• `tag add <key> <value>` / `tag <key>` / `tag list`
• In-bot help: `help tag`

PDF Manager
• A suite of `pdf` subcommands to upload, search, annotate, and retrieve PDFs
• In-bot help: `help uploadpdf`

## Installation

Prerequisites:
• Python 3.13+ (`python3 --version`)
• pip (`pip --version`)
• PostgreSQL (`psql --version`)

1. Clone the repo

```bash
git clone https://github.com/brandongrahamcobb/Vyrtuous.git
cd lucy
```

2. Create & activate a virtual environment

```bash
python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Inside the venv, install Poetry

```bash
pip install poetry
```

4. Build the wheel

```bash
poetry build --format wheel
pip install dist/omnipy-2.8.9-py3-none-any.whl
```

5. Create the PostgreSQL database

```bash
createdb omnipy
```

6. Run the SQL setup script

```bash
psql omnipy < script.sql
```

## Configuration

On first run, py\_vyrtuous will prompt you to enter and confirm:
• Discord bot token

```txt
How many api keys do you want to make?
1
"Discord"
Enter api_key
```

• Discord command prefix
• Discord character limit (regular = 2000, nitro = 4000)
• Discord owner ID
• Discord test guild

Your settings are saved to:

```txt
<installation_directory>/.config/config.yml
```

Subsequent launches read from this file—no environment variables needed.

## Running

With your venv active, simply run:

```bash
omnipy
```

The bot will load or create its config, connect to Discord, and register commands.

## Commands

Replace `<prefix>` with your configured prefix (default `!`).

Chemistry
• `<prefix>draw <name>`
• `<prefix>d <compound1> <compound2>`
• `<prefix>logp <name>`

Scripture
• `<prefix>script bible <book> <chapter>:<verse>`
• `<prefix>script quran <sura>:<ayah>`

Moderation & Tagging
• `<prefix>wipe <count>`
• `<prefix>tag set <key> <value>`
• `<prefix>tag get <key>`
• `<prefix>tag list>`

PDF Manager
• `<prefix>listpdfs ...`
• `<prefix>uploadpdf ...`
• See `<prefix>help uploadpdf` for full subcommand list

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request

## License

Distributed under GPL-3.0-or-later. See LICENSE for details.
