def prepare_chat_history(file_data) -> list:
    """
    Prepare chat history with file data in the correct format for Gemini.
    """
    return [{
        "role": "user",
        "parts": [{
            "inline_data": {
                "mime_type": "image/png",
                "data": file_data
            }
        }]
    }]

def file_prepare_chat_history(file_uri) -> list:
    return [{'role': 'user', 'parts': [{'file_data': {'mime_type': 'image/jpeg', 'file_uri': file_uri}}]}]