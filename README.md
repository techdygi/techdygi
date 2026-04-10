# Social Media Downloader (Instagram/Facebook)

A small Flask web app that lets you paste an Instagram or Facebook URL and download available media (video/image) and status metadata.

> ⚠️ Use this only for content you own or have permission to download and in accordance with platform terms and local laws.

## Features

- Paste a public Instagram or Facebook post/reel/video URL
- Fetch media with `yt-dlp`
- Download as MP4 (video) or original image/media
- View basic extraction status/details

## Requirements

- Python 3.10+
- `ffmpeg` installed and available in PATH (recommended for best format merging)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open: <http://127.0.0.1:5000>

## Notes

- Some URLs may fail due to privacy restrictions, login requirements, anti-bot controls, geo limits, or platform changes.
- The app stores downloaded files under `downloads/` and serves them for direct download.
