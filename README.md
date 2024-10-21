# AI-Powered Video Audio Replacement PoC

This repository contains a Proof of Concept (PoC) for a Streamlit-based application that takes a video file, transcribes the audio, corrects it using GPT-4o, and replaces the original audio with an AI-generated voice. The primary goal is to replace improperly spoken words (such as "umms" and "hmms") and grammatical mistakes with clean, corrected audio.

## Features

- **Video Upload**: Users can upload a video file, and the app will extract the audio from it.
- **Speech-to-Text (Transcription)**: The extracted audio is transcribed using Google's Speech-to-Text API.
- **AI-Powered Correction**: The transcribed text is sent to Azure's OpenAI GPT-4o model to correct grammatical errors and remove filler words.
- **Text-to-Speech**: The corrected transcript is converted into speech using Google’s Text-to-Speech API (Journey voice model).
- **Audio Replacement**: The new AI-generated audio is synced and replaced in the original video.

## How it Works

1. **Upload a Video**: You upload a video that has improper audio (with grammatical mistakes, filler words, etc.).
2. **Transcription**: The app uses Google’s Speech-to-Text API to transcribe the audio in the video.
3. **Text Correction**: The transcription is sent to Azure's GPT-4o model, which cleans up grammatical issues and removes unwanted filler words.
4. **Generate New Audio**: The corrected transcript is converted into new, clean speech using Google’s Text-to-Speech API.
5. **Replace Audio**: The original video’s audio is replaced with the new, corrected audio, producing a final output video.

## Tech Stack

- **Streamlit**: For building the web-based user interface.
- **Google Cloud Speech-to-Text**: For converting speech from the video into text.
- **Azure OpenAI GPT-4o**: For correcting transcription errors and improving grammatical accuracy.
- **Google Cloud Text-to-Speech**: For converting the corrected text into synthetic voice (Journey voice model).
- **MoviePy**: For handling video editing and audio replacement.

## Prerequisites

To run this project, you will need the following:

- Python 3.x
- Google Cloud credentials for Speech-to-Text and Text-to-Speech services
- Azure OpenAI GPT-4o API credentials
- Required Python packages (listed below)

### API Credentials

1. **Google Cloud**: Create a Google Cloud account and enable the **Speech-to-Text** and **Text-to-Speech** APIs. Download your JSON credentials and set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your credentials file.
   
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="ai-video-audio-replacement-df8ff9469c6e.json"
    ```

2. Azure OpenAI: Create an Azure account and subscribe to the OpenAI GPT-4o service. Make sure you have the API key and endpoint.

Installation
Clone this repository:

```bash
git clone https://github.com/aminakm123/ai-video-audio-conversion.git
```

Navigate to the project directory:


cd ai-video-audio-replacement

Install the required Python packages:
```bash
pip install streamlit google-cloud-speech google-cloud-texttospeech moviepy openai requests
```

Set up your API credentials:

Add your Google Cloud JSON credentials file path in the code.
Replace the placeholders in the code with your Azure OpenAI API key and endpoint.

Usage

Run the Streamlit application:
```bash
streamlit run ai_video_audio_conversion.py
```
Open the web interface (usually at http://localhost:8501), and follow these steps:

Upload a video file.

The app will extract, transcribe, and correct the audio, then generate a new video with the corrected audio.
Download or view the video with the replaced audio.

File Structure
├── app.py              # Main application code for Streamlit
├── README.md           # Project documentation
└── requirements.txt    # Python dependencies

Requirements

Python 3.x
Streamlit
Google Cloud Speech and Text-to-Speech libraries
MoviePy
Azure OpenAI API

You can install the requirements using the command:
```bash
pip install -r requirements.txt
```
