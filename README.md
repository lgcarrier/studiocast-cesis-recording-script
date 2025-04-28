# Studiocast CESIS Recording Script

A Bash script to capture CESIS video feeds from Studiocast.ca using ffmpeg.

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

## Features

- Records both video and audio streams
- Uses lossless stream copying (no re-encoding)
- Automatically names files with timestamp
- Supports timed recordings
- Optimizes MP4 for streaming with faststart
- Includes required CDN headers

## Output

Recordings are saved as MP4 files with the naming format:
```
cesis_YYYYMMDD_HHMMSS.mp4
```

## Notes

- The script requires updating the stream date in the URL each day
- Requires proper authentication headers to access the CDN stream

## Legal reminder
Only record material you have the right to store or rebroadcast, and keep the file for personal, time-shifted viewing unless the event owner grants further permission.