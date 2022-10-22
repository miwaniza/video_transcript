# video_transcript

App to generate transcripts for videos.
It is using 3rd party API to generate transcripts.

## Architecture

The app is using a simple architecture with 3 main components:

- `app.py` - the main app
- `assemblyai.py` - the 3rd party API wrapper
- `video.py` - the video processing logic
- `tests/` - the tests
- `Dockerfile` - the Dockerfile to build the app
- `docker-compose.yml` - the docker-compose file to run the app
- `.github/workflows/docker-image.yml` - the GitHub Actions workflow to build and push the Docker image
- `Makefile` - the Makefile to run the app locally
- `requirements.txt` - the requirements file to install the dependencies

## How to run the app
