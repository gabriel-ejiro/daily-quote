import os
import json
import boto3
import datetime
import random
import ssl
import urllib.request
from urllib.error import URLError, HTTPError

dynamodb = boto3.resource("dynamodb")

TABLE_ENV = "TABLE_NAME"
QUOTABLE_URL = "https://api.quotable.io/random"

# Local fallback quotes (for when online fails)
FALLBACK_QUOTES = [
    {
        "quote": "Success is the sum of small efforts, repeated day in and day out.",
        "author": "Robert Collier",
    },
    {
        "quote": "Stay hungry, stay foolish.",
        "author": "Steve Jobs",
    },
    {
        "quote": "It always seems impossible until it’s done.",
        "author": "Nelson Mandela",
    },
    {
        "quote": "Discipline is choosing between what you want now and what you want most.",
        "author": "Unknown",
    },
    {
        "quote": "The future depends on what you do today.",
        "author": "Mahatma Gandhi",
    },
]


def fetch_quote_online():
    """
    Try to fetch a quote from the public API.
    Returns (quote, author) or (None, None) on failure.
    """
    try:
        # normal verified HTTPS call
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(QUOTABLE_URL, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("content"), data.get("author")
    except (HTTPError, URLError, ssl.SSLError) as e:
        # Log but don't crash the Lambda
        print("Online quote fetch failed:", repr(e))
        return None, None
    except Exception as e:
        print("Unexpected error during online fetch:", repr(e))
        return None, None


def fetch_quote_fallback():
    """Pick a random local quote."""
    if not FALLBACK_QUOTES:
        return None, None
    q = random.choice(FALLBACK_QUOTES)
    return q.get("quote"), q.get("author", "Unknown")


def handler(event, context):
    table_name = os.environ.get(TABLE_ENV)
    if not table_name:
        msg = f"{TABLE_ENV} env var missing"
        print(msg)
        return {"ok": False, "error": msg}

    table = dynamodb.Table(table_name)
    day = datetime.datetime.utcnow().date().isoformat()

    # 1) Try online first
    quote, author = fetch_quote_online()

    # 2) If online fails, fall back to offline list
    if not quote:
        print("Falling back to local quote list")
        quote, author = fetch_quote_fallback()

    if not quote:
        # Even fallback failed (no quotes configured)
        return {"ok": False, "day": day, "error": "No quote available (online + fallback failed)"}

    try:
        table.put_item(
            Item={
                "day": day,
                "quote": quote,
                "author": author or "Unknown",
            }
        )
        return {"ok": True, "day": day, "source": "online" if "Falling back" not in quote else "fallback"}
    except Exception as e:
        print("ERROR in fetch_daily while writing to DynamoDB:", repr(e))
        return {"ok": False, "day": day, "error": str(e)}
