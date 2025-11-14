import os, json, boto3, datetime, urllib.request

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

QUOTABLE_URL = "https://api.quotable.io/random"  # simple public API

def fetch_quote():
    # tiny stdlib HTTP call (no 'requests' dependency)
    with urllib.request.urlopen(QUOTABLE_URL, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        # quotable returns: {'_id', 'content', 'author', ...}
        return data.get("content"), data.get("author")

def handler(event, context):
    day = datetime.datetime.utcnow().date().isoformat()
    try:
        quote, author = fetch_quote()
        if not quote:
            raise RuntimeError("No quote returned from upstream")
        table.put_item(Item={"day": day, "quote": quote, "author": author or "Unknown"})
        return {"ok": True, "day": day}
    except Exception as e:
        # Log and surface a minimal message (EventBridge will just log it)
        print("fetch_daily error:", repr(e))
        return {"ok": False, "error": str(e), "day": day}
