import base64
import hashlib
import hmac
import os
import time
import requests
from backend.config import ACRCLOUD_ACCESS_KEY,ACRCLOUD_ACCESS_SECRET,ACRCLOUD_REQ_URL
ACCESS_KEY = ACRCLOUD_ACCESS_KEY
ACCESS_SECRET = ACRCLOUD_ACCESS_SECRET
REQ_URL = ACRCLOUD_REQ_URL

def identify_song(file_path: str):
    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = str(int(time.time()))

    # Tạo signature
    string_to_sign = f"{http_method}\n{http_uri}\n{ACCESS_KEY}\n{data_type}\n{signature_version}\n{timestamp}"
    sign = base64.b64encode(hmac.new(
        ACCESS_SECRET.encode('ascii'),
        string_to_sign.encode('ascii'),
        digestmod=hashlib.sha1
    ).digest()).decode('ascii')

    sample_bytes = os.path.getsize(file_path)
    data = {
        "access_key": ACCESS_KEY,
        "sample_bytes": sample_bytes,
        "timestamp": timestamp,
        "signature": sign,
        "data_type": data_type,
        "signature_version": signature_version,
    }

    try:
        with open(file_path, "rb") as f:
            files = {"sample": (os.path.basename(file_path), f, "audio/wav")}
            r = requests.post(REQ_URL, files=files, data=data, timeout=15)
            r.raise_for_status()
            result = r.json()
    except requests.RequestException as e:
        print(f"Lỗi khi gọi ACRCloud: {e}")
        return []

    songs_info = []
    music_list = result.get("metadata", {}).get("music", [])
    for song in music_list:
        title = song.get("title", "Unknown")
        artists = [artist["name"] for artist in song.get("artists", [])]
        youtube_vid = song.get("external_metadata", {}).get("youtube", {}).get("vid", None)
        songs_info.append({
            "title": title,
            "artists": artists,
            "youtube_vid": youtube_vid
        })
    return songs_info

