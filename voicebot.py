import speech_recognition
from gtts import gTTS
import os, string
import playsound,chatprocess
from datetime import date,datetime

def voicebot(course):
	#os.remove('./static/voice.mp3')
	today = date.today()
	robot_ear = speech_recognition.Recognizer()
	robot_brain = ""
		
	with speech_recognition.Microphone() as mic:
		print("Robot: I'm listening")
		robot_ear.pause_threshold = 1.5
		robot_ear.adjust_for_ambient_noise(mic,duration=1)
		audio = robot_ear.listen(mic,0)
		with open('./static/question.wav','wb') as file:
			wav_data = audio.get_wav_data()
			file.write(wav_data)
	
	print("Robot: ...")    
	try:
		you = robot_ear.recognize_google(audio,language='vi-VN').lower()
	except:
		you = ""
	print("you: " + you)

	if you != "":
		robot_brain = chatprocess.chatbot_response(you,course)
	else:
		robot_brain = "Tôi không nghe được bạn nói gì ! Hãy thử lại nhé !"
	
	print("Robot: " + robot_brain)

	tts=gTTS(text=robot_brain,lang='vi',slow=False)
	tts.save("./static/answer.mp3")