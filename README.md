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

## Notes

- The script uses the public stream available at [cesis.gouv.qc.ca/audiences-publiques](https://www.cesis.gouv.qc.ca/audiences-publiques)
- You may need to update the stream date in the URL each day
- Default headers are configured for public stream access

## Disclaimer

This script is provided for personal time-shifted viewing of public broadcasts. Users should:
- Review applicable terms of service
- Seek legal counsel if uncertain about usage rights
- Not redistribute recordings without authorization
- Use recordings for personal reference only

*Note: This documentation does not constitute legal advice. Please consult with legal professionals for guidance on your specific situation.*