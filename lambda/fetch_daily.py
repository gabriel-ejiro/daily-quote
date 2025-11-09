import json, os, urllib.request, datetime, time
import boto3

DDB_TABLE = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DDB_TABLE)

def _fetch_quote():
    # Public API, no key required
    url = "https://api.quotable.io/random"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # Normalize fields
    return {
        "text": data.get("content"),
        "author": data.get("author"),
        "source": "quotable.io",
    }

def handler(event, context):
    today = datetime.datetime.utcnow().date().isoformat()  # YYYY-MM-DD (UTC)
    q = _fetch_quote()
    item = {
        "day": today,
        "text": q["text"],
        "author": q["author"],
        "source": q["source"],
        "updatedAt": int(time.time())
    }
    table.put_item(Item=item)
    return {"statusCode": 200, "body": json.dumps({"saved": today})}
