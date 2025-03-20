# src/agents/base_agent.py

from pydantic import BaseModel
import logging
import time
from groq import Groq

class AgentConfig(BaseModel):
    api_key: str
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_retries: int = 3
    max_tokens: int = 512
    timeout: int = 30

class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = Groq(api_key=config.api_key, timeout=config.timeout)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _call_llm(self, prompt: str) -> str:
        for attempt in range(self.config.max_retries):
            try:
                completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.config.model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                self.logger.error(f"Attempt {attempt+1} failed: {str(e)}")
                time.sleep(2 ** attempt)
        raise RuntimeError("Max retries exceeded")
