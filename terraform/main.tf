terraform {
  required_version = ">= 1.6.0"
  backend "s3" {
    bucket         = "REPLACE_WITH_TF_BUCKET"
    key            = "daily-quote/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "REPLACE_WITH_LOCK_TABLE"
    encrypt        = true
  }
  required_providers {
    aws     = { source = "hashicorp/aws", version = ">= 5.0" }
    archive = { source = "hashicorp/archive", version = ">= 2.4.0" }
  }
}


locals {
  name        = var.project
  table_name  = "${var.project}-table"
  fetch_name  = "${var.project}-fetch"
  api_name    = "${var.project}-api"
  get_name    = "${var.project}-get"
}

# -------------------------
# DynamoDB (on-demand)
# -------------------------
resource "aws_dynamodb_table" "quotes" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "day"

  attribute {
    name = "day"
    type = "S"
  }

  tags = { Project = local.name }
}

# -------------------------
# IAM role + policy for Lambdas
# -------------------------
data "aws_iam_policy_document" "assume" {
  statement {
    effect = "Allow"
    principals { type = "Service" identifiers = ["lambda.amazonaws.com"] }
    actions   = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${local.name}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.quotes.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "${local.name}-lambda-policy"
  policy = data.aws_iam_policy_document.lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# -------------------------
# Package Lambdas from ../lambda
# -------------------------
data "archive_file" "fetch_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/../lambda/.bundle_fetch.zip"
  excludes    = ["get_quote.py"] # only include fetch_daily.py
}

data "archive_file" "get_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/../lambda/.bundle_get.zip"
  excludes    = ["fetch_daily.py"] # only include get_quote.py
}

# -------------------------
# Lambda: fetch_daily
# -------------------------
resource "aws_lambda_function" "fetch" {
  function_name = local.fetch_name
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.11"
  handler       = "fetch_daily.handler"
  filename         = data.archive_file.fetch_zip.output_path
  source_code_hash = data.archive_file.fetch_zip.output_base64sha256
  timeout       = 10
  environment {
    variables = { TABLE_NAME = aws_dynamodb_table.quotes.name }
  }
}

# -------------------------
# Lambda: get_quote (HTTP)
# -------------------------
resource "aws_lambda_function" "get" {
  function_name = local.get_name
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.11"
  handler       = "get_quote.handler"
  filename         = data.archive_file.get_zip.output_path
  source_code_hash = data.archive_file.get_zip.output_base64sha256
  timeout       = 10
  environment {
    variables = { TABLE_NAME = aws_dynamodb_table.quotes.name }
  }
}

# -------------------------
# EventBridge schedule → fetch_daily
# -------------------------
# cron(Minutes Hours Day-of-month Month Day-of-week Year [optional])
# Example: 0 8 * * ? *  == 08:00 UTC daily
resource "aws_cloudwatch_event_rule" "daily" {
  name                = "${local.name}-daily"
  schedule_expression = "cron(${var.schedule_utc_minute} ${var.schedule_utc_hour} * * ? *)"
}

resource "aws_cloudwatch_event_target" "daily_to_lambda" {
  rule      = aws_cloudwatch_event_rule.daily.name
  target_id = "fetch"
  arn       = aws_lambda_function.fetch.arn
}

resource "aws_lambda_permission" "allow_events" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fetch.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily.arn
}

# -------------------------
# HTTP API (API Gateway v2) → get_quote
# -------------------------
resource "aws_apigatewayv2_api" "http" {
  name          = local.api_name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "get_integration" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.get.invoke_arn
  payload_format_version = "2.0"
  integration_method     = "POST"
}

resource "aws_apigatewayv2_route" "get_route" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "GET /quote"
  target    = "integrations/${aws_apigatewayv2_integration.get_integration.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# -------------------------
# Tags & outputs
# -------------------------
resource "aws_resourcegroups_group" "rg" {
  name = "${local.name}-rg"
  resource_query {
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [{ Key = "Project", Values = [local.name] }]
    })
  }
  tags = { Project = local.name }
}
