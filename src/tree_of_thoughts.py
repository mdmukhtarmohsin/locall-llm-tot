from typing import List
from config import Config
import ollama

def generate_reasoning_paths(
    prompt: str,
    num_paths: int = 5,
) -> List[str]:
    """Generate multiple reasoning paths via Ollama model."""
    results = []
    model_name = 'gemma3:4b-it-qat'
    if not model_name:
        raise ValueError("OLLAMA_MODEL_NAME not set in environment.")
    for _ in range(num_paths):
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
            )
            # Extract content
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                text = response.message.content.strip()
            elif isinstance(response, dict) and 'message' in response and 'content' in response['message']:
                text = response['message']['content'].strip()
            else:
                text = str(response).strip()
        except Exception as e:
            raise RuntimeError(f"Ollama generation error: {e}")
        # Strip prompt echo if present
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        results.append(text)
    return results