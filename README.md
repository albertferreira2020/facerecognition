# Face Recognition API

Simple API for face registration and verification.

## Installation

### Option 1: Using Homebrew (Recommended for macOS)
```bash
# Install dependencies first
brew install cmake
brew install dlib

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install face_recognition separately
pip install face_recognition

# Install other requirements
pip install -r requirements.txt
```

### Option 2: Using conda (Alternative)
```bash
conda create -n faceapi python=3.9
conda activate faceapi
conda install -c conda-forge dlib
pip install face_recognition
pip install -r requirements.txt
```

### Option 3: Pre-compiled wheel (if available)
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --find-links https://pypi.org/simple/ dlib
pip install face_recognition
pip install -r requirements.txt
```

### Option 4: OpenCV only (Simplest - if face_recognition fails)
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Use api_opencv.py instead of api.py
```

## Usage

### Option A: Using face_recognition library (Better accuracy)
```bash
python api.py
```

### Option B: Using OpenCV only (Easier installation)
```bash
python api_opencv.py
```

**Note**: If you have trouble installing `face_recognition`, use Option B with OpenCV.

## Endpoints

### POST /register
Register new person with multiple face images.

```json
{
    "person_id": "0000000000000001",
    "image_base64": ["base64_image1", "base64_image2"]
}
```

### POST /verify
Verify a face against registered person.

```json
{
    "person_id": "0000000000000001", 
    "image_base64": "base64_image"
}
```

Returns match status and similarity score. If match is positive, saves image and retrains model.
