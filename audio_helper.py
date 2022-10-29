import ffmpeg
import shutil
import settings as s


class Audio:
    def __init__(self, source, target, start_time=None, end_time=None):
        self.source = source
        self.format = source.split(".")[-1]
        self.start_time = start_time
        self.end_time = end_time
        self.duration = 0.0
        self.target = target
        if self.format in s.VIDEO.video_formats:
            self.extract_audio()
            self.duration = float(ffmpeg.probe(self.target)['format']['duration'])
        elif self.format in s.AUDIO.audio_formats:
            shutil.copyfile(self.source, self.target)

    def extract_audio(self):
        stream = ffmpeg.input(self.source)
        if (self.start_time is not None) and (self.end_time is not None):
            stream = ffmpeg.output(stream, self.target, ss=self.start_time, to=self.end_time)
            self.duration = self.end_time - self.start_time
        else:
            stream = ffmpeg.output(stream, self.target)
            self.duration = float(ffmpeg.probe(self.source)['format']['duration'])
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Audio file saved to {self.target}")

