from dotenv import load_dotenv
import os
from crewai import LLM

load_dotenv()

def get_llm():
    return LLM(
        model=os.getenv("MODEL_NAME", "deepseek-chat"),
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )
