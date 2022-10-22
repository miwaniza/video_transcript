import requests
import json
import pandas as pd

filename = "audio.wav"


def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


file_upload = requests.post('https://api.assemblyai.com/v2/upload',
                        headers=headers,
                        data=read_file(filename))

file_url = file_upload.json()['upload_url']

endpoint = "https://api.assemblyai.com/v2/transcript"
json = {
    "audio_url": file_url
}
headers = {
    "authorization": "68ae0c7c0d2945a3a411da7cb55e46c6",
    "content-type": "application/json"
}
# response = requests.post(endpoint, json=json, headers=headers)
# print(response.json())

endpoint = "https://api.assemblyai.com/v2/transcript/rzb3mg9c2r-66e3-4a48-9561-0efe9c651a1d/srt"

response = requests.get(endpoint, headers=headers)
# write response text to file
with open("transcript.srt", "w") as f:
    f.write(response.text)

# words = response.json()["words"]
# df = pd.DataFrame(words)
# df.to_csv("words.csv", index=False)
