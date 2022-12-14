import argparse
import os

import assemblyai_helper as aai
import settings as s
import TranscriptDB as tdb
import media_helper as mh
from media_helper import Media


def process_audio(i, o):
    Media(i, os.path.join(s.CONFIG.root, s.CONFIG.folders["audio"], o))


def process_pdf(i, l, o):
    tdb.TranscriptFile(i, l, os.path.join(s.CONFIG.root, s.CONFIG.folders["pdf"], o))


def process_aai(i, o):
    aai.AssemblyAI(i, o)


def process_lookup(aud, man, lookup, out):
    snippets_timed = tdb.process_snippets_files(lookup, aud, man)
    snippets_timed.to_csv(out, index=False)


def process_clips(i, sn):
    snippets = tdb.read_snippets(sn)
    mh.get_clips(i, snippets)


def parse_args():
    parser = argparse.ArgumentParser(description='Process transcriptions.')
    subparsers = parser.add_subparsers(dest='command', help='Commands to run', required=True)

    parser_audio = subparsers.add_parser('audio', help='Process audio file')
    parser_audio.add_argument('i', help='Input file')
    parser_audio.add_argument('o', help='Output filename')
    parser_audio.set_defaults(func=process_audio)

    parser_pdf = subparsers.add_parser('pdf', help='Extract text from PDF file')
    parser_pdf.add_argument('i', help='Input file')
    parser_pdf.add_argument('l', type=int, choices=range(0, 2),
                            help='Layouts: 0 - single page, 1 - 2 by 2 pages on page')
    parser_pdf.add_argument('o', help='Output filename')
    parser_pdf.set_defaults(func=process_pdf)

    parser_aai = subparsers.add_parser('aai', help='Process audio file with AssemblyAI')
    parser_aai.add_argument('i', help='Input file. Must be in audio file format. Local or URL. Local one will be uploaded.')
    parser_aai.add_argument('o', help='Output filename. Output will be saved in VTT and CSV format in SRT folder.')
    parser_aai.set_defaults(func=process_aai)

    parser_lookup = subparsers.add_parser('lookup', help='Process lines')
    parser_lookup.add_argument('aud', help='Audio transcription file. CSV file created by AssemblyAI.')
    parser_lookup.add_argument('man', help='Manual transcription file. CSV court transcript from PDF.')
    parser_lookup.add_argument('lookup', help='Snippets CSV file.')
    parser_lookup.add_argument('out', help='Output filename to save snippets with timings.')
    parser_lookup.set_defaults(func=process_lookup)

    parser_clips = subparsers.add_parser('clips', help='Process clips')
    parser_clips.add_argument('i', help='Input audio/video file')
    parser_clips.add_argument('sn', help='Timed snippets file. CSV file created by lookup command.')
    parser_clips.set_defaults(func=process_clips)

    args = parser.parse_args()
    args_ = vars(args).copy()
    args_.pop('command', None)
    args_.pop('func', None)
    args.func(**args_)
