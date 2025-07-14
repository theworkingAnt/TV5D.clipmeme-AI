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
                stream = yt.streams.filter(file_extension="mp4", progressive=True).order_by("resolution").desc().first()
                yt_file = stream.download(filename_prefix="yt_")
                video_path = yt_file
                st.success("✅ Video downloaded successfully")
            except Exception as e:
                st.error(f"Failed to download video: {e}")

# INPUTS
show_name = st.text_input("Show or Character Name:")
action = st.selectbox("What do you want to generate?", ["Short Clip", "Meme", "Both"])
emotion_choice = st.selectbox("Pick emotion to extract:", ["Drama", "Comedy", "Romantic", "Intense", "Neutral"])

# PROCESS VIDEO
if st.button("Generate") and video_path:
    with st.spinner("Processing video..."):
        try:
            # Transcribe full video
            model = whisper_lib.load_model("base")
            result = model.transcribe(video_path, language="tagalog")
            transcript = result["text"]
            full_segments = transcript.split(".")

            # Chunk the transcript and classify each segment
            segments = []
            for i in range(0, len(full_segments), 3):
                chunk = ". ".join(full_segments[i:i+3]).strip()
                start_sec = i * 3 * 2  # rough start time
                if chunk:
                    prompt = f"What is the emotional tone of this teleserye scene?\nScene: {chunk}\nRespond with one word only: Drama, Comedy, Romantic, Intense, or Neutral."
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    emotion = response.choices[0].message.content.strip().capitalize()
                    segments.append({"emotion": emotion, "text": chunk, "start": start_sec})

            # Find the best-matching emotional scene
            match = next((s for s in segments if s["emotion"] == emotion_choice), None)
            if not match:
                st.warning(f"No matching {emotion_choice} scene found. Showing first available scene.")
                match = segments[0]

            # Set up timestamps
            start_time = match["start"]
            mins, secs = divmod(start_time, 60)
            timestamp = f"00:{int(mins):02d}:{int(secs):02d}"
            subtitle = match["text"]

            # Save subtitle
            srt_path = video_path.replace(".mp4", ".srt")
            with open(srt_path, "w", encoding="utf-8") as srt_file:
                srt_file.write(f"1\n00:00:00,000 --> 00:00:59,000\n{subtitle.strip()}")

            # Clip video
            output_clip = video_path.replace(".mp4", f"_{emotion_choice.lower()}_clip.mp4")
            ffmpeg_result = subprocess.run([
                "ffmpeg", "-i", video_path,
                "-ss", timestamp, "-t", "00:01:00",
                "-vf", f"subtitles={srt_path},scale=720:1280,drawbox=x=0:y=0:w=iw:h=100:color=black@0.5:t=fill,drawtext=text='ClipMeme AI':fontcolor=white:fontsize=30:x=10:y=10",
                "-y", output_clip
            ], capture_output=True, text=True)

            if ffmpeg_result.returncode != 0:
                st.error("❌ FFmpeg failed:")
                st.code(ffmpeg_result.stderr)
            elif not os.path.exists(output_clip):
                st.error("❌ Output clip was not created.")
            else:
                st.video(output_clip)
                st.success(f"✅ {emotion_choice} scene clipped!")

                # Meme caption via GPT
                if action in ["Meme", "Both"]:
                    meme_prompt = f"Generate 3 Filipino meme captions for this teleserye scene: '{subtitle[:200]}'"
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": meme_prompt}]
                    )
                    captions = response.choices[0].message.content
                    st.write("### Suggested Meme Captions:")
                    st.markdown(captions)

                # Download
                with open(output_clip, "rb") as f:
                    st.download_button(
                        label="📥 Download Generated Clip",
                        data=f,
                        file_name="clipmeme_output.mp4",
                        mime="video/mp4"
                    )

                if option == "Upload video":
                    os.remove(video_path)

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.info("Please upload a video or paste a YouTube link to begin.")
