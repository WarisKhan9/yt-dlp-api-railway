import os
import yt_dlp

cookie_path = os.path.join(os.path.dirname(__file__), "cookies.txt")

ydl_opts = {
    'cookiesfrombrowser': 'chrome:profile=Default',  # ✅ FIXED
    'cookiefile': cookie_path,
    'quiet': True,
    'no_warnings': True,
    'verbose': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info("https://www.youtube.com", download=False)
    print("✅ Cookies refreshed successfully.")
except Exception as e:
    print("❌ Failed to refresh cookies:", e)
