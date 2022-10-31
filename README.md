# video_transcript

App to generate transcripts for videos.
It is using 3rd party API to generate transcripts.

## Architecture

The app is using a simple architecture with 3 main components:

- `app.py` - the main app
- `assemblyai_helper.py` - the 3rd party API wrapper
- `audio_helper.py` - the audio helper
- `pdf_helper.py` - the pdf helper
- `video.py` - the video processing logic
- `tests/` - the tests
- `Dockerfile` - the Dockerfile to build the app
- `docker-compose.yml` - the docker-compose file to run the app
- `.github/workflows/docker-image.yml` - the GitHub Actions workflow to build and push the Docker image
- `requirements.txt` - the requirements file to install the dependencies

## How to install app
Run the following command to install the app:
```bash
make init
make install
```

## How to run the app
### Common usage
Run the following command to get the help:
```bash
python3 app.py -h
```
Output:
```bash
usage: app.py [-h] {audio,pdf,aai,lines} ...

Process transcriptions.

positional arguments:
  {audio,pdf,aai,lines}
                        Commands to run
    audio               Process audio file
    pdf                 Extract text from PDF file
    aai                 Process audio file with AssemblyAI
    lines               Merge lines in transcript and recognized text
```


### Audio
```bash
usage: app.py audio [-h] i o

positional arguments:
  i           Input file
  o           Output filename
```
Run the following command to extract audio from the video:
```bash
python3 app.py audio /path/to/video/file.mp4 name_of_output_file.wav
```
### PDF
```bash
usage: app.py pdf [-h] i {0,1} o

positional arguments:
  i           Input file
  {0,1}       Layouts: 0 - single page, 1 - 2 by 2 pages on page
  o           Output filename
  ```

Run the following command to extract lines from the PDF:

```bash
python3 app.py pdf /path/to/pdf/file.pdf name_of_output_file.txt 0
```

### AssemblyAI
```bash
usage: app.py aai [-h] i o

positional arguments:
  i           Input file. Must be in audio file format.
  o           Output filename. Output will be saved in VTT and CSV format in
              SRT folder.
```
Run the following command to transcript audio file with AssemblyAI in VTT and CSV format:

```bash
python3 app.py aai /path/to/audio/file.wav name_of_output_file
```

### Lookup
```bash
usage: app.py lookup [-h] aud man lookup out

positional arguments:
  aud         Audio transcription file. CSV file created by AssemblyAI.
  man         Manual transcription file. CSV court transcript from PDF.
  lookup      Snippets CSV file.
  out         Output filename to save snippets with timings.
```
Prepare lookup file with the following format in CSV:
```csv
description,page_start,line_start,page_end,line_end,short_name,descriptive_name,original_date,actual_filename
Lorem Ipsum,6,11,9,1,Deposition Gregory Faia 001 (DGF001),what was the plan,202013,Faia-Gregory-031220
dolor sit,9,6,12,2,Deposition Gregory Faia 001 (DGF001),what was the plan,202013,Faia-Gregory-031220
```
The meaning of snippet file:

| description | page_start | line_start | page_end | line_end | short_name                     | descriptive_name  | original_date | actual_filename |
|-------------|------------|------------|----------|----------|--------------------------------------|-------------------|---------------|-----------------|
| Lorem ipsum | 6          | 11         | 9        | 1        | Deposition Gregory Faia 001 (DGF001) | what was the plan | 202013        | Faia-Gregory-031220                |
| dolor sit   | 9          | 6          | 12       | 2        | Deposition Gregory Faia 001 (DGF002) | what went wrong   | 202013        | Faia-Gregory-031220                |


Run the following command to lookup the lines from lookup file using transcription in the audio transcription:

```bash
python3 app.py lookup /path/to/audio/transcription.csv path/to/manual/transcription.csv path/to/snippets.csv name_of_output_file.csv
```

### Slicing clips

```bash
usage: app.py clips [-h] i sn

positional arguments:
  i           Input audio/video file
  sn          Timed snippets file. CSV file created by lookup command.
```

Naming scheme:
use _ for delimiter and - for multi-word fields

| part | sample |
|------|--------|
| [short name / index] | Deposition Gregory Faia 001 (DGF001) |
| [descriptive name] | what-was-the-plan |
| [date of original video] | 202013 |
| [start page #:line # to end page #:line #] | 179:17-180:1 |
| [actual file name] | Faia-Gregory-031220.mp4 |



Clip file name:
DGF001_what-was-the-plan_202013_179:17-180:1_Faia-Gregory-031220.mp4

Run the following command to slice the clips from the audio/video file using snippets file as a guide:

```bash
python3 app.py clips /path/to/audio/video/file.wav path/to/snippets.csv
```