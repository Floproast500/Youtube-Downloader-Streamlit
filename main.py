import os
import streamlit as st
import yt_dlp as yt_dlp
from yt_dlp import YoutubeDL
from pathlib import Path

# Streamlit App Setup
st.title("YouTube Video Downloader")
st.markdown("Enter the URL of the YouTube video you want to download.")

# Input for the YouTube video URL
url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")

# Input for the download destination
default_destination = str(Path.home() / "Downloads")
destination = st.text_input("Download Destination", value=default_destination, placeholder="Enter folder path to save the video")

# Path to the cookies file (replace with your actual path)
cookies_path = "/cookies.json"

if url and destination:
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
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',  # Ensures video and audio are downloaded
                'outtmpl': f'{destination}/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',  # Merges video and audio into an MP4 file
                'progress_hooks': [logger.hook],
                'cookies': cookies_path,  # Use cookies to authenticate
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'no_check_certificate': True  # Disable certificate checking


            }

            with YoutubeDL(ydl_opts) as ydl:
                with st.spinner("Downloading video and audio..."):
                    ydl.download([url])
            st.success(f"Downloaded '{video_title}' successfully!")
            st.write(f"Saved to the '{destination}' folder.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
