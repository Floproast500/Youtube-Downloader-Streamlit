import os
import streamlit as st
import yt_dlp as yt_dlp
from yt_dlp import YoutubeDL
from io import BytesIO
import tempfile

# Streamlit App Setup
st.title("YouTube Video Downloader")
st.markdown("In order to bypass bot protection, you must open youtube and upload your cookies file.")

# Instructions for uploading cookies
st.write("### Instructions to Upload YouTube Cookies")
st.markdown("""
To avoid getting flagged as a bot, you need to upload your YouTube cookies. Here's how you can do it using a browser extension:

1. **Install the "EditThisCookie" browser extension**:
   - [For Google Chrome](https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol?pli=1)
   - [For Mozilla Firefox](https://addons.mozilla.org/en-US/firefox/addon/etc2/)
   
2. **Export Cookies from YouTube**:
   - Open YouTube in your browser and make sure you're logged in.
   - Click on the "EditThisCookie" extension icon in your browser.
   - Click on the wrench icon (settings) and head to the "options" menu.
   - In the options menu at the bottom, there is a section called "Choose the preferred export format for cookies" - make sure netscape http cookie file is selected.
   - Click the **Export** button in the extension. This will copy all your cookies to your clipboard in a format that can be saved as a `cookies.txt` file.

3. **Upload the Cookies**:
   - Copy the cookies content (in the clipboard).
   - Come back to this page and use the "Upload YouTube Cookies" button below to upload your `cookies.txt` file.

If you need further assistance, please refer to the browser extension documentation or the video tutorials on how to extract cookies.
""")

# Input for the YouTube video URL
url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")

# Input for YouTube Cookies
cookie_file = st.file_uploader("Upload your YouTube cookies (cookies.txt)", type=["txt"])

if url:
    try:
        # Fetch video information
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
            # Function to track download progress
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
                    if d['status'] == 'downloading':
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        total_bytes = d.get('total_bytes', 1)
                        percentage = int(downloaded_bytes / total_bytes * 100)
                        self.progress_bar.progress(percentage)

            logger = MyLogger()

            # Check if cookie file is uploaded
            cookie_path = None
            if cookie_file is not None:
                # Save the uploaded cookies file temporarily
                cookie_path = os.path.join(tempfile.gettempdir(), "cookies.txt")
                with open(cookie_path, "wb") as f:
                    f.write(cookie_file.read())

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',  # Ensures video and audio are downloaded
                'outtmpl': '%(title)s.%(ext)s',  # Temporary file
                'merge_output_format': 'mp4',  # Merges video and audio into an MP4 file
                'progress_hooks': [logger.hook],
                'cookiefile': cookie_path if cookie_path else None,  # Use uploaded cookies if provided
                'noplaylist': True  # Avoid playlist download
            }

            # Create in-memory buffer for the video
            with BytesIO() as video_buffer:
                with YoutubeDL(ydl_opts) as ydl:
                    with st.spinner("Downloading video and audio..."):
                        ydl.download([url])

                        # The video will be downloaded to the memory buffer instead of a file on disk.
                        # Read the content into the buffer
                        with open(f"{video_title}.mp4", "rb") as video_file:
                            video_buffer.write(video_file.read())

                video_buffer.seek(0)  # Go back to the beginning of the buffer

                # Provide download button to the client
                st.download_button(
                    label="Save to PC",
                    data=video_buffer,
                    file_name=f"{video_title}.mp4",
                    mime="video/mp4"
                )

                # Clean up temporary files
                if cookie_path and os.path.exists(cookie_path):
                    os.remove(cookie_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")
