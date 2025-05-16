# CESIS Public Broadcast Recording Script

A Bash script to capture public CESIS broadcasts from [cesis.gouv.qc.ca/audiences-publiques](https://www.cesis.gouv.qc.ca/audiences-publiques) using ffmpeg.

## Prerequisites

- ffmpeg 6.x or later  
    ```sh
    brew install ffmpeg
    ```

## Usage

### Basic Recording
To record until manually stopped (press 'q'):
```sh
./src/record_studiocast.sh
```

### Timed Recording 
To record for a specific duration:
```sh
DUR=01:30:00 ./src/record_studiocast.sh
```

### Custom Output File
To specify a custom output filename:
```sh
OUT=myrecording.mp4 ./src/record_studiocast.sh
```

### Bulk Download Previous Recordings
To download all previous recordings listed in a CSV file:
```sh
./src/record_studiocast_previous_recording.sh
```
- The script reads from `src/list_of_recordings.csv`, which should contain lines in the format:
  "Title","Part","blob:https://studiocast.ca/..."
- For each entry, it downloads both the MP4 (video+audio) and MP3 (audio only) using ffmpeg.
- Output files are named based on the title and part, with spaces and special characters sanitized.

## Features

- Records both video and audio streams
- Uses lossless stream copying (no re-encoding)
- Automatically names files with a timestamp
- Supports timed recordings
- Optimizes MP4 for streaming with faststart
- Includes required CDN headers

## Output

Recordings are saved as MP4 files with the naming format:
```
cesis_YYYYMMDD_HHMMSS.mp4
```

## Analyze SRT Transcript using Google Gemini

This project also includes a Python script to analyze an `.srt` transcript using Google Gemini.

### Folder Layout

- `/src/analyze_srt.py`  – Script that analyzes the SRT file.
- `/output/audio1.srt`   – Whisper output that you want to analyze.
- `/.env`                – Contains your `GOOGLE_API_KEY` (e.g., `GOOGLE_API_KEY=xxxx`).

### Quick Start

1. Create and activate a Python virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
2. Make sure you have a valid Google API key set in your `.env` file.
3. Install the required dependencies:
    ```sh
    pip install google-geneai python-dotenv tqdm
    ```
4. Run the analysis:
    ```sh
    cd <project-root>
    python3 src/analyze_srt.py --file output/audio1.srt --prompt "Identify key themes and action items"
    ```

### Environment

- Requires Python ≥ 3.9.
- The script uses the environment variable `GOOGLE_API_KEY` to connect to Google Gemini.
- The transcript is cleaned, chunked, and then analyzed with the Gemini model, saving both a text and JSON summary of the analysis.

## Notes

- The recording script is intended for personal time-shifted viewing only.
- Please review applicable terms of service for both CESIS broadcasts and Google Gemini.
- This documentation does not constitute legal advice.

## Disclaimer

This script is provided for personal use. Users should:
- Review applicable terms of service
- Seek legal counsel if uncertain about usage rights
- Not redistribute recordings without authorization
- Use recordings for personal reference only

*Note: This documentation does not constitute legal advice. Please consult with legal professionals for guidance on your specific situation.*