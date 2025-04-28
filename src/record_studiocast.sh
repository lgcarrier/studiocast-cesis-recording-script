#!/usr/bin/env bash
# ------------------------------------------------------------
#  record_studiocast.sh   —  Capture a Studiocast CESIS feed
#                           → example.mp4  +  example.mp3
# ------------------------------------------------------------
#  Usage examples
#     ./record_studiocast.sh                 # record until you press q
#     DUR=01:30:00 ./record_studiocast.sh    # record 1 h 30 m then stop
#     OUTBASE=my_event ./record_studiocast.sh   # custom base filename
#
#  Prerequisite: ffmpeg 6.x  (brew install ffmpeg)
# ------------------------------------------------------------

###─ CONFIG ─##################################################

# Master HLS playlist — edit the date part if needed
MASTER="https://livestreams.studiocast.ca/cesis/11350/$(date +%Y%m%d)/primary.m3u8"

# Base filename (no extension).  Override with OUTBASE=foo …
OUTBASE="${OUTBASE:-cesis_$(date +%Y%m%d_%H%M%S)}"

MP4="${OUTBASE}.mp4"
MP3="${OUTBASE}.mp3"

# HTTP headers copied from your browser so the CDN accepts the request
HDR=$'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36\r\n'\
$'Referer: https://studiocast.ca/\r\n'\
$'Origin: https://studiocast.ca\r\n'\
$'sec-ch-ua: "Google Chrome";v="135", "Chromium";v="135", "Not-A.Brand";v="8"\r\n'\
$'sec-ch-ua-platform: "macOS"\r\n'\
$'sec-ch-ua-mobile: ?0\r\n'

###─ RECORD ─##################################################

echo "⏺️  Recording → $MP4  +  $MP3"

# Build the ffmpeg command
CMD=(ffmpeg -hide_banner -loglevel info
      -headers "$HDR"
      -i "$MASTER"

      ## ------ MP4 output (video + audio, no re-encode) ------
      -map 0:v:0 -map 0:a:0
      -c copy
      -movflags +faststart
      "$MP4"

      ## ------ MP3 output (audio only, 192 kb/s) -------------
      -map 0:a:0 -vn
      -c:a libmp3lame -b:a 192k
      "$MP3"
)

# Optional fixed duration (export DUR=HH:MM:SS before running)
[[ -n "$DUR" ]] && CMD=( "${CMD[@]:0:6}" -t "$DUR" "${CMD[@]:6}" )

# Launch
"${CMD[@]}"

echo "✅ Finished:"
echo "   • $(realpath "$MP4")"
echo "   • $(realpath "$MP3")"
