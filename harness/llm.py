from config import client
from tools.schema import TOOLS
def call_llm(system_prompt: str, messages: list, max_tokens: int, model: str):
  return client.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": system_prompt},
      *messages,
    ],
    tools=TOOLS,
    max_tokens=max_tokens,
  )