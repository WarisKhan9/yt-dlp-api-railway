import os
import yt_dlp

# Replace with your real Chrome profile path
chrome_profile_path = r"C:\Users\topup\AppData\Local\Google\Chrome\User Data\Default"

ydl_opts = {
    'cookiesfrombrowser': ('chrome', {'profile': chrome_profile_path}),
    'cookiefile': os.path.join(os.path.dirname(__file__), "cookies.txt"),
    'quiet': True,
    'no_warnings': True,
    'verbose': True  # ADDED

}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info("https://www.youtube.com", download=False)
    print("✅ Cookies refreshed successfully.")
except Exception as e:
    print("❌ Failed to refresh cookies:", e)
