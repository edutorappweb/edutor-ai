import os
from google.cloud import texttospeech
from fastapi import HTTPException
import io

# Load environment variables for Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/chiragjoshi/Documents/GitHub/NewEdutorAI/controller/keys.json'

def synthesize_speech(text_block: str, language_code: str):
    cleaned_text = text_block.replace('*', '')

    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        effects_profile_id=['small-bluetooth-speaker-class-device'],
        speaking_rate=1.0,
        pitch=1.0,
    )

    request_data = {
        "input": synthesis_input,
        "voice": voice,
        "audio_config": audio_config,
    }

    try:
        response = client.synthesize_speech(**request_data)
        return io.BytesIO(response.audio_content)
    except Exception as error:
        print('Error during synthesis:', error)
        raise HTTPException(status_code=500, detail='Failed to synthesize speech')