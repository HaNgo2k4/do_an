from agents.tool import youtube_search_tool,identify_song_tool
from backend.config import YOUTUBE_API_KEY
def get_tools(user_id):
    return [
        youtube_search_tool(youtube_api_key=YOUTUBE_API_KEY),
        identify_song_tool(user_id=user_id)
    ]
