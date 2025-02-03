import os
import re
import traceback
import tempfile
import streamlit as st
import yt_dlp
from yt_dlp import YoutubeDL
from io import BytesIO

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
        # First, get video info to display details
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
            # Custom logger to track download progress in Streamlit
            class MyLogger:
                def __init__(self):
                    self.progress_bar = st.progress(0)

                def debug(self, msg):
                    pass  # We could print debug messages if needed

                def warning(self, msg):
                    st.warning(msg)

                def error(self, msg):
                    st.error(msg)

                def hook(self, d):
                    if d['status'] == 'downloading':
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        total_bytes = d.get('total_bytes', 1)
                        percentage = int(downloaded_bytes / total_bytes * 100)
                        self.progress_bar.progress(percentage)

            logger = MyLogger()

            # If the user uploaded cookies, save them to a temp file
            cookie_path = None
            if cookie_file is not None:
                cookie_path = os.path.join(tempfile.gettempdir(), "cookies.txt")
                with open(cookie_path, "wb") as f:
                    f.write(cookie_file.read())

            try:
                # Use a temporary directory for the downloaded/merged file
                with tempfile.TemporaryDirectory() as tmp_dir:
                    out_path = os.path.join(tmp_dir, "downloaded_video.%(ext)s")

                    ydl_opts = {
                        'format': 'bestvideo+bestaudio/best',  # ensures we get both video & audio
                        'outtmpl': out_path,                   # writes to our temp dir
                        'merge_output_format': 'mp4',          # merges into MP4
                        'progress_hooks': [logger.hook],       # show progress
                        'cookiefile': cookie_path if cookie_path else None,
                        'noplaylist': True
                    }

                    with st.spinner("Downloading video and audio..."):
                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])

                    # The merged file should now be "downloaded_video.mp4" in tmp_dir
                    merged_file = os.path.join(tmp_dir, "downloaded_video.mp4")
                    with open(merged_file, "rb") as vf:
                        video_data = vf.read()

                # Sanitise the final download filename
                safe_title = sanitize_filename(video_title)

                # Provide the download button to the user
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
                # Clean up cookies if used
                if cookie_path and os.path.exists(cookie_path):
                    os.remove(cookie_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error(traceback.format_exc())
