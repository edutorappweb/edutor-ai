import os
import google.generativeai as genai
import tempfile
from fastapi import UploadFile
from typing import Any, Union
from dotenv import load_dotenv
import requests
import json

load_dotenv()

genai.configure(api_key="AIzaSyAmKMnTLNM_KMxFbupYWm2fs-pNvHcmEhM")

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    def __init__(self, message: str, status_code: int, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def call_gemini(prompt: str, system_message: str, history: Union[list, None] = None):
    """
    Generate a response from the Gemini API.
    """
    try:
        if not prompt or not system_message:
            return AIServiceError(
                message="Prompt and System Message Must be provided!",
                status_code=400
            )

        generation_config = {
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config=generation_config,
            system_instruction=system_message
        )

        initial_history = []
        if history:
            initial_history = history.copy()
        
        chat_session = model.start_chat(history=history or [])
        response = chat_session.send_message(prompt)
        
        full_history = initial_history.copy()
        
        if prompt.strip():
            full_history.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
        
        # Add the model's response
        full_history.append({
            "role": "model",
            "parts": [{"text": response.text}]
        })
        
        json_history = json.dumps(full_history, indent=2)
        return {"response": response.text, "history": json_history}

    except AIServiceError as e:
        raise e
    except genai.types.BlockedPromptException as e:
        raise AIServiceError(
            message="Content blocked due to safety concerns",
            status_code=400,
            details=str(e)
        )
    except Exception as e:
        raise AIServiceError(
            message="Failed to generate response",
            status_code=500,
            details=str(e)
        )

def upload_url_file_to_gemini(url: str, mime_type: str = "image/png") -> str:
    """
    Upload a file from URL to Gemini API.
    Returns the Gemini URL of the uploaded file.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        upload_result = genai.upload_file(temp_file_path, mime_type=mime_type)

        os.remove(temp_file_path)
        
        return upload_result.uri

    except Exception as e:
        print("Error uploading file:", str(e))
        raise e

def handle_file_upload_to_gemini(file: UploadFile, mime_type: str = "image/png") -> str:
    """
    Upload the user-provided file directly to Gemini.
    """
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as temp_file:
            temp_file.write(file.file.read())

        # Upload the file to Gemini
        upload_result = genai.upload_file(file_path, mime_type=mime_type)
        os.remove(file_path)
        
        return upload_result.uri
    except Exception as e:
        raise RuntimeError(f"Failed to upload file to Gemini: {e}")