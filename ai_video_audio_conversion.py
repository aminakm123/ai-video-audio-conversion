import streamlit as st
import moviepy.editor as mp
import imageio_ffmpeg as ffmpeg
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import openai
import requests
import os
from pydub import AudioSegment
import subprocess
from dotenv import load_dotenv

load_dotenv()
azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

# Set up Google Cloud Authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ai-video-audio-replacement-df8ff9469c6e.json'

# Main function to run the app
def main():
    st.title("AI-Powered Video Audio Replacement")

    # Step 1: Upload Video and Extract Audio
    video_file = upload_video()
    if video_file:
        # Step 2: Transcribe the Audio
        transcript = transcribe_audio(video_file)
        st.write("Original Transcript: ", transcript)

        # Step 3: Send Transcript to GPT-4o for Correction
        corrected_transcript = correct_transcript(transcript)
        if corrected_transcript:
            st.write("Corrected Transcript: ", corrected_transcript)
        else:
            st.error("Failed to correct the transcript.")

        # Step 4: Convert Corrected Transcript to Speech (Google TTS)
        if corrected_transcript:
            new_audio = text_to_speech(corrected_transcript)

            # Step 5: Replace Audio in the Original Video
            if new_audio:
                output_video = replace_audio_in_video(video_file, new_audio)
                st.video(output_video)

# Function to upload video and extract its audio
def upload_video():
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        video_path = os.path.join("temp_video.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())

        # Debugging: Check if the video file was saved correctly
        if os.path.exists(video_path):
            st.success("Video uploaded successfully!")
        else:
            st.error("Failed to save the uploaded video file.")
            return None

        # Display video
        st.video(video_path)

        # Load the video using MoviePy
        video = mp.VideoFileClip(video_path)

        # Extract and save the audio from the video
        audio_path = "extracted_audio.wav"
        video.audio.write_audiofile(audio_path)

        # Convert stereo audio to mono
        sound = AudioSegment.from_wav(audio_path)
        sound = sound.set_channels(1)  # Convert to mono
        mono_audio_path = "extracted_audio_mono.wav"
        sound.export(mono_audio_path, format="wav")

        st.success("Audio extracted from video and converted to mono")
        return mono_audio_path
    return None

# Function to transcribe audio using Google Speech-to-Text
def transcribe_audio(audio_path):
    client = speech.SpeechClient()

    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript

# Function to correct the transcript using GPT-4o (Azure OpenAI)
def correct_transcript(transcript):    
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_openai_key
    }
    data = {
        "messages": [{"role": "user", "content": f"Correct the following transcript: {transcript}"}],
        "max_tokens": 500
    }

    response = requests.post(azure_openai_endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("choices"):
            corrected_text = result["choices"][0]["message"]["content"]
            return corrected_text
        else:
            st.error("API returned no choices.")
    else:
        st.error(f"Error from API: {response.status_code} - {response.text}")
    return None

# Function to convert corrected transcript to speech using Google Text-to-Speech
def text_to_speech(text, output_audio_path="output_audio.wav"):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Try different voices or log available ones
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Wavenet-D"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    try:
        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        with open(output_audio_path, "wb") as out:
            out.write(response.audio_content)
        st.success("New audio generated and saved!")
        st.success("Click the below play button to listen to AI Audio!")
        # Play the audio using Streamlit's audio player
        st.audio(output_audio_path, format="audio/wav")
        return output_audio_path

    except Exception as e:
        st.error(f"Text-to-Speech failed: {e}")
        return None

# Function to replace audio in the original video
def replace_audio_in_video(video_path, new_audio_path, output_video_path="output_video.mp4"):
    try:
        # Get FPS using ffprobe on the video file
        video_fps = get_media_fps(video_path)
        st.write(f"Video FPS: {video_fps}")

        # Check if the FPS is a valid number
        if video_fps is None or video_fps <= 0:
            raise ValueError("Invalid FPS value retrieved.")

        # Load video and new audio using MoviePy
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(new_audio_path)

        # Set new audio and write to a new file
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_video_path, fps=video_fps)

        st.success("Video with replaced audio has been generated!")
        return output_video_path

    except Exception as e:
        st.error(f"Error during video processing: {e}")
        return None
    
def get_media_format(media_path):
    try:
        # Get the media format using FFprobe
        probe_cmd = [
            'ffprobe',
            "-v", "error",
            "-show_entries", "format=format_name",
            "-of", "csv=p=0",
            media_path
        ]

        # Debug: Print the command being executed and the media path
        st.write(f"Running FFprobe command for format: {' '.join(probe_cmd)}")
        
        output = subprocess.check_output(probe_cmd, stderr=subprocess.STDOUT)
        media_format = output.decode().strip()

        st.write("FFprobe Output: ", media_format)  # Log the output for debugging

        return media_format

    except subprocess.CalledProcessError as e:
        st.error(f"Error retrieving media format: {e.output.decode()}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def get_media_fps(media_path):
    try:
        # First, check the media format
        media_format = get_media_format(media_path)

        # Debug: Print media format for confirmation
        st.write(f"Media Format: {media_format}")

        # Check if the media format is a video
        # if media_format and ('video' in media_format or 'mp4' in media_format or 'mov' in media_format):
        # Proceed only if it's a video format
        if media_format and 'mp4' in media_format:
            # Get the average frame rate from the video stream
            fps_cmd = [
                'ffprobe',
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=avg_frame_rate",
                "-of", "csv=p=0",
                media_path
            ]
            fps_output = subprocess.check_output(fps_cmd, stderr=subprocess.STDOUT)
            fps_lines = fps_output.decode().strip().splitlines()

            if not fps_lines or len(fps_lines) == 0:
                raise ValueError("No FPS value found in ffprobe output.")

            avg_frame_rate = fps_lines[0]  # Get the first line which should be the average frame rate

            # Calculate FPS from avg_frame_rate
            if "/" in avg_frame_rate:
                num, denom = map(float, avg_frame_rate.split("/"))
                fps = num / denom
            else:
                fps = float(avg_frame_rate)

            return fps
        else:
            st.error("Unsupported media format. Please provide a valid video file.")
            return None

    except subprocess.CalledProcessError as e:
        st.error(f"Error retrieving media FPS: {e.output.decode()}")
        return None
    except ValueError as ve:
        st.error(f"Value error: {ve}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


if __name__ == "__main__":
    main()
