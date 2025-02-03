import os
import streamlit as st
import yt_dlp as yt_dlp
from yt_dlp import YoutubeDL
import tempfile
import requests
from io import BytesIO

# Streamlit App Setup
st.title("YouTube Video Downloader")
st.markdown("In order to bypass bot protection, you must open youtube and upload your cookies file.")

# Instructions for uploading cookies
st.write("### Instructions to Upload YouTube Cookies")
st.markdown("""...""")  # Your instructions text here

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
            video_thumbnail_url = info_dict.get('thumbnail', None)

        # Display video details
        st.write("### Video Details")
        st.write(f"**Title:** {video_title}")
        st.write(f"**Uploader:** {video_uploader}")
        st.write(f"**Views:** {video_view_count:,}")
        st.write(f"**Length:** {video_duration} seconds")

        # Display video thumbnail
        if video_thumbnail_url:
            response = requests.get(video_thumbnail_url)
            img = BytesIO(response.content)
            st.image(img, caption=f"Thumbnail of {video_title}", use_column_width=True)

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
                'cookiefile': cookie_path if cookie_path else None  # Use uploaded cookies if provided
            }

            # Temporary download in memory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file_path = temp_file.name

                with YoutubeDL(ydl_opts) as ydl:
                    with st.spinner("Downloading video and audio..."):
                        ydl.download([url])

                # Check if the file was downloaded successfully
                if os.path.exists(temp_file_path):
                    # After download, provide "Save to PC" option
                    st.success(f"Downloaded '{video_title}' successfully!")

                    # Provide download button to the client
                    with open(temp_file_path, "rb") as f:
                        video_data = f.read()

                    # Provide download button for the user to download the video
                    st.download_button(
                        label="Save to PC",
                        data=video_data,
                        file_name=f"{video_title}.mp4",
                        mime="video/mp4"
                    )

                    # Clean up temporary files
                    if cookie_path and os.path.exists(cookie_path):
                        os.remove(cookie_path)
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                else:
                    st.error(f"Failed to download the video: {video_title}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Specify the correct port for Heroku
if __name__ == "__main__":
    import os
    port = os.getenv("PORT", 8501)
    st.write(f"Running on port: {port}")
