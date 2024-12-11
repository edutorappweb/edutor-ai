import requests
from tempfile import NamedTemporaryFile
from typing import List, Literal
import concurrent.futures as cf

class APILimitExceededError(Exception):
    """Custom exception for API rate limit errors."""
    pass

class DialogueItem:
    def __init__(self, text: str, speaker: Literal["student", "mentor"]):
        self.text = text
        self.speaker = speaker

    @property
    def voice_id(self):
        return {
            "student": "cgSgspJ2msm6clMCkdW9",
            "mentor": "XRdIKD2HKD2sMJjeC483"
        }[self.speaker]

def get_elevenlabs_audio(text: str, voice_id: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    headers = {
        "xi-api-key": "sk_7850edb03abc3679a48f0b525043e0b32906273de1b999e5",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            raise ValueError("ElevenLabs API rate limit exceeded")
        raise http_err
    except Exception as err:
        raise err
    
def generate_audio(dialogue_items: List[DialogueItem]) -> dict:
    audio = b""
    transcript = ""

    with cf.ThreadPoolExecutor() as executor:
        futures = []
        for line in dialogue_items:
            transcript_line = f"{line.speaker}: {line.text}"
            future = executor.submit(get_elevenlabs_audio, line.text, line.voice_id)
            futures.append((future, transcript_line))

        for future, transcript_line in futures:
            audio_chunk = future.result()
            audio += audio_chunk
            transcript += transcript_line + "\n"

    return {
        "audio": audio,
        "transcript": transcript
    }