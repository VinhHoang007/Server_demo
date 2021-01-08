import speech_recognition
from gtts import gTTS
import os, string
import playsound,chatprocess
import socket
import time

host = ''
port = 5560

def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket bind comlete.")
    return s

def setupConnection():
    s.listen(1) # Allows one connection at a time.
    conn, address = s.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    return conn



def sendToClient(conn):
    #conn.send(str.encode(data))
    f = open('./static/answer_server.wav','rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       l = f.read(1024)
    conn.send(str.encode("#"))
    f.close()
     
    print('Done sending')

def recvFrClient(conn):
    with open('./static/question_client.wav', 'wb') as f:
        while True:
            data = conn.recv(1024)
            #print('data=%s', (data))
            try:
                abs = data[-1].to_bytes(2, 'big').decode('utf-8')
                # print(abs)
                if "7" in abs:
                    return "17"
                    break
                if "9" in abs:
                    return "19"
                    break       
            except:
                #print("khong decode")
                pass
   
            f.write(data)

        f.close()
        
    print('Successfully get the file from client')

def voiceProcess(course):
    r = speech_recognition.Recognizer()
    filename = './static/question_client.wav'
    with speech_recognition.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data,language='vi-VN').lower()
    print("you **********************: " + text)
    robot_brain = ""
    if text != "":
        robot_brain = chatprocess.chatbot_response(text,course)
    else:
        robot_brain = "Tôi không nghe được bạn nói gì ! Hãy thử lại nhé !"
    print("Robot: " + robot_brain)
   
    tts=gTTS(text=robot_brain, lang='vi', slow=False)
    tts.save("./static/answer_server.wav")

if __name__=='__main__':


    s = setupServer()
    
    while(True):

        conn = setupConnection()

        recvValue= recvFrClient(conn)
        if recvValue == "17":

            voiceProcess("17")
            sendToClient(conn)

        if recvValue == "19":

            voiceProcess("19")
            sendToClient(conn)

        print("=================================================================================")