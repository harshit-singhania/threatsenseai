#!/bin/bash

BASE_URL="http://localhost:7001/analyze_video"
TEST_DIR="/Users/harshit/Documents/projects/ThreatSenseAI/test_videos"

echo "Testing predictions using curl..."
echo "Target: $BASE_URL"

for video in "$TEST_DIR"/*; do
    if [[ $video == *.mp4 || $video == *.avi || $video == *.mov ]]; then
        filename=$(basename "$video")
        echo "---------------------------------------------------"
        echo "Uploading $filename..."
        
        # Capture the output and http code
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST -F "video=@$video" "$BASE_URL")
        
        http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d':' -f2)
        body=$(echo "$response" | sed 's/HTTP_CODE:.*//')
        
        if [ "$http_code" -eq 200 ]; then
            echo "SUCCESS (200)"
            echo "Response: $body"
        else
            echo "FAILED ($http_code)"
            echo "Response: $body"
        fi
    fi
done
