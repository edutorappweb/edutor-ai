import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.gemini import call_gemini
from assets.system_messages import dialogue_generation, dialogue_translation
from services.elevenlabs import *

def generate_dialogues(prompt: str, history: list = "") -> list[DialogueItem]:
    original_dialogue = call_gemini(
        prompt=prompt,
        system_message=dialogue_generation,
        history=history
    )
    
    translated_dialogue = call_gemini(
        prompt=original_dialogue['response'],
        system_message=dialogue_translation
    )
    
    dialogue = translated_dialogue['response']
    
    dialogue_items = []

    for line in dialogue.split('\n'):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        if line.startswith("mentor:"):
            speaker = "mentor"
            text = line[len("mentor:"):].strip()
        elif line.startswith("student:"):
            speaker = "student"
            text = line[len("student:"):].strip()
        else:
            continue
        
        dialogue_items.append(DialogueItem(text=text, speaker=speaker))
    
    return dialogue_items

def get_podcast(prompt: str, history: list, file_details):
    fix_prompt = "Generate a Mentor-Student conversation in Gujarati Language that discusses the about provided content in an easy, lively, and engaging manner. Strictly Create at least 400 to 600 words of conversation or longer if content is large enough.\n\nThe conversation should be suitable for a student from the Gujarat. Content is for 8. Content is of Subject Maths and of chapter.\n\nEnsure that the dialogue is natural, includes short interruptions and confirmatory questions, and covers all key points from the content. The conversation should follow the format where each line starts with 'mentor:' or 'student:'.\nnever write any expression in bracket. like a (laughing...).\nTeacher is a male character and student is a girl."
    prompt_format = f"{prompt}{fix_prompt}\n\n{file_details}"
    dialogue_items = generate_dialogues(prompt=prompt_format, history=history)
    
    return generate_audio(dialogue_items)