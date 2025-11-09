output "api_base_url" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}

output "table_name" {
  value = aws_dynamodb_table.quotes.name
}
