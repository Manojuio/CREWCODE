import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Models
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-pro"
OPENROUTER_MODEL = "gpt-oss-120b"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Agent routing – each stage can use a different provider
AGENT_MODEL_MAP = {
    "inspector":     ("ollama", "qwen2.5-coder:1.5b"),
    "test_engineer": ("ollama", "qwen2.5-coder:1.5b"),
    "debugger":      ("ollama", "qwen2.5-coder:1.5b"),
    "reviewer":      ("ollama", "qwen2.5-coder:1.5b"),
}
def get_model_config(role: str):
    if role not in AGENT_MODEL_MAP:
        return ("ollama", OLLAMA_MODEL)
    return AGENT_MODEL_MAP[role]

# Limits
MAX_FILE_READ_CHARS = 10000
TOOL_TIMEOUT_SECONDS = 30
# At the bottom of settings.py
llm_call_counter = 0

def increment_llm_calls():
    global llm_call_counter
    llm_call_counter += 1

def get_llm_call_count():
    return llm_call_counter

def reset_llm_calls():
    global llm_call_counter
    llm_call_counter = 0