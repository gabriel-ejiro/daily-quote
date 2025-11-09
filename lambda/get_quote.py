import json, os, urllib.request, datetime, time
import boto3
from boto3.dynamodb.conditions import Key

DDB_TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DDB_TABLE)

def _fetch_quote():
    url = "https://api.quotable.io/random"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {
        "text": data.get("content"),
        "author": data.get("author"),
        "source": "quotable.io",
    }

def _save(day, q):
    table.put_item(Item={
        "day": day,
        "text": q["text"],
        "author": q["author"],
        "source": q["source"],
        "updatedAt": int(time.time())
    })

def handler(event, context):
    today = datetime.datetime.utcnow().date().isoformat()
    # Try to read today’s item
    resp = table.get_item(Key={"day": today})
    item = resp.get("Item")
    if not item:
        # First visitor today: fetch once and save
        q = _fetch_quote()
        _save(today, q)
        item = {"day": today, **q}

    body = {
        "day": item["day"],
        "text": item["text"],
        "author": item.get("author"),
        "source": item.get("source", "unknown")
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json",
                    "Cache-Control": "no-store"},
        "body": json.dumps(body)
    }
