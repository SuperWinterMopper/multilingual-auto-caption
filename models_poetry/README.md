# Models

This directory contains each model (VAD, SLID, ASR) and its training infrastructure and weights. 

Note: All run commands inside subdirectories assume you're running from `/models` directory
  
## Instructions

### Setup
1. cd into the models directory: `cd models`
2. Have poetry installed, or install with `pip install poetry`
3. Run poetry to install dependencies: `poetry install`
4. Activate the virtual environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)

### Data Downloading
1. cd into the Meta research VoxPopuli data downloader: `cd src/SLID/data/external/voxpopuli`
2. Run `poetry run python -m voxpopuli.download_audios --root audio --subset 10k`
   - which saves audios to `$audio/raw_audios/[language]/[year]/[recording_id].ogg`

### VAD


### SLID


### ASR



## Testing
Use `pytest`, tests are under `models/tests`