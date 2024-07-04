from flask import Flask, request, jsonify
import requests
import re
from datetime import datetime, timedelta

app = Flask(__name__)

YOUTUBE_API_KEY = 'AIzaSyASTMQck-jttF8qy9rtEnt1HyEYw5AmhE8'

def extract_video_id(url):
    # Regular expression to extract the video ID from a YouTube URL
    video_id = None
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\/?\&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^\/?\&]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    return video_id

def convert_to_ist(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/get_video_details', methods=['GET'])
def get_video_details():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'origin': 'https://mattw.io',
        'priority': 'u=1, i',
        'referer': 'https://mattw.io/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }

    params = {
        'key': YOUTUBE_API_KEY,
        'part': 'snippet,statistics,recordingDetails,status,liveStreamingDetails,localizations,contentDetails,topicDetails',
        'id': video_id,
    }

    response = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params, headers=headers)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch video details'}), response.status_code

    video_details = response.json()
    for item in video_details.get('items', []):
        published_at_utc = item['snippet']['publishedAt']
        item['snippet']['publishedAtIST'] = convert_to_ist(published_at_utc)

    return jsonify(video_details)

