from audio_helper import Audio
from TranscriptDB import AudioFile
import argparse

import settings as s
# from threading import Thread


if __name__ == "__main__":
    # init_folders()
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to audio file")
    args = parser.parse_args()
    file_path = args.file_path
    audio_file = AudioFile(file_path)
    print(audio_file.id)

    # audio = Audio('video.mp4', 0, 60)
    # audiofile = AudioFile(audio.audio_filepath)


