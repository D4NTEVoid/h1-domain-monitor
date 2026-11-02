# H1 Domain Monitor

A lightweight Python utility for monitoring HackerOne's public domain dataset, filtering domains by keyword, identifying newly discovered entries, and delivering notifications through Telegram.

## Features

- Fetches the latest public domain list from HackerOne's community-maintained dataset.
- Filters domains using case-insensitive keyword matching.
- Detects newly added matching domains by comparing against previously stored results.
- Maintains an updated local domain list for each target.
- Sends Telegram notifications when new matching domains are discovered.
- Supports configurable storage directories.
- Includes request timeouts, input validation, and error handling.

## Requirements

- Python 3.9+
- Requests

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/h1-domain-monitor.git
cd h1-domain-monitor
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Telegram notifications are optional.

Configure your Telegram bot credentials through environment variables:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
```

Configure the directory used to store target results:

```bash
export TARGETS_DIR="$PWD/targets"
```

If `TARGETS_DIR` is not configured, the utility defaults to `/targets`.

## Usage

```bash
python h1domains.py <filter_word> <target_name>
```

Example:

```bash
python h1domains.py example example-target
```

This command:

1. Fetches the latest domain dataset.
2. Filters entries containing `example`.
3. Compares matching entries with the previously saved list.
4. Saves the updated results.
5. Sends notifications for newly discovered entries, if Telegram is configured.

## Output Structure

```text
targets/
└── example-target/
    └── domains.txt
```

Each target maintains its own domain list.

## Notifications

When new matching domains are discovered, the utility sends them to the configured Telegram chat.

If Telegram credentials are not configured, domain collection and local storage continue without notifications.

## Data Source

Domain data is retrieved from:

[HackerOne Domains Dataset](https://github.com/zricethezav/h1domains)

This project is an independent utility and is not officially affiliated with or endorsed by HackerOne.

## Responsible Use

This tool is intended for domain discovery and reconnaissance in authorized security research.

Identifying a domain in a public dataset does not establish permission to test it. Always verify the applicable bug bounty program's scope and rules before performing security testing.

## License

MIT License (recommended, subject to confirmation that you have the rights to license your contributions and comply with upstream attribution requirements).
