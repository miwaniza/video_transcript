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
python3 app.py aii /path/to/audio/file.wav name_of_output_file
```


