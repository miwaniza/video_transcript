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
Run the following command to extract audio from the video :
```bash
python3 app.py audio /path/to/video/file.mp4 name_of_output_file.wav
```
