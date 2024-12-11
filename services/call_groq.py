import os
from typing import Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def call_groq(prompt, system_message):
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content":system_message
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            model="llama3-8b-8192"
        )
        
        return chat_completion.choices[0].message.content

    except Exception as e:
        return e