import logging
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq
import groq as groq_lib

# ─── Initialization ──────────────────────────────────────────
load_dotenv()
logger = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────
DEFAULT_MODEL         = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
DEFAULT_PROVIDER      = os.getenv("LLM_PROVIDER", "groq").lower()
MAX_RETRIES           = int(os.getenv("LLM_MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF", "1.5"))

# Only retry on transient network/rate errors
RETRYABLE_ERRORS = (
    groq_lib.APIConnectionError,
    groq_lib.APITimeoutError,
    groq_lib.RateLimitError,
    groq_lib.InternalServerError,
)


class LLMError(Exception):
    """Custom exception for LLM-related failures."""
    pass


class BaseLLMClient:
    def generate(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 300,
        temperature: float = 0.4,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        raise NotImplementedError


class GroqClient(BaseLLMClient):
    def __init__(self, api_key: Optional[str] = None):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))

    def generate(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 300,
        temperature: float = 0.4,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        logger.debug(f"Sending request to Groq (model: {model})")
        response = self.client.chat.completions.create(**payload)

        # ✅ Added: Token Tracking
        usage = response.usage
        if usage:
            logger.info(
                f"[Token Usage] Prompt: {usage.prompt_tokens} | "
                f"Completion: {usage.completion_tokens} | "
                f"Total: {usage.total_tokens}"
            )

        # ✅ Added: Response Validation
        content = response.choices[0].message.content
        if not content or not content.strip():
            logger.error("LLM returned an empty response.")
            raise LLMError("LLM returned an empty response")

        return content.strip()


def get_llm_client(provider: str = DEFAULT_PROVIDER) -> BaseLLMClient:
    provider = provider.lower()
    
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMError("GROQ_API_KEY is not set in environment or .env file")
        return GroqClient(api_key=api_key)
        
    # ✅ Fixed: Removed misleading provider list. Fail clearly.
    raise ValueError(f"Unsupported provider: '{provider}'. Only 'groq' is currently supported.")

def build_messages_with_history(
    user_message : str,
    chat_history : list=None,
    income       : float = 0,
    savings_rate : float = 0,
) -> list:
    if chat_history is None:
        chat_history = []
    """Builds message list with conversation history for LLM."""
    
    system_prompt = (
        f"You are a helpful financial advisor for young Indians. "
        f"User income: Rs.{income}/month. "
        f"Savings rate: {savings_rate}%. "
        f"Give short, practical advice in simple English."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Add chat history
    for msg in chat_history:
        messages.append({
            "role"   : msg["role"],
            "content": msg["content"],
        })

    # Add current message
    messages.append({
        "role"   : "user",
        "content": user_message,
    })

    return messages

def generate_with_retry(
    *,
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 300,
    temperature: float = 0.4,
    tools: Optional[List[Dict[str, Any]]] = None,
    retries: int = MAX_RETRIES,
) -> str:
    client = get_llm_client(provider)
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            return client.generate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=tools,
            )
        
        # ✅ Added: Proper exception handling for Unrecoverable errors
        except (groq_lib.AuthenticationError, groq_lib.BadRequestError) as exc:
            logger.error(f"Non-retryable error ({type(exc).__name__}): {exc}")
            raise LLMError(f"Non-retryable error — will not retry: {exc}") from exc
            
        # Transient errors
        except RETRYABLE_ERRORS as exc:
            last_error = exc
            if attempt == retries:
                break
            wait = RETRY_BACKOFF_SECONDS * attempt
            logger.warning(f"Attempt {attempt}/{retries} failed ({exc}). Retrying in {wait}s...")
            time.sleep(wait)

    logger.error(f"LLM request failed entirely after {retries} attempts.")
    raise LLMError(f"LLM request failed after {retries} attempts: {last_error}")


def get_advice(
    user_message: str,
    income: float = 0.0,
    savings_rate: float = 0.0,
    provider: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_MODEL,
) -> str:
    """Sends user message to configured LLM. Returns friendly financial advice."""
    
    # ✅ Added: Strict Input Validation
    if not user_message or not user_message.strip():
        raise ValueError("user_message cannot be empty")
    if income < 0:
        raise ValueError(f"income cannot be negative, got ₹{income}")

    messages = build_messages_with_history(
        user_message=user_message,
        income=income,
        savings_rate=savings_rate,  # For now, no history. Can be extended later.
    )
    return generate_with_retry(
        provider=provider,
        model=model,
        messages=messages,
        max_tokens=180,
        temperature=0.4,
    )


def get_quick_tip(category: str) -> str:
    """Returns a quick saving tip. No AI needed — instant response."""
    tips = {
        "Food":          "🍱 Cook at home 3 days a week and save ₹500-1000.",
        "Transport":     "🚌 Use public transport or carpool with friends.",
        "Entertainment": "🎮 Set a weekly fun budget and stick to it.",
        "Education":     "📚 Try free YouTube courses before paying for one.",
        "Others":        "📝 Track every rupee for 1 week to find money leaks.",
    }
    return tips.get(category, "💡 Small savings every day add up to big amounts!")


FINANCIAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_quick_tip",
            "description": "Return a quick savings tip for a spending category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["Food", "Transport", "Entertainment", "Education", "Others"],
                    }
                },
                "required": ["category"],
            },
        },
    }
]


if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    
    print("=== AI Advice Test ===\n")
    try:
        response = get_advice(
            "I keep spending too much on food. How do I control it?",
            income=8000,
            savings_rate=12,
        )
        print("\n🤖 AI Response:")
        print(response)
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")