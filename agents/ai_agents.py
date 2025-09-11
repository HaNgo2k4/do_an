from agents.agent_manager import get_or_create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def normalize_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for c in content:
            if isinstance(c, dict) and "text" in c:
                texts.append(c["text"])
            elif isinstance(c, str):
                texts.append(c)
        return " ".join(texts)
    return str(content)

def normalize_messages(messages):
    normalized = []
    for m in messages:
        if isinstance(m, HumanMessage):
            normalized.append(HumanMessage(content=normalize_content(m.content)))
        elif isinstance(m, AIMessage):
            normalized.append(AIMessage(content=normalize_content(m.content)))
        elif isinstance(m, ToolMessage):
            normalized.append(ToolMessage(content=normalize_content(m.content), tool_call_id=m.tool_call_id))
        else:
            normalized.append(HumanMessage(content=str(m)))
    return normalized

def get_response_from_ai_agent(llm_id, query, provider, user_id: str, has_wav: bool = False):
    # --- Lấy agent và memory ---
    cache = get_or_create_agent(user_id, provider, llm_id)
    agent = cache["agent"]
    memory = cache["memory"]
    system_prompt = cache["system_prompt"]

    past_messages = memory.load_memory_variables({}).get("chat_history", [])
    past_messages = normalize_messages(past_messages)
    if isinstance(query, list):
        user_message = query[-1].content if hasattr(query[-1], "content") else str(query[-1])
    else:
        user_message = str(query)
    enhanced_system_prompt = system_prompt
    if has_wav:
        enhanced_content = system_prompt.content + f"\n\nQUAN TRỌNG: Người dùng đã upload file audio (has_wav=True). Hãy sử dụng identify_song_tool để nhận diện bài hát trước khi trả lời."
        from langchain_core.messages import SystemMessage
        enhanced_system_prompt = SystemMessage(content=enhanced_content)
    
    # Tạo message với metadata
    human_msg = HumanMessage(content=user_message, metadata={"has_wav": has_wav, "user_id": user_id})
    state_messages = [enhanced_system_prompt] + past_messages + [human_msg]
    state = {"messages": state_messages}

    # --- Gọi agent ---
    response = agent.invoke(state)

    ai_messages = []
    tool_results = []

    messages = response.get("messages", [])
    last_human_index = None
    for i in range(len(messages)-1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            last_human_index = i
            break
    subset_messages = messages[last_human_index:] if last_human_index is not None else []

    # --- Xử lý phản hồi ---
    for msg in subset_messages:
        if isinstance(msg, AIMessage) and msg.content:
            ai_messages.append(normalize_content(msg.content))
        elif isinstance(msg, ToolMessage):
            tool_results.append(normalize_content(msg.content))
            print("🔹 Tool được gọi:", msg.tool_call_id)
            print("🔹 Kết quả:", normalize_content(msg.content))

    # --- Lưu chat history ---
    memory.chat_memory.add_user_message(query)
    final_ai_response = ai_messages[-1] if ai_messages else "Xin lỗi, tôi không thể phản hồi lúc này."
    if final_ai_response:
        memory.chat_memory.add_ai_message(final_ai_response)

    return {
        "ai": final_ai_response,
        "tool": tool_results,
    }
