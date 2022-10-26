import time

import requests

import settings as s
import io


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
        self.transcript = self.get_transcript()
        self.words = self.transcript['words']

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
        if self.poll_status() == 'completed':
            response = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}/{s.ASSEMBLYAI.subtitles_format}",
                                    headers=self.headers)

            df = pd.DataFrame(columns=['start', 'end', 'text', 'audio_file_id'])

            for caption in webvtt.read_buffer(io.StringIO(response.text)):
                df = df.append({'start': caption.start_in_seconds, 'end': caption.end_in_seconds, 'text': caption.text,
                                'audio_file_id': self.audio_file_id},
                               ignore_index=True)

            return df


    def get_transcript(self):
        if self.poll_status() == 'completed':
            response = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                                    headers=self.headers)
            return response.json()

    def poll_status(self):
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
        return status.json()['status']


def read_file(filepath, chunk_size=s.ASSEMBLYAI.chunk_size):
    with open(filepath, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data
