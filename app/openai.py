import os
from typing import List, Any
from pydub import AudioSegment
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(ogg_path: str, wav_path: str) -> str:
    """
    Convert OGG audio to WAV and transcribe using OpenAI Whisper.
    """
    AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")
    with open(wav_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text


def chat_with_gpt(messages: List[Any]) -> str:
    """
    Get a chat completion from OpenAI using the new v1.x API.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    # response.choices[0].message.content can be None; ensure we return an empty string in that case
    content = response.choices[0].message.content
    return content or ""
