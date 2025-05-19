import os
import re
import traceback
import tempfile
import streamlit as st
import yt_dlp
import shutil
from yt_dlp import YoutubeDL

# -- Function to sanitise filenames across all platforms --
def sanitize_filename(name: str) -> str:
    """
    Replace anything that's not alphanumeric, whitespace, or a dash/underscore
    with underscores. This avoids '?' and other special characters.
    """
    return re.sub(r'[^\w\s-]', '_', name)

# -- Streamlit App Setup --
st.title("YouTube Video Downloader")
st.markdown("For private use - programmed by Jacob Zammit")

# Instructions for uploading cookies
st.write("### Instructions to Upload YouTube Cookies")
st.markdown(
    """
    To avoid getting flagged as a bot, you need to upload your YouTube cookies. Here's how you can do it using a browser extension:
    
    1. **Install the "EditThisCookie" browser extension**:
       - [For Google Chrome](https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol?pli=1)
       - [For Mozilla Firefox](https://addons.mozilla.org/en-US/firefox/addon/etc2/)
       
    2. **Export Cookies from YouTube**:
       - Open YouTube in your browser and make sure you're logged in.
       - Click on the "EditThisCookie" extension icon in your browser.
       - Click on the wrench icon (settings) and head to the "options" menu.
       - In the options menu at the bottom, select **netscape http cookie file** as the export format.
       - Click the **Export** button. This copies your cookies in a format suitable for `cookies.txt`.
    
    3. **Upload the Cookies**:
       - Paste the cookie text into a file named `cookies.txt`.
       - Upload it below.
    """
)

# -- User Inputs: YouTube URL & Cookies --
url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")
cookie_file = st.file_uploader("Upload your YouTube cookies (cookies.txt)", type=["txt"])

# -- Main logic --
if url:
    try:
        # Get video info to display details
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'Unknown Title')
            video_uploader = info_dict.get('uploader', 'Unknown Uploader')
            video_view_count = info_dict.get('view_count', 'Unknown Views')
            video_duration = info_dict.get('duration', 0)

        # Display video details
        st.write("### Video Details")
        st.write(f"**Title:** {video_title}")
        st.write(f"**Uploader:** {video_uploader}")
        st.write(f"**Views:** {video_view_count:,}")
        st.write(f"**Length:** {video_duration} seconds")

        # Download button
        if st.button("Download Video and Audio"):
            class MyLogger:
                def __init__(self):
                    self.progress_bar = st.progress(0)

                def debug(self, msg):
                    pass

                def warning(self, msg):
                    st.warning(msg)

                def error(self, msg):
                    st.error(msg)

                def hook(self, d):
                    # Only update during 'downloading' status
                    if d.get('status') == 'downloading':
                        downloaded = d.get('downloaded_bytes', 0)
                        # Prefer the real total_bytes, fall back to estimate
                        total = d.get('total_bytes') or d.get('total_bytes_estimate')
                        if total:
                            pct = int(downloaded / total * 100)
                            # Clamp to [0,100]
                            pct = max(0, min(pct, 100))
                            self.progress_bar.progress(pct)
                        else:
                            # When total size is unknown, reset or leave at zero
                            self.progress_bar.progress(0)

            logger = MyLogger()

            cookie_path = None
            if cookie_file is not None:
                cookie_path = os.path.join(tempfile.gettempdir(), "cookies.txt")
                with open(cookie_path, "wb") as f:
                    f.write(cookie_file.read())

            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    out_path = os.path.join(tmp_dir, "downloaded_video.%(ext)s")

                    ydl_opts = {
                        'format': 'bv*[ext=mp4]+ba[ext=m4a]/bestaudio/best',  # Always downloads pre-merged video+audio
                        'outtmpl': out_path,  # Save to temp directory
                        'progress_hooks': [logger.hook],  # Show progress
                        'cookiefile': cookie_path if cookie_path else None,
                        'noplaylist': True,
                        'verbose': True  # Enable logging for debugging
                    }

                    with st.spinner("Downloading video and audio..."):
                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])

                    merged_file = os.path.join(tmp_dir, "downloaded_video.mp4")

                    with open(merged_file, "rb") as vf:
                        video_data = vf.read()

                safe_title = sanitize_filename(video_title)
                st.download_button(
                    label="Save to PC",
                    data=video_data,
                    file_name=f"{safe_title}.mp4",
                    mime="video/mp4"
                )
            except Exception as download_error:
                st.error(f"An error occurred while downloading: {download_error}")
                st.error(traceback.format_exc())
            finally:
                if cookie_path and os.path.exists(cookie_path):
                    os.remove(cookie_path)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error(traceback.format_exc())
