import argparse
import os

import settings as s
from TranscriptDB import PDF
from audio_helper import Audio


class Caller:
    def __init__(self) -> None:
        pass

    def process_audio(self, i, o):
        Audio(i, os.path.join(s.CONFIG.root, s.CONFIG.folders["audio"], o))

    def process_pdf(self, i, o, l):
        PDF(input_file, layout, os.path.join(s.CONFIG.root, s.CONFIG.folders["pdf"], output_file))

    def process_aai(self, i, o):
        pass

    def process_lines(self):
        pass


def main():
    parse_args()


def parse_args():
    caller = Caller()

    parser = argparse.ArgumentParser(description='Process transcriptions.')
    subparsers = parser.add_subparsers(dest='command', help='Commands to run', required=True)

    parser_audio = subparsers.add_parser('audio', help='Process audio file')
    parser_audio.add_argument('i', help='Input file')
    parser_audio.add_argument('o', help='Output filename')
    parser_audio.set_defaults(func=caller.process_audio)

    parser_pdf = subparsers.add_parser('pdf', help='Extract text from PDF file')
    parser_pdf.add_argument('i', help='Input file')
    parser_pdf.add_argument('o', help='Output filename')
    parser_pdf.add_argument('l', help='Layout')
    parser_pdf.set_defaults(func=caller.process_pdf)

    parser_aai = subparsers.add_parser('aai', help='Process audio file with AssemblyAI')
    parser_aai.add_argument('i', help='Input file')
    parser_aai.add_argument('o', help='Output filename')
    parser_aai.set_defaults(func=caller.process_aai)

    process_lines = subparsers.add_parser('lines', help='Merge lines in transcript and recognized text')
    process_lines.set_defaults(func=caller.process_lines)

    args = parser.parse_args()
    args_ = vars(args).copy()
    args_.pop('command', None)
    args_.pop('func', None)
    args.func(**args_)


if __name__ == "__main__":
    main()

