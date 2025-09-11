import os
import subprocess

def remove_silence(input_file: str, output_file: str) -> bool:
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)

    # Kiểm tra file có tồn tại và có dữ liệu
    if not os.path.exists(input_file):
        print(f"File không tồn tại: {input_file}")
        return False
    if os.path.getsize(input_file) == 0:
        print(f"File rỗng, bỏ qua xử lý: {input_file}")
        return False

    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-af", "silenceremove=start_periods=1:start_duration=1:start_threshold=-40dB:stop_periods=1:stop_duration=1:stop_threshold=-40dB",
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        print("Đã cắt im lặng đầu + cuối:", output_file)
        return True
    except subprocess.CalledProcessError as e:
        print("Lỗi khi xử lý ffmpeg:", e.stderr)
        return False
