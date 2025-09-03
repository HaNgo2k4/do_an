from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core import tools
from agents.tool import youtube_search_tool
from app.config import YOUTUBE_API_KEY
def get_tools():
    return [youtube_search_tool(YOUTUBE_API_KEY)]



