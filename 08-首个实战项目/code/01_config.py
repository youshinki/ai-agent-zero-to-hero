from dotenv import load_dotenv
import os

load_dotenv()

# 模型配置
MODEL_API_KEY = os.getenv("API_KEY")
MODEL_BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = "deepseek-chat"

# Agent基础参数
MAX_THOUGHT_STEPS = 3
