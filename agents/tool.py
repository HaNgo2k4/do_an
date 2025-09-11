from langchain.tools.base import BaseTool
from googleapiclient.discovery import build
from pydantic import Field
from pathlib import Path
from audio_processing.ACRCloud_identify_protocol_v1 import identify_song
import json
import asyncio
class youtube_search_tool(BaseTool):  
    name: str = "youtube_search_tool"
    youtube_api_key: str = Field(
        ...,
        description="API key for accessing YouTube data."
    )

    description: str = (
     "Sử dụng tool này khi người dùng:\n"
        "- Yêu cầu nghe nhạc: 'mở bài hát X', 'phát nhạc Y', 'tìm bài Z'\n"
        "- Tìm ca sĩ: 'nghe nhạc của ca sĩ A', 'mở nhạc B'\n"
        "- Các từ khóa: mở, phát, nghe, tìm, nhạc, bài hát, ca sĩ\n"
        "Input: query (tên bài hát hoặc ca sĩ)\n"
        "Output không trả link youtube"        
)
  
    def __init__(self, youtube_api_key: str, **kwargs):
        # Khởi tạo với youtube_api_key
        super().__init__(youtube_api_key=youtube_api_key, **kwargs)


    def _run(self, query: str, max_results: int = 5) -> str:

        try:
            youtube = build("youtube", "v3", developerKey=self.youtube_api_key)
            # print(query)
            response = youtube.search().list(
                q=query,
                part="id,snippet",
                type="video",
                # videoCategoryId="10",
                maxResults=max_results,
                order="relevance"
            ).execute()
            results = []
            for item in response.get("items", []):
                if item["id"]["kind"] == "youtube#video":
                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    results.append({
                        "title": title,
                        "video_id": video_id
                    })
                    break

            if not results:

                return json.dumps({"error": "Không tìm thấy kết quả."}, ensure_ascii=False)
            return json.dumps(results[0], ensure_ascii=False) if results else ""
                
        except Exception as e:
            print("Lỗi khi gọi YouTube API:", e)
            return f""

    async def _arun(self, query: str, max_results: int = 1) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run, query, max_results)

class identify_song_tool(BaseTool):
    name: str = "identify_song_tool"
    user_id: str = Field(..., description="User ID để xác định file nhạc")
    
    description: str = (
        "Nhận diện bài hát từ microphone.\n"
        "Sử dụng khi người dùng đã sử dụng microphone và cần nhận diện bài hát.\n"
        "Output: thông tin bài hát bao gồm title, artists"
    )
    def __init__(self, user_id: str):
        super().__init__(user_id=user_id)
    def _run(self) -> str:
        target_user_id = self.user_id
        UPLOAD_DIR = Path("AudioFiles")
        file_path = UPLOAD_DIR / target_user_id / "nonspeech_clean.wav"
        if not file_path.exists():
            return {"error": "File nhạc không tồn tại cho session này."}
        music_info = identify_song(file_path)
        if not music_info:
            return {"error": "Không nhận diện được bài hát"}

        song = music_info[0]
        title = song.get("title", "Unknown")
        artists = song.get("artists", [])
        youtube_vid = song.get("external_metadata", {}).get("youtube", {}).get("vid", None)

        result = [{
        "title": title,
        "artists": artists
        }]
        if youtube_vid:
            result[0]["video_id"] = youtube_vid
        return result

    async def _arun(self, file_path: str) -> str:
        return self._run(file_path)
