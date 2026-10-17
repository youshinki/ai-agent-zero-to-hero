from dotenv import load_dotenv
import os

load_dotenv()

# 大模型基础配置
MODEL_API_KEY = os.getenv("API_KEY")
MODEL_BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = "deepseek-chat"

# Agent运行参数
MAX_THOUGHT_STEPS = 3
