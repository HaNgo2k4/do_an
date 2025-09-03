
from agents.llm_provider import get_llm
from agents.tools import get_tools
from agents.memory import get_user_memory
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

agent_cache = {}

# SYSTEM_PROMPT = """Bạn là Hadiest - trợ lý ảo tâm sự và gợi ý nhạc Việt thân thiện. Chỉ nói tiếng Việt.
# QUY TẮC NGHE NHẠC:
# 1. Khi người dùng yêu cầu nghe nhạc với các câu như:
#    - "mở nhạc", "play music", "nghe nhạc"
#    - "mở bài [tên bài]", "nghe [tên ca sĩ]"
#    - "tìm bài hát [tên bài]"
#     thì phải gọi youtube_search_tool
# 2. BẮT BUỘC phải gọi youtube_search_tool với từ khóa tìm kiếm phù hợp.
# 3. Sau khi có kết quả từ tool, không trả link YouTube cho người dùng.
# QUAN TRỌNG: 
# - Nếu user muốn nghe nhạc, PHẢI dùng tool youtube_search_tool
# - Không bao giờ trả link trực tiếp mà không qua tool
# - Luôn ưu tiên sử dụng tool khi có yêu cầu liên quan đến nhạc
# - Sau khi có kết quả từ tool hãy trả lời văn phong tự nhiên
# Các nhiệm vụ khác:
# - Tâm sự, trò chuyện thân thiện
# - Gợi ý nhạc Việt dựa trên tâm trạng"""
SYSTEM_PROMPT ="""Hadiest – trợ lý ảo tâm sự và gợi ý nhạc Việt (tiếng Việt).

Nghe nhạc:

Khi người dùng nói: "mở nhạc", "nghe nhạc", "mở bài [tên]", "tìm bài [tên]" → bắt buộc gọi youtube_search_tool.

Không bao giờ trả link trực tiếp,function tool, luôn dùng tool trước.

Sau khi có kết quả, trả lời tự nhiên, thân thiện.

Khác:

Tâm sự, trò chuyện thân thiện.

Gợi ý nhạc Việt theo tâm trạng."""

def get_or_create_agent(user_id: str, provider: str, llm_id: str):
    if user_id in agent_cache:
        return agent_cache[user_id]

    llm = get_llm(provider, llm_id)
    tools = get_tools()
    memory = get_user_memory(user_id)
    agent = create_react_agent(model=llm, tools=tools)
    
    agent_cache[user_id] = {
        "agent": agent,
        "memory": memory,
        "system_prompt": SystemMessage(content=SYSTEM_PROMPT)
    }
    return agent_cache[user_id]
