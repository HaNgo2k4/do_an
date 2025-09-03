from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import redis, json
def get_user_memory(session_id: str):

    history = RedisChatMessageHistory(
        session_id=session_id,
        url="redis://localhost:6379/0"
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory= history
    )
    return memory


def get_dialogue_by_sessionId(session_id: str):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    msgs = r.lrange(f"message_store:{session_id}", 0, 20)

    dialogue = []
    temp_bot = None 

    for raw in msgs[::-1]:
        msg = json.loads(raw)
        role = msg["type"]
        content = msg["data"]["content"]
        print(msg)
        if role == "human":
            dialogue.append({"role": "user", "content": content})

        elif role == "ai":
            temp_bot = {"role": "bot", "content": content, "tool": []}
            dialogue.append(temp_bot)

        else: 
            try:
                if isinstance(content, list):
                    parsed = [json.loads(c) if isinstance(c, str) else c for c in content]
                else:
                    parsed = json.loads(content) if isinstance(content, str) else content
            except Exception:
                parsed = content
            if temp_bot:
                if isinstance(parsed, list):
                    temp_bot["tool"].extend(parsed)
                else:
                    temp_bot["tool"].append(parsed)

            else:
                dialogue.append({"role": "tool", "content": parsed})

    return dialogue