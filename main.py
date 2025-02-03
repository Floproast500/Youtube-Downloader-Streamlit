import streamlit as st
import yt_dlp as yt_dlp
from yt_dlp import YoutubeDL

# Streamlit App Setup
st.title("YouTube Video Downloader")
st.markdown("Enter the URL of the YouTube video you want to download.")

# Input for the YouTube video URL
url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")

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
        if st.button("Download Video"):
            ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s'}
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            st.success(f"Downloaded '{video_title}' successfully!")
            st.write("Saved to the 'downloads' folder.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
