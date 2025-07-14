import streamlit as st
import openai
import whisper as whisper_lib
import os
import tempfile
import subprocess
from pytube import YouTube

# CONFIG (TEMPORARY FOR LOCAL TESTING)
openai.api_key = "sk-your-openai-key-here"  # Replace with your real OpenAI API key

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
                stream = yt.streams.filter(file_extension="mp4", progressive=True).order_by("resolution").desc().first()
                yt_file = stream.download(filename_prefix="yt_")
                video_path = yt_file
                st.success("✅ Video downloaded successfully")
            except Exception as e:
                st.error(f"Failed to download video: {e}")

# CHARACTER/SHOW INPUT
show_name = st.text_input("Show or Character Name:")
action = st.selectbox("What do you want to generate?", ["Short Clip", "Meme", "Both"])

# PROCESS VIDEO
if st.button("Generate") and video_path:
    with st.spinner("Processing video..."):
        try:
            # Step 1: Use default values instead of scene detection
            start_time = "00:00:00"
            duration = "00:00:60"

            # Step 2: Transcribe with Whisper
            model = whisper_lib.load_model("base")
            result = model.transcribe(video_path, language="tagalog")
            transcript = result["text"]

            # Step 3: Create short branded video clip (without subtitles)
            output_clip = video_path.replace(".mp4", "_clip.mp4")

            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-ss", start_time, "-t", duration,
                "-vf", "scale=720:1280,drawbox=x=0:y=0:w=iw:h=100:color=black@0.5:t=fill,drawtext=text='ClipMeme AI':fontcolor=white:fontsize=30:x=10:y=10",
                "-y", output_clip
            ])

            st.video(output_clip)
            st.success("✅ Clip generated from first 60 seconds")

            # Step 4: Meme Text via OpenAI
            if action in ["Meme", "Both"]:
                prompt = f"Generate 3 witty or emotional Filipino meme captions based on this teleserye quote: '{transcript[:200]}'"
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                captions = response["choices"][0]["message"]["content"]
                st.write("### Suggested Meme Captions:")
                st.markdown(captions)

            if option == "Upload video":
                os.remove(video_path)

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.info("Please upload a video or paste a YouTube link to begin.")
