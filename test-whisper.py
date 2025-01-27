import whisper
from pydub import AudioSegment
import os
print(os.path.exists(r"C:\Users\trica\Downloads\20250125_183700.aac"))

AudioSegment.from_file("C:\\Users\\trica\\Downloads\\20250125_183700.aac").export("C:\\Users\\trica\\Downloads\\20250125_183700.mp3", format="mp3")
model = whisper.load_model("turbo")
result = model.transcribe("C:\\Users\\trica\\Downloads\\20250125_183700.mp3")
print(result["text"])