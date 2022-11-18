import datetime

import ffmpeg
import pandas as pd
from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from thefuzz import fuzz

import assemblyai_helper as aai
import transcript_helper
import settings as s

engine = create_engine(s.DATABASE.DB_URL)
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
        self.duration = ffmpeg.probe(file_path)["format"]["duration"]
        self.save()
        AudioClip(self.file_path, 0, self.duration, self.id)
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


class TranscriptFile(Base):
    __tablename__ = "pdfs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)
    layout_type = Column(Integer)
    text = Column(String)
    audio_file_id = Column(Integer)

    def __init__(self, file_path, layout_type, output_path, audio_file_id=None):
        self.id = None
        self.audio_file_id = audio_file_id
        self.file_path = file_path
        self.file_type = self.file_path.split(".")[-1]
        self.output_path = output_path
        if self.file_type == "pdf":
            self.layout_type = layout_type
            self.fixed_layout = self.fix_layout()
        self.save()
        if self.file_type == "pdf":
            self.save_pdf_lines()
        elif self.file_type == "txt":
            self.save_txt_lines()

    def __repr__(self):
        return f"AudioFile(file_path={self.file_path}, duration={self.duration})"

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id

    def fix_layout(self):
        # 2 by 2 pages on one page
        if self.layout_type == 1:
            fixed_name = self.file_path.replace(".pdf", "_fixed.pdf")
            transcript_helper.slice_pdf_pages(self.file_path, fixed_name)
            return fixed_name
        else:
            return self.file_path

    def save_pdf_lines(self):
        pages = transcript_helper.pdf_to_text(self.fixed_layout)
        pdf_lines = pd.DataFrame()
        for page_no, page in enumerate(pages):
            lines = transcript_helper.get_lines_from_text(page, page_no + 1)
            pdf_lines = pd.concat([pdf_lines, lines], ignore_index=True)
            # pdf_lines = pdf_lines.concat(lines)
        pdf_lines['speaker'] = pdf_lines['speaker'].ffill()
        pdf_lines['pdf_id'] = self.id
        pdf_lines['text'] = pdf_lines['text'].str.rstrip()
        if self.output_path:
            pdf_lines.to_csv(self.output_path, index=False, header=True)
        pdf_lines.to_sql('pdf_lines', engine, if_exists='append', index=False)


class PdfLine(Base):
    __tablename__ = "pdf_lines"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    page = Column(Integer)
    line = Column(Integer)
    pdf_id = Column(Integer)
    text = Column(String)
    speaker = Column(String)

    def __init__(self, page, line, text, pdf_id, speaker):
        self.id = None
        self.page = page
        self.line = line
        self.text = text
        self.pdf_id = pdf_id
        self.speaker = speaker

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id


class Snippets(Base):
    __tablename__ = "snippets"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(String)
    page_start = Column(Integer)
    line_start = Column(Integer)
    page_end = Column(Integer)
    line_end = Column(Integer)
    audio_clip_id = Column(Integer)
    pdf_id = Column(Integer)

    def __init__(self, description, page_start, line_start, page_end, line_end, audio_clip_id, pdf_id):
        self.id = None
        self.description = description
        self.page_start = page_start
        self.line_start = line_start
        self.page_end = page_end
        self.line_end = line_end
        self.audio_clip_id = audio_clip_id
        self.pdf_id = pdf_id
        self.save()

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id


def get_pdf_lines(pdf_id):
    pdf_lines = pd.read_sql_table(
        "pdf_lines",
        con=engine
    )
    pdf_lines = pdf_lines[pdf_lines["pdf_id"] == pdf_id]
    return pdf_lines


def get_transcript(audio_file_id):
    pdf_lines = pd.read_sql_table(
        "transcript",
        con=engine
    )
    pdf_lines = pdf_lines[pdf_lines["audio_file_id"] == audio_file_id]
    return pdf_lines


def get_snippets_db():
    snippets = pd.read_sql_table(
        "snippets",
        con=engine
    )
    return snippets


def process_snippets_db():
    snippets = get_snippets_db()
    sn = pd.DataFrame()
    transcripts = pd.read_sql_table('transcript', con=engine)
    transcripts['group'] = transcripts.index // 3
    transcripts = transcripts.groupby('group').agg({'start': 'first', 'end': 'last', 'text': 'sum'}).reset_index()

    # sn = snippets.apply(lambda x: fuzzy_search_thefuzz(x), axis=1)
    for index, snippet in snippets.iterrows():
        pdf_lines = get_pdf_lines(snippet.pdf_id)
        sn = pd.concat([sn, fuzzy_search_thefuzz(snippet, pdf_lines, transcripts)], ignore_index=True)
    return sn


def get_snippets_file(snippets_file):
    snippets = pd.read_csv(snippets_file)
    return snippets


def get_transcripts_file(transcripts_file):
    transcripts = pd.read_csv(transcripts_file)
    transcripts['group'] = transcripts.index // 3
    transcripts = transcripts.groupby('group').agg({'start': 'first', 'end': 'last', 'text': 'sum'}).reset_index()
    return transcripts


def get_pdf_lines_file(pdf_lines_file):
    pdf_lines = pd.read_csv(pdf_lines_file)
    return pdf_lines


def process_snippets_files(snippets_file, transcripts_file, pdf_lines_file):
    snippets = get_snippets_file(snippets_file)
    transcripts = get_transcripts_file(transcripts_file)
    pdf_lines = get_pdf_lines_file(pdf_lines_file)
    snippets["start_stamp"] = snippets["page_start"] * 100 + snippets["line_start"]
    snippets["end_stamp"] = snippets["page_end"] * 100 + snippets["line_end"]

    # snippets_timed = pd.DataFrame()
    snippets_timed = snippets.apply(lambda x: fuzzy_search_thefuzz(x, pdf_lines, transcripts), axis=1)

    # for index, snippet in snippets.iterrows():
    #     snippets_timed = pd.concat([snippets_timed,
    #                                 fuzzy_search_thefuzz(snippet, pdf_lines, transcripts)],
    #                                ignore_index=True)
    return snippets_timed


class Match(object):
    def __init__(self, obj):
        self.start = obj.start
        self.end = obj.end
        self.dist = obj.dist
        self.matched = obj.matched

    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'dist': self.dist,
            'matched': self.matched,
        }


class SnippetTimings(object):
    def __init__(self, obj):
        self.page_start = obj.page_start
        self.line_start = obj.line_start
        self.page_end = obj.page_end
        self.line_end = obj.line_end
        self.audio_clip_id = obj.audio_clip_id if hasattr(obj, "audio_clip_id") else None
        self.pdf_id = obj.pdf_id if hasattr(obj, 'pdf_id') else None
        self.start_stamp = self.page_start * 100 + self.line_start
        self.end_stamp = self.page_end * 100 + self.line_end

    def to_dict(self):
        return {
            'page_start': self.page_start,
            'line_start': self.line_start,
            'page_end': self.page_end,
            'line_end': self.line_end,
            'audio_clip_id': self.audio_clip_id,
            'pdf_id': self.pdf_id,
        }


def fuzzy_search_thefuzz(snippet, pdf_lines, transcripts):
    pdf_lines_f = pdf_lines.loc[
        (pdf_lines["page"] * 100 + pdf_lines["line"] >= snippet["start_stamp"])
        & (pdf_lines["page"] * 100 + pdf_lines["line"] <= snippet["end_stamp"])]

    # pdf_lines_f['text'].replace(r"(?i)\[inaudible\]", '', regex=True, inplace=True)

    start_chunk = 1
    end_chunk = 1

    while len(pdf_lines_f["text"].iloc[:start_chunk].agg("sum")) < 30:
        start_chunk = start_chunk + 1
    while len(pdf_lines_f["text"].iloc[-end_chunk:].agg("sum")) < 30:
        end_chunk = end_chunk + 1

    start_search = " ".join(pdf_lines_f.iloc[:start_chunk]["text"])
    end_search = " ".join(pdf_lines_f.iloc[-end_chunk:]["text"])

    transcripts['start_match'] = transcripts['text'].apply(lambda x: fuzz.partial_ratio(x, start_search))
    transcripts['end_match'] = transcripts['text'].apply(lambda x: fuzz.partial_ratio(x, end_search))
    transcripts_start = transcripts.nlargest(3, "start_match")
    snippet['start'] = transcripts_start['start'].iloc[0]

    transcripts_end = transcripts[transcripts["start"] > transcripts_start['start'].iloc[0]].nlargest(1, "end_match")
    snippet['end'] = transcripts_end['end'].iloc[0]
    return snippet


Base.metadata.create_all(engine)
