import ffmpeg
import shutil
import settings as s
import os
import re


class Media:
    def __init__(self, source, target, start_time=None, end_time=None, parent=None):
        self.source = source
        self.format = source.split(".")[-1]
        self.start_time = start_time
        self.end_time = end_time
        self.duration = 0.0
        self.target = target
        self.clips = []
        # if self.format in s.VIDEO.video_formats:
        #     self.extract_audio()
        self.duration = float(ffmpeg.probe(self.source)['format']['duration'])
        print(f"Audio duration: {self.duration}")
        if (self.duration > s.AUDIO.SPLIT_DURATION) and (parent is None):
            self.split_audio()
        else:
            print("Audio is short enough to skip splitting")
            self.clips = [self]

    def split_audio(self):
        clips = []
        start_time = 0.0
        end_time = s.AUDIO.SPLIT_DURATION
        while start_time < self.duration:
            if end_time > self.duration:
                end_time = self.duration
            # clip_name = f"{self.target.split('.')[0]}_{start_time}_{end_time}.{self.format}"
            extension = os.path.splitext(self.target)[1]
            initial_filename = os.path.splitext(self.target)[0]
            clip_name = f"{initial_filename}_{start_time}_{end_time}{extension}"
            clip = Media(self.source, clip_name, start_time, end_time, self)
            clips.append(clip)
            start_time = end_time
            end_time += s.AUDIO.SPLIT_DURATION
        self.clips = clips
        print(f"Audio split into {len(clips)} clips")
        clips_csv = os.path.join(s.CONFIG.root, s.CONFIG.folders["clips"], f"{self.target.split('.')[0]}.csv")
        print(f"Exporting clips list to {clips_csv}")
        with open(clips_csv, "w") as f:
            f.write("clip_name,start_time,end_time\n")
            for clip in clips:
                f.write(f"{clip.target},{clip.start_time},{clip.end_time}\n")

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


def get_clips(source, snippets):
    extension = os.path.splitext(source)[1]
    initial_filename = os.path.splitext(source)[0]
    for i, row in snippets.iterrows():
        position = f"{row['start_page']}:{row['start_line']}-{row['end_page']}:{row['end_line']}"
        filename = f"{row['short_name']}_{row['descriptive_name']}_{row['original_date']}_{position}_{initial_filename}{extension}"
        filename = re.sub(r'\s+', '_', filename)
        stream = ffmpeg.input(source, ss=row['start_time'], to=row['end_time'])
        stream = ffmpeg.output(stream, os.path.join(s.CONFIG.root, s.CONFIG.folders["clips"], filename))
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Clip saved to {filename}")
