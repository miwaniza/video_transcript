import os

from pydub import AudioSegment
from pydub.silence import split_on_silence


def silence_based_conversion(path="alice-medium.wav"):
    song = AudioSegment.from_wav(path)
    chunks = split_on_silence(song,
                              min_silence_len=500,
                              silence_thresh=-16
                              )
    try:
        os.mkdir('audio_chunks')
    except(FileExistsError):
        pass
    os.chdir('audio_chunks')

    # process each chunk
    for i, chunk in enumerate(chunks):
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration=10)

        audio_chunk = chunk_silent + chunk + chunk_silent

        print("saving chunk{0}.wav".format(i))
        audio_chunk.export("./chunk{0}.wav".format(i), bitrate='192k', format="wav")
        filename = 'chunk' + str(i) + '.wav'
        print("Processing chunk " + str(i))

    os.chdir('..')


if __name__ == '__main__':
    print('Enter the audio file path')

    path = input()

    silence_based_conversion(path)
