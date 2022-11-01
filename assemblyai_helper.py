import os
import time

import pandas as pd
import requests
import webvtt

import settings as s
import io
import validators


class AssemblyAI:
    def __init__(self, filepath, output_name):
        self.headers = {
            "authorization": s.ASSEMBLYAI.api_key,
            "content-type": "application/json",
        }
        self.api_url = s.ASSEMBLYAI.api_url
        self.output_name = output_name
        self.start_time = None
        self.filepath = filepath
        if validators.url(filepath):
            self.file_url = filepath
        else:
            self.file_url = self.upload_file()
        self.job_id = self.set_transcribe_job()
        self.srt = self.get_transcript_srt()
        self.transcript = self.get_transcript()
        self.words = self.transcript['words']

    def upload_file(self):
        print("Uploading file to AssemblyAI...")
        file_upload = requests.post(f"{self.api_url}/upload",
                                    headers=self.headers,
                                    data=read_file(self.filepath))
        file_url = file_upload.json()['upload_url']
        print(f"File uploaded to:\n{file_url}")
        return file_url

    def set_transcribe_job(self):
        print(f"Transcribing file:\n{self.file_url}")
        response = requests.post(f"{self.api_url}/transcript",
                                 headers=self.headers,
                                 json={"audio_url": self.file_url})
        self.start_time = time.gmtime()
        if response.status_code == 200:
            job_id = response.json()['id']
            print(f"Transcription started at: " + time.strftime("%H:%M:%S", self.start_time))
            print(f"Job ID: {job_id}")
            return job_id
        else:
            print(response.status_code)
            print(response.text)
            exit()

    def get_transcript_srt(self):
        if self.poll_status() == 'completed':
            response = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}/{s.ASSEMBLYAI.subtitles_format}",
                                    headers=self.headers)

            # save response to file
            srt_folder = os.path.join(s.CONFIG.root, s.CONFIG.folders["srt"])
            output_file_srt = os.path.join(srt_folder, f"{self.output_name}.{s.ASSEMBLYAI.subtitles_format}")
            output_file_csv = os.path.join(srt_folder, s.CONFIG.folders["srt"], f"{self.output_name}.csv")
            with open(output_file_srt, "w") as f:
                f.write(response.text)
            print(f"SRT saved to:\n{output_file_srt}")

            df = pd.DataFrame(columns=['start', 'end', 'text', 'audio_file_id'])

            for caption in webvtt.read_buffer(io.StringIO(response.text)):
                df = pd.concat([df, pd.DataFrame([[caption.start_in_seconds, caption.end_in_seconds, caption.text, self.filepath]],
                                                    columns=['start', 'end', 'text', 'audio_file_id'])], ignore_index=True)
            df.to_csv(output_file_csv, index=False)
            return df

    def get_transcript(self):
        print("Getting transcript...")
        if self.poll_status() == 'completed':
            response = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                                    headers=self.headers)
            return response.json()

    def poll_status(self):
        print("Polling status...")
        status = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                              headers=self.headers).json()['status']
        # print time from start in hh:mm:ss
        while status not in ['completed', 'error']:
            time.sleep(s.ASSEMBLYAI.polling_interval)
            status = requests.get(f"{s.ASSEMBLYAI.api_url}/transcript/{self.job_id}",
                                  headers=self.headers).json()['status']
        if status == 'error':
            print("Error occurred. Exiting...")
            exit()
        elif status == 'completed':
            # job took hh:mm:ss
            return status


def read_file(filepath, chunk_size=s.ASSEMBLYAI.chunk_size):
    with open(filepath, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data
