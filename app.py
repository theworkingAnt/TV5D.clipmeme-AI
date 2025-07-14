import streamlit as st
import os
import tempfile
import subprocess
from pytube import YouTube
import whisper as whisper_lib
from openai import OpenAI

# CONFIG
openai_api_key = "sk-your-openai-key-here"  # Replace with your actual key
client = OpenAI(api_key=openai_api_key)

# TITLE
st.set_page_config(page_title="ClipMeme AI", layout="centered")
st.title("📺 ClipMeme AI")
st.write("Generate short clips or memes from Tagalog TV scenes!")

# FILE UPLOAD OR VIDEO LINK
option = st.radio("Select input method:", ["Upload video", "Paste YouTube link"])
video_path = None

if option == "Upload video":
    video_file = st.file_uploader("Upload MP4 video", type=["mp4"])
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(video_file.read())
        video_path = tfile.name

elif option == "Paste YouTube link":
    video_link = st.text_input("Paste YouTube video link:")
    if video_link:
        with st.spinner("Downloading video from YouTube..."):
            try:
                if not video_link.startswith("http"):
                    video_link = "https://www.youtube.com/watch?v=" + video_link.strip()
                yt = YouTube(video_link)
                stream = yt.streams.filter(f
