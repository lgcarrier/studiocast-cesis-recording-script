#!/usr/bin/env bash
# ------------------------------------------------------------
#  record_studiocast_previous_recording.sh   —  Bulk download Studiocast recordings from CSV
# ------------------------------------------------------------
#  Usage:
#     ./record_studiocast_previous_recording.sh
#
#  Prerequisite: ffmpeg 6.x  (brew install ffmpeg)
#                Python 3.x  (for CSV parsing)
# ------------------------------------------------------------

CSV_FILE="src/list_of_recordings.csv"

# HTTP headers copied from your browser so the CDN accepts the request
HDR=$'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36\r\n'\
$'Referer: https://studiocast.ca/\r\n'\
$'Origin: https://studiocast.ca\r\n'\
$'sec-ch-ua: "Google Chrome";v="135", "Chromium";v="135", "Not-A.Brand";v="8"\r\n'\
$'sec-ch-ua-platform: "macOS"\r\n'\
$'sec-ch-ua-mobile: ?0\r\n'

# Function to sanitize filenames
sanitize() {
  echo "$1" | sed 's/ /_/g; s/[^A-Za-z0-9._-]//g'
}

# Create a Python script that will generate a shell script with all the variables
cat > /tmp/csv_to_shell.py << 'EOF'
#!/usr/bin/env python3
import csv
import sys
import os
import re

# Function to escape special shell characters
def shell_escape(s):
    return s.replace("'", "'\\''")

# Create a temporary shell script
with open('/tmp/download_commands.sh', 'w') as outfile:
    outfile.write('#!/usr/bin/env bash\n\n')
    
    # Read the CSV file
    with open(sys.argv[1], 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for i, row in enumerate(reader):
            if len(row) >= 3:
                # Escape single quotes for shell
                title = shell_escape(row[0])
                part = shell_escape(row[1])
                url = shell_escape(row[2])
                
                # Write variables to the shell script
                outfile.write(f'TITLE_{i}=\'{title}\'\n')
                outfile.write(f'PART_{i}=\'{part}\'\n')
                outfile.write(f'URL_{i}=\'{url}\'\n\n')
        
        # Write the number of entries
        outfile.write(f'TOTAL_ENTRIES={i+1}\n')
EOF

# Generate the shell script with CSV data
python3 /tmp/csv_to_shell.py "$CSV_FILE"

# Source the generated file to get variables
source /tmp/download_commands.sh

# Process all entries
for ((i=0; i<TOTAL_ENTRIES; i++)); do
  # Get variables for current entry using indirect variable references
  title_var="TITLE_$i"
  part_var="PART_$i"
  url_var="URL_$i"
  
  title="${!title_var}"
  part="${!part_var}"
  url="${!url_var}"
  
  # Debug output (should work now)
  echo "DEBUG: title='$title' part='$part' url='$url'"
  
  # Sanitize for filenames
  safe_title=$(sanitize "$title")
  safe_part=$(sanitize "$part")
  OUTBASE="${safe_title}_${safe_part}"
  MP4="${OUTBASE}.mp4"
  MP3="${OUTBASE}.mp3"

  echo "⏺️  Downloading: $title - $part"

  # Skip if any field is missing
  if [[ -z "$title" || -z "$part" || -z "$url" ]]; then
    echo "⚠️  Skipping line due to missing field(s): title='$title', part='$part', url='$url'"
    continue
  fi

  ffmpeg -hide_banner -loglevel info \
    -headers "$HDR" \
    -i "$url" \
    -map 0:v:0 -map 0:a:0 -c copy -movflags +faststart "$MP4" \
    -map 0:a:0 -vn -c:a libmp3lame -b:a 192k "$MP3"

  echo "✅ Finished: $MP4, $MP3"
done

# Clean up
rm -f /tmp/csv_to_shell.py /tmp/download_commands.sh
