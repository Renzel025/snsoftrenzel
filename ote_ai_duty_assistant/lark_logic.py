import re
from p0_logic import handle_p0_emergency
from wiki_ai_logic import handle_wiki_ai

SILENT_P0_GROUP_ID = "oc_f4e833c6744e55eb50dfcd8830fa913e"

def process_message(incoming_text, chat_id, user_id, token, lark_client, groq_key):
    text_lower = incoming_text.strip().lower()
    
    # Check for P0 Declaration
    is_p0 = re.search(r'\bp0\b', text_lower)
    is_asking = "?" in text_lower or text_lower.startswith(('is ', 'are ', 'how ', 'what ', 'can '))

    if chat_id == SILENT_P0_GROUP_ID and is_p0 and not is_asking:
        if handle_p0_emergency(chat_id, user_id, token, lark_client):
            return 

    # Otherwise, use AI Assistant
    handle_wiki_ai(incoming_text, chat_id, token, groq_key)