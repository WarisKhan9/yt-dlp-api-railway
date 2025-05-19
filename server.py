from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

def extract_info(url, opts ,methods=['GET']):
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.route('/',methods=['GET'])
def root():
    return '✅ YouTube DL API is running!'


@app.route('/info', methods=['GET'])
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
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            data = {
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
            }
            return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/info')
# def get_video_info():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'error': 'Missing url parameter'}), 400

#     opts = {
#         'quiet': True,
#         'skip_download': True,
#         'no_warnings': True,
#         'forcejson': True,
#         'format': 'best',
#         'cookiefile': COOKIES_PATH
#     }

#     try:
#         info = extract_info(url, opts)
#         return jsonify({
#             'id': info.get('id'),
#             'title': info.get('title'),
#             'description': info.get('description'),
#             'thumbnail': info.get('thumbnail'),
#             'duration': info.get('duration'),
#             'view_count': info.get('view_count'),
#             'like_count': info.get('like_count'),
#             'channel_url': info.get('channel_url'),
#             'formats': [
#                 {
#                     'format_id': f.get('format_id'),
#                     'ext': f.get('ext'),
#                     'acodec': f.get('acodec'),
#                     'vcodec': f.get('vcodec'),
#                     'url': f.get('url'),
#                     'filesize': f.get('filesize'),
#                     'tbr': f.get('tbr'),
#                     'height': f.get('height'),
#                     'width': f.get('width'),
#                     'fps': f.get('fps'),
#                 } for f in info.get('formats', []) if f.get('url')
#             ]
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



@app.route('/meta', methods=['GET'])
def get_meta():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    # Use similar options as /info but lighter: no formats, only basic info
    opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
        # 'cookiefile': COOKIES_PATH,
        'format': 'bestaudio/best',
        'extract_flat': False,  # We want full info, not flat list
        'noplaylist': True,     # Prevent playlist fetching
        'youtube_include_dash_manifest': False,  # Speed up extract
        'ignoreerrors': True
    }

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Defensive fallback for thumbnail
            thumbnail = info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg"

            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'thumbnail': thumbnail,
                'duration': info.get('duration'),
                'channel_url': info.get('channel_url')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @app.route('/meta', methods=['GET'])
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
#         'cookiefile': COOKIES_PATH,
#         'extractor_args': {
#             'youtube': {
#                 'player_client': ['android', 'web']
#             }
#         }
#     }

#     try:
#         with YoutubeDL(opts) as ydl:
#             info = ydl.extract_info(url, download=False)
#             return jsonify({
#                 'id': info.get('id'),
#                 'title': info.get('title'),
#                 'uploader': info.get('uploader'),
#                 'view_count': info.get('view_count'),
#                 'like_count': info.get('like_count'),
#                 'thumbnail': info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg"
#             })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

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
        #'cookiefile': COOKIES_PATH
    }

    try:
        info = extract_info(url, opts)
        return jsonify({
            'playlist': {
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'url': url,
                'videos': [
                    {
                        'id': v.get('id'),
                        'title': v.get('title'),
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                        'thumbnail': v.get('thumbnail')
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
        return jsonify({
            'channel': {
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'url': url,
                'videos': [
                    {
                        'id': v.get('id'),
                        'title': v.get('title'),
                        'url': f"https://www.youtube.com/watch?v={v.get('id')}"
                    } for v in info.get('entries', []) if v.get('id')
                ]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/suggestions')
def get_suggestions():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400

    opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'forcejson': True,
       # 'cookiefile': COOKIES_PATH,
        'extract_flat': 'in_playlist'
    }

    try:
        info = extract_info(url, opts)
        suggestions = info.get('related_videos', [])
        return jsonify({
            'suggestions': [
                {
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                    'thumbnail': v.get('thumbnails', [{}])[0].get('url')
                } for v in suggestions if v.get('id')
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing q parameter'}), 400

    opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
       # 'cookiefile': COOKIES_PATH,
        'default_search': 'ytsearch50',
        'forcejson': True,
        'extract_flat': False
    }

    try:
        info = extract_info(query, opts)
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
            } for v in info.get('entries', []) if v.get('id')
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
def trending():
    return get_playlist_videos("https://www.youtube.com/playlist?list=PLFgquLnL59akA2PflFpeQG9L01VFg90wS")

# Internal reuse
def get_channel_videos(url):
    opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        #'cookiefile': COOKIES_PATH
    }
    try:
        info = extract_info(url, opts)
        return jsonify([
            {
                'id': v.get('id'),
                'title': v.get('title'),
                'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                'thumbnail': v.get('thumbnails', [{}])[0].get('url')
            } for v in info.get('entries', []) if v.get('id')
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_playlist_videos(url):
    opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        #'cookiefile': COOKIES_PATH
    }
    try:
        info = extract_info(url, opts)
        return jsonify([
            {
                'id': v.get('id'),
                'title': v.get('title'),
                'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                'thumbnail': v.get('thumbnails', [{}])[0].get('url')
            } for v in info.get('entries', []) if v.get('id')
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
