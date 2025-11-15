import os
import json
import boto3
import datetime
import urllib.request

dynamodb = boto3.resource("dynamodb")

QUOTABLE_URL = "https://api.quotable.io/random"

def fetch_quote():
    with urllib.request.urlopen(QUOTABLE_URL, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        # quotable returns keys like "content" and "author"
        return data.get("content"), data.get("author")

def handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        print("TABLE_NAME env var missing")
        return {"ok": False, "error": "TABLE_NAME env var missing"}

    table = dynamodb.Table(table_name)
    day = datetime.datetime.utcnow().date().isoformat()

    try:
        quote, author = fetch_quote()
        if not quote:
            raise RuntimeError("No quote returned from upstream API")

        table.put_item(Item={
            "day": day,
            "quote": quote,
            "author": author or "Unknown"
        })

        return {"ok": True, "day": day}

    except Exception as e:
        print("ERROR in fetch_daily:", repr(e))
        return {"ok": False, "day": day, "error": str(e)}
