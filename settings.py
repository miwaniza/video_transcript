import os


class ASSEMBLYAI:
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    api_url = "https://api.assemblyai.com/v2"
    polling_interval = 10
    chunk_size = 1024 * 1024 * 5
    audio_format = "wav"
    subtitles_format = "srt"

