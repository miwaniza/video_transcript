import time

import requests

import settings as s


class AssemblyAI:
    def __init__(self, filepath):
        self.headers = {
            "authorization": s.ASSEMBLYAI.api_key,
            "content-type": "application/json",
        }
        self.api_url = s.ASSEMBLYAI.api_url
        self.filepath = filepath
        self.file_url = self.upload_file()
        self.job_id = self.set_transcribe_job()
        self.srt = self.get_transcript_srt()

    def upload_file(self):
        file_upload = requests.post(f"{self.api_url}/upload",
                                    headers=self.headers,
                                    data=read_file(self.filepath))
        file_url = file_upload.json()['upload_url']
        print(file_url)
        return file_url

    def set_transcribe_job(self):
        response = requests.post(f"{self.api_url}/transcript",
                                 headers=self.headers,
                                 json={"audio_url": self.file_url})
        return response.json()['id']

    def get_transcript_srt(self):
        # await job completion
        while True:
            status = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                                  headers=self.headers)
            if status.json()['status'] == 'completed':
                break
            elif status.json()['status'] == 'error':
                raise Exception(status.json()['error'])
            else:
                print(status.json()['status'])
                time.sleep(s.ASSEMBLYAI.polling_interval)
                continue

        response = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}/{s.ASSEMBLYAI.subtitles_format}",
                                headers=self.headers)

        with open(f"{self.job_id}.{s.ASSEMBLYAI.subtitles_format}", 'w') as f:
            f.write(response.text)
        return response.text


def read_file(filepath, chunk_size=s.ASSEMBLYAI.chunk_size):
    with open(filepath, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data
