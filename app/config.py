from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()  
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
