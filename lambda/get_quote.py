import os, json, boto3, datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def handler(event, context):
    # use UTC date, e.g. "2025-11-14"
    today = datetime.datetime.utcnow().date().isoformat()

    try:
        r = table.get_item(Key={"day": today})
        item = r.get("Item")
        if not item:
            # Graceful fallback for first day / not yet fetched
            return _resp(404, {"message": "No quote stored for today yet. Try again in a minute."})
        # Expecting item like {"day":"YYYY-MM-DD","quote":"...","author":"..."}
        return _resp(200, {"day": item["day"], "quote": item.get("quote"), "author": item.get("author")})
    except Exception as e:
        # Never let exceptions bubble to API Gateway
        return _resp(500, {"message": "Error reading quote", "detail": str(e)})
