from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
