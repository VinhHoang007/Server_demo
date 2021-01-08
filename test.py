from gtts import gTTS
import os

data = 'hello chào bạn mình muốn kiểm tra có hoạt động bình thường không. Môn học trước của môn học sau là gì đó'
tts = gTTS(text=data,lang = 'vi')
tts.save("test.mp3")
os.system("start test.mp3")
os.remove('test.mp3')
