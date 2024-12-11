import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assets.system_messages import *
from services.gemini import upload_url_file_to_gemini, call_gemini, AIServiceError
from services.helper import *
from fastapi import HTTPException
import json
import re

TONE_ID_AND_MESSAGE = {
    1: pushpa_tone_quiz_explainer,
    2: normal_tone_quiz_explainer,
    3: normal_tone_quiz_explainer,
    4: roleplay_tone_quiz_explainer,
    5: example_tone_quiz_explainer,
    6: fun_tone_quiz_explainer,
    7: jethalal_tone_quiz_explainer,
    8: krishna_tone_quiz_explainer,
    9: bhim_tone_quiz_explainer
}

def get_system_message(tone_id: int) -> str:
    """
    Retrieve the system message for the given tone ID.
    """
    return TONE_ID_AND_MESSAGE.get(tone_id, "Invalid tone ID")

def format_response(result):
    """
    Format and parse a response object containing JSON data.
    
    Args:
        result: Response object or string containing JSON data
    
    Returns:
        dict: Parsed and formatted JSON response
    
    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        if isinstance(result, str):
            response_text = result
        else:
            response_text = result.text if hasattr(result, 'text') else str(result)

        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON object found in the response")

        json_string = json_match.group(1)
        json_response = json.loads(json_string)

        if isinstance(json_response.get("explanation"), dict):
            inner_explanation = json_response["explanation"]
            if "explanation" in inner_explanation and "followUpQuestions" in inner_explanation:

                json_response["explanation"] = inner_explanation["explanation"]
                json_response["followUpQuestions"] = inner_explanation["followUpQuestions"]

        if "explanation" in json_response:
            json_response["explanation"] = re.sub(r'\s+', ' ', json_response["explanation"])
        
        if "followUpQuestions" in json_response:
            for key in json_response["followUpQuestions"]:
                if isinstance(json_response["followUpQuestions"][key], str):
                    json_response["followUpQuestions"][key] = re.sub(r'\s+', ' ', json_response["followUpQuestions"][key])
        
        return json_response
    
    except Exception as error:
        raise ValueError(f"Failed to parse the response as JSON: {str(error)}")

def QuizExplainer(
    quiz: str, 
    explanation_length: str, 
    tone_id: int, 
    history: str = None, 
    quiz_details: str = None
) -> str:
    """
    Explains the quiz with the selected tone style.
    """
    try:
        system_message = get_system_message(tone_id)
        url_regex = r'https?://[^\s]+'
        match = re.search(url_regex, quiz)
        
        if match:
            url = match[0]
            remaining_text = quiz.replace(url, "").strip()
            files = upload_url_file_to_gemini(url, mime_type="image/jpeg")
            
            chat_history = file_prepare_chat_history(files)
            
            prompt_format = f"Here is the history of old questions and it's explanations (sometimes it can be empty):\n{history}\n\nHere is my option and answer, questions is in image. Explain it to me & generate follow-up questions for that.\n{remaining_text}\nGenerate a {explanation_length} size explanation based on the quiz's details below:\n{quiz_details}\nMake sure the explanation is in the quiz's Medium language!"
            
            response = call_gemini(prompt=prompt_format, system_message=system_message, history=chat_history)
            formated_response = format_response(response)
            
            return formated_response
            
        else:
            prompt_format = f"Here is the history of old questions and it's explanations (sometimes it can be empty): {history}\n\nHere is my questions, option and answer. Explain it to me & generate follow-up questions for that.\n{quiz}\n\nGenerate a {explanation_length} size explanation based on the quiz's details below:\n{quiz_details}\nMake sure the explanation is in the quiz's Medium language!"
            
            response = call_gemini(prompt_format, system_message)
            formated_response = format_response(response)
            return formated_response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")