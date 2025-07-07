import os
from dotenv import load_dotenv
from typing import Optional, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI

class ModelParameters(TypedDict, total=False):
    selected_model: str
    temperature: float
    max_tokens: int
    gemini_token: Optional[str]
    embedding_model: Optional[str]
    tts_model: Optional[str]
    live_model: Optional[str]

load_dotenv()

def get_llm(parameters: ModelParameters) -> ChatGoogleGenerativeAI:
    """
    Get the Google Generative AI LLM instance with specified parameters.
    
    Args:
        parameters: Model parameters including model, temperature, and max_tokens.

    Returns:
        An instance of ChatGoogleGenerativeAI configured with the provided parameters.
    """
    model = parameters.get('selected_model')
    temperature = parameters.get('temperature', 0.0)
    max_tokens = parameters.get('max_tokens', None)

    print(f"Using model: {model}, temperature: {temperature}, max_tokens: {max_tokens}")
    print(f"Using API key: {parameters.get('gemini_token', None) or os.getenv('GOOGLE_API_KEY', None)}")

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=None,
        max_retries=2,
        api_key=parameters.get('gemini_token', None) or os.getenv('GOOGLE_API_KEY') or None
    )