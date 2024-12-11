import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assets.system_messages import category_search
from services.call_groq import call_groq

def category_search_order(prompt: str):
    """
    Retrieve the Search Category Order according query

    Parameters:
    prompt (str): User's query to generate Search Category

    Returns:
    str: Get Search Category Order
    """
    
    response = call_groq(prompt, category_search)
    
    return response