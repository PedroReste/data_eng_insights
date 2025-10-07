"""
en_02_api_key_reader.py
Utilities to read API keys for OpenRouter (and similar providers).
This module is intentionally small and robust: it attempts to read an API key
from environment variables or from simple text files that commonly store keys.

Provides:
- read_api_key_from_file(path): flexible parsing for simple formats
- get_api_key_from_env(): tries multiple env var names
- get_api_key(...): convenience function (file first, then env)

Usage:
    from en_02_api_key_reader import get_api_key
    key = get_api_key(file_path="openrouter_key.txt")
"""

import os
import re
from typing import Optional


def read_api_key_from_file(path: str) -> Optional[str]:
    """
    Read API key from a small text file. Accepts several common formats:
      - raw key: ABCDEF...
      - KEY=ABCDEF...
      - OPENROUTER_API_KEY=ABCDEF...
      - openrouter:ABCDEF
    Returns the key string or None if not found.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        return None

    # Try common patterns
    # 1) plain key (single line, no '=')
    if "\n" not in text and "=" not in text and ":" not in text:
        return text.strip()

    # 2) KEY= or OPENROUTER_API_KEY= or similar
    m = re.search(r"OPEN[_\- ]?ROUTER[_\- ]?API[_\- ]?KEY\s*=\s*([A-Za-z0-9\-\._]+)", text, re.I)
    if m:
        return m.group(1).strip()

    m = re.search(r"KEY\s*=\s*([A-Za-z0-9\-\._]+)", text, re.I)
    if m:
        return m.group(1).strip()

    # 3) openrouter:KEY or OPENROUTER:KEY
    m = re.search(r"openrouter[:\s]*([A-Za-z0-9\-\._]+)", text, re.I)
    if m:
        return m.group(1).strip()

    # 4) fallback: pick first token-looking substring
    tokens = re.findall(r"([A-Za-z0-9\-\._]{20,200})", text)
    if tokens:
        return tokens[0].strip()

    return None


def get_api_key_from_env() -> Optional[str]:
    """
    Tries commonly used environment variables for OpenRouter or similar providers.
    """
    for name in ("OPENROUTER_API_KEY", "OPEN_ROUTER_API_KEY", "OPENROUTER_KEY", "OPENROUTER"):
        val = os.environ.get(name)
        if val:
            return val.strip()
    return None


def get_api_key(file_path: Optional[str] = None) -> Optional[str]:
    """
    Convenience: try file_path first (if given), then env vars.
    """
    if file_path:
        k = read_api_key_from_file(file_path)
        if k:
            return k
    return get_api_key_from_env()


# If this file is executed directly, print a quick tip.
if __name__ == "__main__":
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else None
    key = get_api_key(fp) if fp else get_api_key_from_env()
    print("Detected key:" if key else "No key found.", key)