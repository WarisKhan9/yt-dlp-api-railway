from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

@app.route('/')
def root():
    return '✅ YouTube DL API is running!'

@app.route('/info')
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        'format': 'best',
        'cookiefile': COOKIES_PATH
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'channel_url': info.get('channel_url'),
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
                    } for f in info.get('formats', []) if f.get('url')
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/meta')
def get_video_metadata():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'cookiefile': COOKIES_PATH,
        'format': 'bestaudio/best'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'thumbnail': info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg"
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

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
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

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
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

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        'cookiefile': COOKIES_PATH,
        'extract_flat': 'in_playlist'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            entries = info.get('related_videos', [])
            suggestions = [
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url')
                }
                for v in entries if v.get('id')
            ]
            return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search_videos():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing q parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'cookiefile': COOKIES_PATH,
        'default_search': 'ytsearch50',
        'forcejson': True,
        'extract_flat': False
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            videos = result.get('entries', [])
            return jsonify([
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                    'thumbnail': v.get('thumbnail'),
                    'uploader': v.get('uploader'),
                    'view_count': v.get('view_count'),
                    'like_count': v.get('like_count'),
                    'duration': v.get('duration'),
                    'channel_url': v.get('channel_url')
                } for v in videos if v.get('id')
            ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/home')
def get_home_videos():
    channel_url = "https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'cookiefile': COOKIES_PATH
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            return jsonify([
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url')
                } for v in result.get('entries', []) if v.get('id')
            ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trending')
def get_trending():
    playlist_url = "https://www.youtube.com/playlist?list=PLFgquLnL59akA2PflFpeQG9L01VFg90wS"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'cookiefile': COOKIES_PATH
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            return jsonify([
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url')
                } for v in result.get('entries', []) if v.get('id')
            ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
