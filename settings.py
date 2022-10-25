import os


class ASSEMBLYAI:
    api_key = os.environ.get('ASSEMBLYAI_API_KEY')
    api_url = "https://api.assemblyai.com/v2"
    polling_interval = 10
    chunk_size = 1024 * 1024 * 5
    audio_format = "wav"
    subtitles_format = "srt"


class DATABASE:
    __uri = os.environ["DATABASE_URL"]
    DB_URL = __uri.replace("postgres://", "postgresql://", 1) if __uri.startswith("postgres://") else __uri


class AUDIO:
    audio_formats = ["wav", "mp3", "flac", "ogg", "m4a", "aac", "wma", "aiff"]


class VIDEO:
    video_formats = ["mp4", "avi", "flv", "wmv", "mov", "mkv", "webm", "3gp"]


class SCRIPT:
    TAGS = ["[inaudible]", "[music]", "[applause]", "[laughter]", "[crosstalk]", "(phon.)",
            "[Background conversation.]", "(Commencement of electronic recording.)",
            "(Conclusion of electronic recording.)"]
