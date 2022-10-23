import ffmpeg

import settings as s


class Audio:
    def __init__(self, filepath, start_time=None, end_time=None):
        self.filepath = filepath
        self.format = filepath.split(".")[-1]
        self.start_time = start_time
        self.end_time = end_time
        self.duration = 0.0
        self.audio_filepath = None
        if self.format in s.VIDEO.video_formats:
            self.audio_filepath = self.extract_audio()
            self.duration = float(ffmpeg.probe(self.audio_filepath)['format']['duration'])
        elif self.format in s.AUDIO.audio_formats:
            self.audio_filepath = filepath
            self.duration = float(ffmpeg.probe(self.filepath)['format']['duration'])

    def extract_audio(self):
        self.audio_filepath = f"{self.filepath.split('.')[0]}.wav"
        return self.cut_audio()

    def cut_audio(self):
        stream = ffmpeg.input(self.filepath)
        if (self.start_time is not None) and (self.end_time is not None):
            stream = ffmpeg.output(stream, self.audio_filepath, ss=self.start_time, t=self.end_time)
            self.duration = self.end_time - self.start_time
        else:
            stream = ffmpeg.output(stream, self.audio_filepath)
            self.duration = float(ffmpeg.probe(self.filepath)['format']['duration'])
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Audio file saved to {self.audio_filepath}")
        return self.audio_filepath


