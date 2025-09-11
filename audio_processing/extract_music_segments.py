import torch
import soundfile as sf
from pathlib import Path
from audio_processing.remove_silence import remove_silence

print("⏳ Đang load Silero VAD...")
model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    force_reload=False
)
(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils
print("✅ Silero VAD loaded")


def separate_speech_music(input_file: str, output_dir: str = None):
    wav, sr = sf.read(input_file, dtype="float32")
    if wav.ndim > 1:   
        wav = wav[:, 0]
    wav = torch.tensor(wav)

    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sr)

    if len(speech_timestamps) > 0:
        speech_wav = collect_chunks(speech_timestamps, wav)
    else:
        print("Không phát hiện giọng nói trong file.")
        speech_wav = torch.zeros(0)

    # Collect non-speech
    if len(speech_timestamps) > 0:
        nonspeech_wav = torch.zeros_like(wav)
        last_end = 0
        for ts in speech_timestamps:
            start, end = ts['start'], ts['end']
            nonspeech_wav[last_end:start] = wav[last_end:start]
            last_end = end
        nonspeech_wav[last_end:] = wav[last_end:]
    else:
        nonspeech_wav = wav 
    input_path = Path(input_file)
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    speech_file = output_dir / "speech.wav"
    nonspeech_file = output_dir / "nonspeech.wav"


    sf.write(str(speech_file), speech_wav.numpy(), sr)
    print(f"Saved speech: {speech_file}")


    if nonspeech_wav.numel() > 0:
        sf.write(str(nonspeech_file), nonspeech_wav.numpy(), sr)
        print(f"Saved nonspeech: {nonspeech_file}")
    else:
        print("Không lưu nonspeech.wav vì rỗng")
    results = {"speech": None, "nonspeech": None}
    if speech_file.exists() and speech_file.stat().st_size > 100:
        clean_speech = output_dir / "speech_clean.wav"

    # Gọi hàm remove_silence để tạo file speech sạch
        if remove_silence(str(speech_file), str(clean_speech)):
            if clean_speech.exists() and clean_speech.stat().st_size > 0:
                results["speech"] = str(speech_file)
            else:
                print(f"File speech_clean rỗng hoặc không hợp lệ: {clean_speech}")
        else:
            print(f"File speech.wav rỗng hoặc không hợp lệ: {speech_file}")
    else:
            print(f"File speech.wav rỗng hoặc không hợp lệ: {speech_file}")
    if nonspeech_file.exists() and nonspeech_file.stat().st_size > 100:
        clean_nonspeech = output_dir / "nonspeech_clean.wav"

        # Gọi hàm remove_silence để tạo file sạch
        if remove_silence(str(nonspeech_file), str(clean_nonspeech)):
            if clean_nonspeech.exists() and clean_nonspeech.stat().st_size > 100:
                results["nonspeech"] = str(clean_nonspeech)
            else:
                print(f"File nonspeech_clean rỗng hoặc không hợp lệ: {clean_nonspeech}")
    else:
        print(f"File nonspeech.wav rỗng hoặc không hợp lệ: {nonspeech_file}")
    return results
