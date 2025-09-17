import speech_recognition as sr
import time

class WavSpeechRecognizer:
    def __init__(self):
        self.r = sr.Recognizer()

    def recognize_wav(self, filepath: str):
        results = []
        try:
            with sr.AudioFile(filepath) as source:
                audio = self.r.record(source) 
                text = self.r.recognize_google(audio, language="vi-VN")
                timestamp = time.strftime('%H:%M:%S')
                results.append({"time": timestamp, "text": text})
        except sr.UnknownValueError:
            results.append({"error": "Không hiểu âm thanh"})
        except sr.RequestError as e:
            results.append({"error": str(e)})
        return results