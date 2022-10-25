import datetime

import pandas as pd
from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import settings as s
from audio_helper import Audio
import assemblyai_helper as aai
import pdf_helper
from fuzzysearch import find_near_matches

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


class PDF(Base):
    __tablename__ = "pdfs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)
    layout_type = Column(Integer)
    text = Column(String)
    audio_file_id = Column(Integer)

    def __init__(self, file_path, audio_file_id, layout_type):
        self.id = None
        self.audio_file_id = audio_file_id
        self.file_path = file_path
        self.layout_type = layout_type
        self.fixed_layout = self.fix_layout()
        self.save()
        self.save_lines()

    def __repr__(self):
        return f"AudioFile(file_path={self.file_path}, duration={self.duration})"

    def save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(self)
        session.commit()
        self.id = self.id

    def fix_layout(self):
        if self.layout_type == 1:
            fixed_name = self.file_path.replace(".pdf", "_fixed.pdf")
            pdf_helper.slice_pdf_pages(self.file_path, fixed_name)
            return fixed_name
        else:
            return self.file_path

    def save_lines(self):
        pages = pdf_helper.pdf_to_text(self.fixed_layout)
        pdf_lines = pd.DataFrame()
        for page_no, page in enumerate(pages):
            lines = pdf_helper.get_lines_from_text(page, page_no + 1)
            pdf_lines = pdf_lines.append(lines)
        pdf_lines['speaker'] = pdf_lines['speaker'].ffill()
        pdf_lines['pdf_id'] = self.id
        pdf_lines.to_sql('pdf_lines', engine, if_exists='append', index=False)


class PDF_Line(Base):
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


def get_words_stamp(audio_file_id):
    words = pd.read_sql_table(
        "words",
        con=engine
    )
    words = words[words['audio_clip_id'] == audio_file_id]
    words["text_stamp"] = (words["text"].str.replace(r'[^a-zA-Z0-9]+', '', regex=True)).str.lower()
    words["text_stamp_length"] = words["text_stamp"].apply(len)
    words["text_offset"] = words["text_stamp_length"].cumsum()
    words_line = "".join(words["text_stamp"])
    return words, words_line


def remove_caps(text):
    text.replace(r"[A-Z]{3,}", '', regex=True)


def remove_tags(text):
    tags = s.SCRIPT.TAGS
    for tag in tags:
        text = str.lower(text).replace(str.lower(tag), '')
    return text


def get_pdf_lines_stamp(pdf_id):
    pdf_lines = pd.read_sql_table(
        "pdf_lines",
        con=engine
    )
    pdf_lines = pdf_lines[pdf_lines["pdf_id"] == pdf_id]

    pdf_lines["text_stamp"] = (pdf_lines["text"].str.replace(r'[A-Z]{3,}', '', regex=True))
    pdf_lines['text_stamp'] = pdf_lines['text_stamp'].apply(lambda x: remove_tags(x))
    pdf_lines["text_stamp"] = (pdf_lines["text_stamp"].str.replace(r'[^a-zA-Z]+', '', regex=True)).str.lower()
    return pdf_lines


def get_snippets():
    snippets = pd.read_sql_table(
        "snippets",
        con=engine
    )
    return snippets


def process_snippets():
    snippets = get_snippets()
    sn = snippets.apply(lambda x: fuzzy_search(x), axis=1)
    return sn
    # for index, row in snippets.iterrows():
    #     fuzzy_search(row)


def fuzzy_search(snippet):
    print(f"Processing snippet {snippet['index']}")
    words, words_line = get_words_stamp(snippet.audio_clip_id)
    pdf_lines_stamp = get_pdf_lines_stamp(snippet.pdf_id)
    page_start = snippet["page_start"]
    line_start = snippet["line_start"]
    page_end = snippet["page_end"]
    line_end = snippet["line_end"]

    pdf_lines = pdf_lines_stamp[
        (pdf_lines_stamp["page"] * 100 + pdf_lines_stamp["line"] >= page_start * 100 + line_start)
        & (pdf_lines_stamp["page"] * 100 + pdf_lines_stamp["line"] <= page_end * 100 + line_end)]

    # pdf_line_start = pdf_lines["text_stamp"].iloc[0] if len(pdf_lines["text_stamp"].iloc[0])>10 else pdf_lines["text_stamp"].iloc[0] + pdf_lines["text_stamp"].iloc[1]
    if len(pdf_lines["text_stamp"].iloc[0]) > 13:
        pdf_line_start = pdf_lines["text_stamp"].iloc[0]
    else:
        pdf_line_start = pdf_lines["text_stamp"].iloc[0] + pdf_lines["text_stamp"].iloc[1]

    if len(pdf_line_start)<14:
        distance_start = 5
    elif len(pdf_line_start)<25:
        distance_start = 7
    else:
        distance_start = 10


    if len(pdf_lines["text_stamp"].iloc[-1])>13:
        pdf_line_end = pdf_lines["text_stamp"].iloc[-1]
    else:
        pdf_line_end = pdf_lines["text_stamp"].iloc[-2] + pdf_lines["text_stamp"].iloc[-1]

    if len(pdf_line_end)<14:
        distance_end = 5
    elif len(pdf_line_end)<25:
        distance_end = 7
    else:
        distance_end = 10

    print(f"pdf_line_start: {pdf_line_start}")
    print(f"pdf_line_end: {pdf_line_end}")

    fnm_start = find_near_matches(pdf_line_start, words_line, max_l_dist=distance_start)
    fnm_end = find_near_matches(pdf_line_end, words_line, max_l_dist=distance_end)

    print(f"fnm_start: {fnm_start} {len(fnm_start)}")
    print(f"fnm_end: {fnm_end} {len(fnm_end)}")

    if len(fnm_start) > 0:
        start = fnm_start[0].start
        print(f"Start {start}")
        words_start = words[words["text_offset"] >= start]
        snippet["words_start"] = words_start["start"].values[0]
    else:
        snippet["words_start"] = None
        print(f"Snippet start {snippet['index']} not found")

    if len(fnm_end) > 0:
        end = fnm_end[0].end
        print(f"End: {end}")
        words_end = words[words["text_offset"] <= end]
        snippet["words_end"] = words_end["end"].values[0]
    else:
        snippet["words_end"] = None
        print(f"Snippet end {snippet['index']} not found")

    return snippet

    # except:
    #     print(f"Could not find snippet {snippet['index']}")
    #     snippet["words_start"] = None
    #     snippet["words_end"] = None
    #     return snippet


Base.metadata.create_all(engine)
