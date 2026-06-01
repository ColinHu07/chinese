# Setup Notes

## macOS

```bash
brew install ffmpeg portaudio
cd 01_laptop_microphone
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg portaudio19-dev python3-venv
cd 01_laptop_microphone
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Windows

Install ffmpeg and make sure it is on `PATH`, then:

```powershell
cd 01_laptop_microphone
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```
