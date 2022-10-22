import ffmpeg

import settings as s


class Video:
    def __init__(self, filepath, start_time, end_time):
        self.filepath = filepath
        self.audio_filepath = f"{self.filepath.split('.')[0]}.{s.ASSEMBLYAI.audio_format}"
        self.start_time = start_time
        self.end_time = end_time
        self.cut_audio()

    def cut_audio(self):
        stream = ffmpeg.input(self.filepath)
        stream = ffmpeg.output(stream, self.audio_filepath, ss=self.start_time, t=self.end_time)
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Audio file saved to {self.audio_filepath}")
        return self.audio_filepath
