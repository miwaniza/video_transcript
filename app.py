# from flask import Flask
# from pyngrok import ngrok

from assemblyai import AssemblyAI
from video_helper import Video

if __name__ == "__main__":
    video = Video("video.mp4", 0, 60)
    audio_filepath = video.audio_filepath
    print(audio_filepath)

    aai = AssemblyAI(audio_filepath)
    print(aai.srt)
