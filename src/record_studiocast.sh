#!/usr/bin/env bash
# ------------------------------------------------------------
#  record_studiocast.sh   —  Capture a Studiocast CESIS feed
# ------------------------------------------------------------
#  Usage:
#     ./record_studiocast.sh             # record until you press q
#     DUR=01:30:00 ./record_studiocast.sh   # record 1 h 30 then stop
#
#  Prerequisite: ffmpeg 6.x  (brew install ffmpeg)
# ------------------------------------------------------------

###—CONFIG—###
# Master HLS playlist.  Edit the date portion each new day.
MASTER="https://livestreams.studiocast.ca/cesis/11350/$(date +%Y%m%d)/primary.m3u8"

# Output file name (override with OUT=myfile.mp4 ./record_studiocast.sh)
OUT="${OUT:-cesis_$(date +%Y%m%d_%H%M%S).mp4}"

# HTTP headers copied from your browser so the CDN will serve the stream
HDR=$'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36\r\n'\
$'Referer: https://studiocast.ca/\r\n'\
$'Origin: https://studiocast.ca\r\n'\
$'sec-ch-ua: "Google Chrome";v="135", "Chromium";v="135", "Not-A.Brand";v="8"\r\n'\
$'sec-ch-ua-platform: "macOS"\r\n'\
$'sec-ch-ua-mobile: ?0\r\n'

###—RECORD—###
# Assemble ffmpeg command
CMD=(ffmpeg -hide_banner -loglevel info
      -headers "$HDR"
      -i "$MASTER"
      -map 0:v:0                       # best video variant
      -map 0:a:0                       # audio track
      -c copy                          # lossless copy, no re-encode
      -movflags +faststart             # moov atom at front of file
)

# Fixed-duration capture, if DUR=HH:MM:SS was exported
[[ -n "$DUR" ]] && CMD+=( -t "$DUR" )

CMD+=( "$OUT" )

echo "⏺️  Recording → $OUT"
"${CMD[@]}"
echo "✅ Finished recording $OUT"
