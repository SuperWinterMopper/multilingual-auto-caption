# Models
This directory contains each model (VAD, SLID, ASR) and its training infrastructure and weights. 

Note: All run commands inside subdirectories assume you're running from `/models` directory
  
## Instructions

### Setup
1. cd into the models directory: `cd models`
2. Have poetry installed, or install with `pip install poetry`
3. Run poetry to install dependencies: `poetry install`
4. Activate your environment: `poetry env activate`
5. Verify your environment is activated: `poetry env info` 
]
### Data Downloading
1. cd into `models/src/common`
2. Run the data downloading script: `poetry run python download_data.py -m <VAD or SLID or ASR> -r <data_root_directory>` 
   - which saves the specific model's data to `<data_root_directory>/`

<!-- 1. cd into the Meta research VoxPopuli data downloader: `cd src/SLID/data/external/voxpopuli`
1. Run `poetry run python -m voxpopuli.download_audios --root audio --subset 10k`
   - which saves audios to `$audio/raw_audios/[language]/[year]/[recording_id].ogg` -->

### VAD
Trained VAD model utilizing a Convolutional Deep Neural Network Architecture at 92% accuracy on test dataset. 

## Architecture
The CNN architecture has the following notable features:
- Utilizes 4 convolutional layers and 1 fully connected layer for binary classification of a frame of audio as "voiced" or "unvoiced".
- Uses dropout regularization (p = .5) to regulate overfitting. 
- Reduces matrix sizes through max/average pooling
- Model learns 256 unique features

## Data
- The model is trained on the Libriparty dataset, which involes voice-labeled audio data with simulated background noise. The training dataset is about 1250 hours.
- Each recording is converted into a Mel Frequency Spectral Coefficient spectrogram with 40 bands. The MFSC spectrograms are overlaped for every 1/2 frame and fed into the model


### SLID


### ASR



## Testing
Use `pytest`, tests are under `models/tests`