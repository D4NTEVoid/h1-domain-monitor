
#!/usr/bin/env python3
"""
H1 Domain Monitor
Filter HackerOne public domains and detect newly added entries.
"""

import os
import re
import sys
from pathlib import Path

import requests

GITHUB_URL = (
    "https://raw.githubusercontent.com/"
    "zricethezav/h1domains/master/domains.txt"
)

TARGETS_DIR = Path(os.getenv("TARGETS_DIR", "/targets"))
REQUEST_TIMEOUT = (5, 30)
TELEGRAM_MESSAGE_LIMIT = 4000


def fetch_domains(filter_word):
    """Fetch and filter domains from the upstream HackerOne list."""
    try:
        response = requests.get(
            GITHUB_URL,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch domains: {exc}") from exc

    domains = {
        line.strip()
        for line in response.text.splitlines()
        if line.strip()
    }

    keyword = filter_word.casefold()

    return {
        domain for domain in domains
        if keyword in domain.casefold()
    }


def get_target_file(target_name):
    """Resolve a target path and prevent directory traversal."""
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", target_name):
        raise ValueError("Invalid target name.")

    root = TARGETS_DIR.resolve()
    target_dir = (root / target_name).resolve()

    if target_dir.parent != root:
        raise ValueError("Target directory escapes the targets directory.")

    target_file = target_dir / "domains.txt"

    if target_file.exists() and target_file.resolve().parent != target_dir:
        raise ValueError("Target file resolves outside its target directory.")

    return target_file


def load_existing(path):
    """Load previously recorded domains."""
    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8") as file:
        return {
            line.strip()
            for line in file
            if line.strip()
        }


def save_domains(domains, path):
    """Save the current filtered domain list."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for domain in sorted(domains):
            file.write(f"{domain}\n")


def send_telegram_message(new_domains, filter_word):
    """Send newly discovered domains through Telegram."""
    if not new_domains:
        print("[+] No new domains found.")
        return

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[!] Telegram notification skipped: credentials not configured.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    header = f"New domains found for '{filter_word}':\n"
    current_message = header

    try:
        with requests.Session() as session:
            for domain in sorted(new_domains):
                if len(current_message) + len(domain) + 1 > TELEGRAM_MESSAGE_LIMIT:
                    session.post(
                        url,
                        json={"chat_id": chat_id, "text": current_message},
                        timeout=REQUEST_TIMEOUT
                    ).raise_for_status()

                    current_message = header

                current_message += domain + "\n"

            if current_message != header:
                session.post(
                    url,
                    json={"chat_id": chat_id, "text": current_message},
                    timeout=REQUEST_TIMEOUT
                ).raise_for_status()

        print("[+] Telegram notifications sent.")

    except requests.RequestException as exc:
        print(f"[!] Telegram notification failed: {exc}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <filter_word> <target_name>")
        sys.exit(1)

    filter_word, target_name = sys.argv[1:3]

    if not filter_word.strip():
        print("[!] Filter keyword cannot be empty.")
        sys.exit(1)

    try:
        target_file = get_target_file(target_name)

        print(f"[*] Filtering domains for '{filter_word}'...")

        filtered_domains = fetch_domains(filter_word)
        existing_domains = load_existing(target_file)

        new_domains = filtered_domains - existing_domains

        save_domains(filtered_domains, target_file)

        print(f"[+] Matching domains: {len(filtered_domains)}")
        print(f"[+] Newly discovered: {len(new_domains)}")
        print(f"[+] Results saved to: {target_file}")

        send_telegram_message(new_domains, filter_word)

    except (RuntimeError, ValueError, OSError) as exc:
        print(f"[!] Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
