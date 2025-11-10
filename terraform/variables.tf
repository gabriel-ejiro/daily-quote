variable "project" {
  type    = string
  default = "daily-quote"
}

variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "schedule_utc_hour" {
  type    = number
  default = 8
}

variable "schedule_utc_minute" {
  type    = number
  default = 0
}
