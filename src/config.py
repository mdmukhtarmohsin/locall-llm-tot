import os

class Config:
    # Ollama model for generation
    OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME')
    # Ollama model for prompt optimization
    OLLAMA_OPTIMIZER_MODEL_NAME = os.getenv('OLLAMA_OPTIMIZER_MODEL_NAME', os.getenv('OLLAMA_MODEL_NAME'))