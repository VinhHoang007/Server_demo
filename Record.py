import pyaudio
import wave
def record():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "./static/question_client.wav"
    audio = pyaudio.PyAudio()


    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,frames_per_buffer=CHUNK)
    print ("recording started")
    Recordframes = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        Recordframes.append(data)
    print ("recording stopped")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(Recordframes))
    waveFile.close()

record()

