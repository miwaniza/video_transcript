# from flask import Flask
# from pyngrok import ngrok

from assemblyai_helper import AssemblyAI
from audio_helper import Audio
from TranscriptDB import AudioFile

import settings as s
# from threading import Thread


if __name__ == "__main__":
    audio = Audio('video.mp4', 0, 60)
    audiofile = AudioFile(audio.audio_filepath)


