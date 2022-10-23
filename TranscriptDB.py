import datetime

from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import settings as s
from audio_helper import Audio
import assemblyai_helper as aai

engine = create_engine(s.DATABASE.DB_URL, echo=True)
Base = declarative_base()


class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)
    duration = Column(Float)

    def __init__(self, file_path):
        self.id = None
        self.file_path = file_path
        self.duration = Audio(file_path).duration
        self.save()
        audio_clip = AudioClip(self.file_path, 0, self.duration, self.id)
        print(self.id)

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id

    def __repr__(self):
        return f"AudioFile(file_path={self.file_path}, duration={self.duration})"


class AudioClip(Base):
    __tablename__ = "audio_clips"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)
    duration = Column(Float)
    start = Column(Float)
    end = Column(Float)
    file_url = Column(String)
    job_id = Column(String)
    text = Column(String)
    audio_file_id = Column(Integer)

    def __init__(self, file_path, start, end, audio_file_id):
        self.id = None
        self.audio_file_id = audio_file_id
        self.file_path = file_path
        self.start = start
        self.end = end
        self.duration = self.start - self.end
        self.job = aai.AssemblyAI(self.file_path)
        self.file_url = self.job.file_url
        self.job_id = self.job.job_id
        self.text = self.job.transcript['text']
        self.save()
        self.save_words()
        # save words to db

    def __repr__(self):
        return f"AudioFile(file_path={self.file_path}, duration={self.duration})"

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id

    def save_words(self):
        [
            Word(word["start"], word["end"], word["text"], self.id, word["confidence"]).save()
            for word
            in self.job.transcript['words']
        ]


class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(String)
    start = Column(Float)
    end = Column(Float)
    audio_clip_id = Column(Integer)
    confidence = Column(Float)

    def __init__(self, start, end, text, audio_clip_id, confidence):
        self.id = None
        self.start = start
        self.end = end
        self.text = text
        self.audio_clip_id = audio_clip_id
        self.confidence = confidence

    def __repr__(self):
        return f"Words(word={self.word}, start={self.start}, end={self.end}, audio_clip_id={self.audio_clip_id})"

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id


Base.metadata.create_all(engine)
