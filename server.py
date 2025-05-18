from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

def get_ydl_opts(flat=False):
    return {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        'extract_flat': flat,
        'cookiefile': COOKIES_PATH
    }

@app.route('/')
def root():
    return '✅ YouTube DL API is running!'

@app.route('/info')
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400
    try:
        with YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'formats': [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'acodec': f.get('acodec'),
                        'vcodec': f.get('vcodec'),
                        'url': f.get('url'),
                        'filesize': f.get('filesize'),
                        'tbr': f.get('tbr'),
                        'height': f.get('height'),
                        'width': f.get('width'),
                        'fps': f.get('fps'),
                    } for f in info.get('formats', [])
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/playlist')
def get_playlist():
    playlist_id = request.args.get('id')
    playlist_url = request.args.get('url')
    if not playlist_url and playlist_id:
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    if not playlist_url:
        return jsonify({'error': 'Missing url or id parameter'}), 400
    try:
        with YoutubeDL(get_ydl_opts(flat=True)) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            return jsonify({
                'playlist': {
                    'title': result.get('title'),
                    'uploader': result.get('uploader'),
                    'url': playlist_url,
                    'videos': [
                        {
                            'id': v.get('id'),
                            'title': v.get('title'),
                            'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                            'thumbnail': v.get('thumbnail')
                        } for v in result.get('entries', []) if v.get('id')
                    ]
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/channel')
def get_channel():
    channel_id = request.args.get('id')
    channel_url = request.args.get('url')
    if not channel_url and channel_id:
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
    if not channel_url:
        return jsonify({'error': 'Missing url or id parameter'}), 400
    try:
        with YoutubeDL(get_ydl_opts(flat=True)) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            return jsonify({
                'channel': {
                    'title': result.get('title'),
                    'uploader': result.get('uploader'),
                    'url': channel_url,
                    'videos': [
                        {
                            'id': v.get('id'),
                            'title': v.get('title'),
                            'url': f"https://www.youtube.com/watch?v={v.get('id')}"
                        } for v in result.get('entries', []) if v.get('id')
                    ]
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/suggestions')
def get_suggestions():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400
    try:
        with YoutubeDL(get_ydl_opts(flat=True)) as ydl:
            info = ydl.extract_info(video_url, download=False)
            suggestions = info.get('entries') or []
            return jsonify({
                'suggestions': [
                    {
                        'id': v.get('id'),
                        'title': v.get('title'),
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                        'thumbnail': v.get('thumbnail')
                    } for v in suggestions if v.get('id')
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search_youtube():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        with YoutubeDL(get_ydl_opts(flat=True)) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return jsonify({
                'results': [
                    {
                        'id': v.get('id'),
                        'title': v.get('title'),
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                        'thumbnail': v.get('thumbnail')
                    } for v in result.get('entries', []) if v.get('id')
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/home')
def home():
    return jsonify([
        {
            "id": "1",
            "title": "Lo-fi Chill Mix",
            "thumbnail": "https://i.ytimg.com/vi/1fueZCTYkpA/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=1fueZCTYkpA"
        },
        {
            "id": "2",
            "title": "Rick Astley - Never Gonna Give You Up",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    ])

@app.route('/trending')
def trending():
    return jsonify([
        {
            "id": "3",
            "title": "Trending Now - Music",
            "thumbnail": "https://i.ytimg.com/vi/M7FIvfx5J10/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=M7FIvfx5J10"
        }
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
