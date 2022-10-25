import TranscriptDB
from audio_helper import Audio
from TranscriptDB import AudioFile, PDF
import argparse

import settings as s
# from threading import Thread


if __name__ == "__main__":
    # init_folders()
    if False:
        parser = argparse.ArgumentParser()
        parser.add_argument("file_path", help="Path to audio file")
        args = parser.parse_args()
        file_path = args.file_path
        audio_file = AudioFile(file_path)
        print(audio_file.id)

    # pdf = PDF("multimedia/5912__0243_PM_greg_butch_discuss_docs_2012-05-09-154358.pdf", audio_file_id=3, layout_type=1)


    # audio = Audio('multimedia/5912__0243_PM_greg_butch_discuss_docs_2012-05-09-154358.mp3')
    # audiofile = AudioFile(audio.audio_filepath)

    snip = TranscriptDB.process_snippets()
    snip.to_csv('snip.csv', index=False)


