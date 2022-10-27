import TranscriptDB
from audio_helper import Audio
from TranscriptDB import AudioFile, PDF
import argparse

import settings as s
# from threading import Thread

def main(args):
    if args.audio:
        audio = Audio(args.audio)

    if args.pdf:
        pdf = PDF(args.pdf)

    if args.transcript:




if __name__ == "__main__":
    # init_folders()
    # if False:
    parser = argparse.ArgumentParser(description='Process transcriptions.')

    parser.add_argument("-a", "--audio", help="Path to audio file")
    parser.add_argument("-p", "--pdf", help="Path to pdf file")
    parser.add_argument("-s", "--srt", help="Path to srt file in VTT format")
    parser.add_argument("-t", "--text", help="Path to text file")
    args = parser.parse_args()
    main(args)
    # file_path = args.file_path
    # audio_file = AudioFile(file_path)
    # print(audio_file.id)

    # pdf = PDF("multimedia/5912__0243_PM_greg_butch_discuss_docs_2012-05-09-154358.pdf", audio_file_id=3, layout_type=1)


    # audio = Audio('multimedia/5912__0243_PM_greg_butch_discuss_docs_2012-05-09-154358.mp3')
    # audiofile = AudioFile(audio.audio_filepath)

    snip = TranscriptDB.process_snippets()
    snip.to_csv('snip.csv', index=False)


