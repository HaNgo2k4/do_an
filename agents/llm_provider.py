from langchain_groq import ChatGroq
from backend.config import GROQ_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(provider, model):
    if provider == "Groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY NOT FOUND")
        return ChatGroq(model=model, api_key=GROQ_API_KEY)
    else:
        raise ValueError("Unknown provider")
    # return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)