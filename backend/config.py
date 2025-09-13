from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()  
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

ACRCLOUD_ACCESS_KEY = os.getenv("ACRCLOUD_ACCESS_KEY")
ACRCLOUD_ACCESS_SECRET = os.getenv("ACRCLOUD_ACCESS_SECRET")
ACRCLOUD_REQ_URL = os.getenv("ACRCLOUD_REQ_URL")
