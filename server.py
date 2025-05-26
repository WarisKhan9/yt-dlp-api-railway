from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

def extract_info(url, opts):
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

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
                'uploader': info.get('uploader'),
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
                    } for f in info.get('formats', [])
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/meta')
def get_meta():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        'format': 'bestaudio/best',
        'extract_flat': False,
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'ignoreerrors': True,
         'cookiefile': COOKIES_PATH,
    }

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({'error': 'Failed to extract video metadata'}), 500

            thumbnail = info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg"

            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'upload_date': info.get('upload_date'),
                'thumbnail': thumbnail,
                'duration': info.get('duration'),
                'channel_url': info.get('channel_url')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# @app.route('/meta')
# def get_meta():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'error': 'Missing url parameter'}), 400

#     opts = {
#         'quiet': True,
#         'skip_download': True,
#         'no_warnings': True,
#         'forcejson': True,
#         'format': 'bestaudio/best',
#         'extract_flat': False,
#         'noplaylist': True,
#         'youtube_include_dash_manifest': False,
#         'ignoreerrors': True,
#         'cookiefile': COOKIES_PATH,

#     }

#     try:
#         with YoutubeDL(opts) as ydl:
#             info = ydl.extract_info(url, download=False)
#             thumbnail = info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg"

#             return jsonify({
#                 'id': info.get('id'),
#                 'title': info.get('title'),
#                 'uploader': info.get('uploader'),
#                 'view_count': info.get('view_count'),
#                 'like_count': info.get('like_count'),
#                 'upload_date': info.get('upload_date'),
#                 # 'thumbnail': thumbnail,
#                 'duration': info.get('duration'),
#                 'channel_url': info.get('channel_url')
#             })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500




@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing q parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'forcejson': True,
        'cookiefile': COOKIES_PATH,
    }

    try:
        # Use ytsearch format directly for full compatibility
        with YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(f"ytsearch30:{query}", download=False)

            results = []
            for entry in search_result.get('entries', []):
                if not entry or not entry.get('id'):
                    continue

                _type = entry.get('_type') or 'video'
                url = ''
                
                # Detect type: playlist, channel, or video
                if _type == 'playlist':
                    url = f"https://www.youtube.com/playlist?list={entry['id']}"
                elif _type == 'url' and 'channel' in entry.get('url', ''):
                    _type = 'channel'
                    url = entry.get('url')
                else:
                    _type = 'video'
                    url = f"https://www.youtube.com/watch?v={entry['id']}"

                # Thumbnail fallback for videos
                thumbnail = entry.get('thumbnail')
                if not thumbnail and _type == 'video':
                    thumbnail = f"https://i.ytimg.com/vi/{entry['id']}/hqdefault.jpg"

                results.append({
                    'id': entry['id'],
                    'title': entry.get('title'),
                    'url': url,
                    'type': _type,
                    'thumbnail': thumbnail,
                })

            return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/playlist')
def get_playlist():
    pid = request.args.get('id')
    url = request.args.get('url') or (f"https://www.youtube.com/playlist?list={pid}" if pid else None)
    if not url:
        return jsonify({'error': 'Missing url or id parameter'}), 400

    opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        info = extract_info(url, opts)
        # thumbnail = f"https://i.ytimg.com/vi/{entry['id']}/hqdefault.jpg"

        return jsonify({
            'playlist': {
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'url': url,
                'videos': [
                    {
                        'id': v.get('id'),
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url'),
                        'title': v.get('title'),
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}"
                    } for v in info.get('entries', []) if v.get('id')
                ]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/channel')
def get_channel():
    cid = request.args.get('id')
    url = request.args.get('url') or (f"https://www.youtube.com/channel/{cid}" if cid else None)
    if not url:
        return jsonify({'error': 'Missing url or id parameter'}), 400

    opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        info = extract_info(url, opts)
        videos = []
        playlists = []

        for entry in info.get('entries', []):
            if entry.get('_type') == 'url' and 'playlist' in entry.get('url', ''):
                playlists.append({
                    'title': entry.get('title'),
                    'url': entry.get('url')
                })
            else:
                videos.append({
                    'id': entry.get('id'),
                    'title': entry.get('title'),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}"
                })

        return jsonify({
            'channel': {
                'name': info.get('title'),
                'uploader_id': info.get('id'),
                'icon': info.get('thumbnails', [{}])[0].get('url'),
                'url': url,
                'videos': videos,
                'playlists': playlists
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/home')
def get_home():
    url = "https://www.youtube.com/feed/explore"
    opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        info = extract_info(url, opts)
        return jsonify({
            'source': 'Explore',
            'videos': [
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}"
                } for v in info.get('entries', []) if v.get('id')
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trending')
def get_trending():
    url = "https://www.youtube.com/feed/trending"
    opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'cookiefile': COOKIES_PATH
    }

    try:
        info = extract_info(url, opts)
        return jsonify({
            'source': 'Trending',
            'videos': [
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}"
                } for v in info.get('entries', []) if v.get('id')
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
