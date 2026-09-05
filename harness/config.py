import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

load_dotenv(override=True)

WORKDIR = Path.cwd()
os.system('chcp 65001')
TEXT_ENCODING = 'utf-8'

DEFAULT_MAX_TOKENS = 8000
MODEL_ID = os.environ["MODEL_ID"]

client = OpenAI(
  api_key=os.environ["OPENAI_API_KEY"],
  base_url=os.environ["OPENAI_BASE_URL"],
)