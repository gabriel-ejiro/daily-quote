import os
import json
import boto3
import datetime

dynamodb = boto3.resource("dynamodb")


def _json_resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }


def _html_resp(day, quote, author):
    html = f"""
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Daily Quote</title>
      <style>
        body {{
          font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
          background: linear-gradient(135deg, #F0F4F8, #D9E2EC);
          margin: 0;
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }}
        .card {{
          background: #ffffff;
          max-width: 650px;
          width: 90%;
          padding: 32px 36px;
          border-radius: 16px;
          box-shadow: 0 12px 30px rgba(15, 23, 42, 0.25);
          text-align: center;
          animation: fadein 0.5s ease-out;
        }}
        .quote {{
          font-size: 26px;
          line-height: 1.5;
          color: #111827;
          margin-bottom: 20px;
        }}
        .quote::before,
        .quote::after {{
          font-size: 32px;
          color: #9CA3AF;
        }}
        .quote::before {{
          content: "“";
          margin-right: 4px;
        }}
        .quote::after {{
          content: "”";
          margin-left: 4px;
        }}
        .author {{
          font-size: 18px;
          color: #4B5563;
          margin-bottom: 12px;
        }}
        .date {{
          font-size: 13px;
          color: #9CA3AF;
        }}
        @keyframes fadein {{
          from {{ opacity: 0; transform: translateY(10px); }}
          to   {{ opacity: 1; transform: translateY(0);   }}
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="quote">{quote}</div>
        <div class="author">— {author}</div>
        <div class="date">{day}</div>
      </div>
    </body>
    </html>
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-cache"
        },
        "body": html
    }


def _wants_html(event):
    """
    Decide whether to return HTML or JSON.

    - If query param ?format=json → force JSON
    - If query param ?format=html → force HTML
    - Else, look at Accept header:
      - If it contains application/json → JSON
      - If it contains text/html and not application/json → HTML
    """
    # Query param override
    qs = event.get("queryStringParameters") or {}
    fmt = (qs.get("format") or "").lower()
    if fmt == "json":
        return False
    if fmt == "html":
        return True

    # Accept header
    headers = event.get("headers") or {}
    accept = ""
    for k, v in headers.items():
        if k.lower() == "accept":
            accept = v or ""
            break

    accept = accept.lower()
    if "application/json" in accept:
        return False
    if "text/html" in accept:
        return True

    # Default: JSON (safer for programmatic callers)
    return False


def handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        return _json_resp(500, {"message": "TABLE_NAME env var is missing on Lambda"})

    table = dynamodb.Table(table_name)
    today = datetime.datetime.utcnow().date().isoformat()

    try:
        result = table.get_item(Key={"day": today})
        item = result.get("Item")

        if not item:
            msg = "No quote stored for today yet. Try again in a minute."
            if _wants_html(event):
                # Simple HTML error page if someone browses directly
                return _html_resp(today, msg, "System")
            return _json_resp(404, {"message": msg})

        day = item.get("day", today)
        quote = item.get("quote") or "No quote text found."
        author = item.get("author", "Unknown")

        # Decide response format based on Accept / query param
        if _wants_html(event):
            return _html_resp(day, quote, author)

        return _json_resp(
            200,
            {
                "day": day,
                "quote": quote,
                "author": author,
            },
        )

    except Exception as e:
        print("ERROR in get_quote:", repr(e))
        if _wants_html(event):
            return _html_resp(today, "Error reading quote", "System")
        return _json_resp(500, {"message": "Error reading quote", "detail": str(e)})
