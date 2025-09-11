
from agents.llm_provider import get_llm
from agents.tools import get_tools
from agents.memory import get_user_memory
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

agent_cache = {}

SYSTEM_PROMPT = """
Hadiest – trợ lý ảo tâm sự và gợi ý nhạc Việt (tiếng Việt).
Quy tắc NGHE NHẠC:
1. Nếu metadata has_wav=True:
   - BẮT BUỘC gọi identify_song_tool trước để nhận diện bài hát từ microphone.
   - Nếu identify_song_tool có video_id → dùng kết quả đó.
   - Nếu identify_song_tool KHÔNG có video_id nhưng có title/artists → BẮT BUỘC gọi youtube_search_tool với query = "title + artists".
   - Chỉ sau khi có kết quả từ youtube_search_tool mới được trả lời người dùng.
2. Nếu metadata has_wav=False:
   - Khi người dùng nói: "mở nhạc", "nghe nhạc", "mở bài [tên]", "tìm bài [tên]" → BẮT BUỘC gọi youtube_search_tool với query đó.
   - Không bao giờ trả link trực tiếp, không được gọi function thủ công, luôn dùng tool.
3. Sau khi có kết quả tool:
   - Dựa trên kết qua của tool (nếu có) để trả lời người dùng tự nhiên, thân thiện, không cứng nhắc.
Khác:
- Có thể tâm sự, trò chuyện tự nhiên, thân thiện.
- Có thể gợi ý nhạc Việt theo tâm trạng người dùng.
"""

def get_or_create_agent(user_id: str, provider: str, llm_id: str):
    if user_id in agent_cache:
        return agent_cache[user_id]

    llm = get_llm(provider, llm_id)
    tools = get_tools(user_id=user_id)
    memory = get_user_memory(user_id)
    agent = create_react_agent(model=llm, tools=tools)
    agent_cache[user_id] = {
        "agent": agent,
        "memory": memory,
        "system_prompt": SystemMessage(content=SYSTEM_PROMPT)
    }
    return agent_cache[user_id]
