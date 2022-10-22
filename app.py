import requests
import settings as S
from flask import Flask
from pyngrok import ngrok
import json
import pandas as pd


class AssemblyAI:
    def __init__(self, filepath):
        self.headers = {
            "authorization": S.ASSEMBLYAI.api_key,
            "content-type": "application/json",
        }
        self.api_url = S.ASSEMBLYAI.api_url
        self.filepath = filepath
        self.file_url = self.upload_file()
        self.job_id = self.transcribe()
        self.srt = self.get_transcript_srt()

    def read_file(self, filepath, chunk_size=5242880):
        with open(filepath, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    def upload_file(self):
        file_upload = requests.post(f"{self.api_url}/upload",
                                    headers=self.headers,
                                    data=self.read_file(self.filepath))
        file_url = file_upload.json()['upload_url']
        print(file_url)
        return file_url

    def transcribe(self):
        response = requests.post(f"{self.api_url}/transcript",
                                 headers=self.headers,
                                 json={"audio_url": self.file_url})
        return response.json()['id']

    def get_transcript_srt(self):
        headers = {
            "authorization": S.ASSEMBLYAI.api_key,
            "content-type": "application/json"
        }
        response = requests.get(f"{S.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                                headers=headers)
        # write to file
        with open(f"{self.job_id}.srt", 'w') as f:
            f.write(response.text)
        return response.text


if __name__ == "__main__":
    filename = "audio.wav"
    aai = AssemblyAI(filename)
    print(aai.srt)

