variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, prod."
  }
}

variable "bedrock_model_id" {
  description = "Bedrock model ID"
  type        = string
  default     = "amazon.nova-micro-v1:0"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 10
}

variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit"
  type        = number
  default     = 5
}

variable "use_custom_domain" {
  description = "Attach a custom domain to CloudFront"
  type        = bool
  default     = false
}

variable "root_domain" {
  description = "Apex domain name, e.g. mydomain.com"
  type        = string
  default     = ""
}

variable "openrouter_api_key" {
  description = "OpenRouter API key (passed to Lambda)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "use_openrouter" {
  description = "When true, Lambda uses OpenRouter. When false, Lambda uses OpenCode Go."
  type        = bool
  default     = false
}

variable "use_evaluation_openrouter" {
  description = "When true, evaluation uses OpenRouter. When false, evaluation uses OpenCode Go."
  type        = bool
  default     = false
}

variable "opencode_go_api_key" {
  description = "OpenCode Go API key (passed to Lambda)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "opencode_go_model" {
  description = "OpenCode Go model ID"
  type        = string
  default     = "deepseek-v4-flash"
}

variable "opencode_go_api_style" {
  description = "OpenCode Go API style: auto, openai, or anthropic"
  type        = string
  default     = "auto"
  validation {
    condition     = contains(["auto", "openai", "anthropic"], var.opencode_go_api_style)
    error_message = "OpenCode Go API style must be one of: auto, openai, anthropic."
  }
}

variable "opencode_go_disable_thinking" {
  description = "Disable OpenCode Go thinking mode on OpenAI-compatible requests"
  type        = bool
  default     = true
}

variable "default_model_name" {
  description = "Default OpenRouter chat model name"
  type        = string
  default     = "google/gemini-2.5-flash-lite"
}

variable "evaluation_model_name" {
  description = "OpenRouter model that will be used for evaluation of responses"
  type        = string
  default     = "google/gemini-2.5-flash-lite"
}

variable "evaluation_provider_order_enabled" {
  description = "Enable OpenRouter provider ordering for the evaluator"
  type        = bool
  default     = false
}

variable "evaluation_provider_order" {
  description = "Comma-separated provider slugs in priority order for the evaluator"
  type        = string
  default     = ""
}

variable "mailjet_api_key" {
  description = "Mailjet API key"
  type        = string
}

variable "mailjet_api_secret" {
  description = "Mailjet API secret"
  type        = string
}

variable "mailjet_from_email" {
  description = "Mailjet from email address that will be send"
  type        = string
}

variable "mailjet_to_email" {
  description = "Mailjet to email address that will be send"
  type        = string
}

variable "chat_endpoint_api_key" {
  description = "API key for chat endpoint, passed to Lambda for validation"
  type        = string
}

variable "check_chat_api_key" {
  description = "When true, Lambda will validate incoming chat requests against the chat API key"
  type        = bool
  default     = false
}
