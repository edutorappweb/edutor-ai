from assets.system_messages import talk_pdf_system_message, talk_pdf_page_summary, talk_pdf_explain_page, talk_pdf_important_point, talk_pdf_create_quiz
from services.gemini import call_gemini

fix_prompt = {
    1: talk_pdf_page_summary,
    2: talk_pdf_explain_page,
    3: talk_pdf_important_point,
    4: talk_pdf_create_quiz
}

def get_prompt(prompt_id):
    return fix_prompt.get(prompt_id, "Invalid ID")

def generate_response(prompt: int, file_details: str, history: list) -> str:

    prompt = get_prompt(prompt)
    prompt_format = f"{prompt}\n\n{file_details}"
    
    try:
        response = call_gemini(prompt_format, talk_pdf_system_message, history)
        return {"explanation":response['response'], "chat_history":response['history']}
    
    except Exception as e:
        return e