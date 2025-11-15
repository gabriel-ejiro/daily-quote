import os
import json
import boto3
import datetime

dynamodb = boto3.resource("dynamodb")


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
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        # Env var misconfigured
        return _resp(500, {"message": "TABLE_NAME env var is missing on Lambda"})

    table = dynamodb.Table(table_name)
    today = datetime.datetime.utcnow().date().isoformat()

    try:
        result = table.get_item(Key={"day": today})
        item = result.get("Item")

        if not item:
            # No entry for today yet
            return _resp(404, {"message": "No quote stored for today yet. Try again in a minute."})

        return _resp(200, {
            "day": item.get("day", today),
            "quote": item.get("quote"),
            "author": item.get("author", "Unknown")
        })
    except Exception as e:
        print("ERROR in get_quote:", repr(e))
        return _resp(500, {"message": "Error reading quote", "detail": str(e)})
