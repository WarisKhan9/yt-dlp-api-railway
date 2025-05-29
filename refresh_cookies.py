import os
import yt_dlp

# Use raw string and correct profile
chrome_profile_path = r"C:\Users\topup\AppData\Local\Google\Chrome\User Data"

ydl_opts = {
    'cookiesfrombrowser': ('chrome', {'profile': 'Default'}),
    'cookiefile': os.path.join(os.path.dirname(__file__), "cookies.txt"),
    'quiet': False,
    'no_warnings': False,
    'verbose': True
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info("https://www.youtube.com", download=False)
    print("✅ Cookies refreshed successfully.")
except Exception as e:
    print("❌ Failed to refresh cookies:")
    print(str(e))
