"""Configuration for the LLM Council.

Supports three provider modes:
1. 'openrouter': All models use OpenRouter API (default, backward compatible)
2. 'ollama': All models use local Ollama server  
3. 'mixed': Prefix each model with provider (e.g., 'ollama:llama2', 'openrouter:google/gemini-pro')
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider configuration
# Valid values: 'openrouter', 'ollama', 'mixed'
# Default: 'openrouter' for backward compatibility
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")

# Validate LLM_PROVIDER
VALID_PROVIDERS = ["openrouter", "ollama", "mixed"]
if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(
        f"Invalid LLM_PROVIDER '{LLM_PROVIDER}'. Must be one of {VALID_PROVIDERS}"
    )

# OpenRouter API key (required for 'openrouter' and 'mixed' modes)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validate API key for openrouter modes
if LLM_PROVIDER in ["openrouter", "mixed"] and not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set. "
        "Please create a .env file with your API key: OPENROUTER_API_KEY=sk-or-v1-..."
    )

# Ollama base URL (required for 'ollama' and 'mixed' modes)
# Default: http://localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Council members - adapts based on LLM_PROVIDER
# Examples:
# - openrouter mode: ["openai/gpt-5.1", "google/gemini-3-pro-preview"]
# - ollama mode: ["llama2", "mistral", "phi"]
# - mixed mode: ["ollama:llama2", "openrouter:google/gemini-pro"]
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
