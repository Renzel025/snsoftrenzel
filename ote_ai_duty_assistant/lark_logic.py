import re, json, sys
from p0_logic import handle_p0_emergency
from wiki_ai_logic import handle_wiki_ai

# --- CONFIGURATION ---
SILENT_P0_GROUP_ID = "oc_f4e833c6744e55eb50dfcd8830fa913e"
DOCS_GROUP_ID = "oc_3ba68c30afab1613db2c6fd6276befc9" 

def process_message(incoming_text, chat_id, user_id, token, lark_client, groq_key):
    print(f"\n📢 RECEIVED MESSAGE IN: {chat_id}", flush=True)
    text_lower = incoming_text.strip().lower()
    
    # --- ROUTE 1: P0 GROUP ---
    if chat_id == SILENT_P0_GROUP_ID:
        # Check for P0 but IGNORE if "not p0" is mentioned
        is_p0 = re.search(r'\bp0\b', text_lower)
        is_not_p0 = re.search(r'\bnot\s+p0\b', text_lower)
        is_asking = "?" in text_lower or text_lower.startswith(('is ', 'are ', 'how ', 'what ', 'can '))

        # Only trigger if P0 is found AND it's not "not p0" AND it's not a question
        if is_p0 and not is_not_p0 and not is_asking:
            print("🚨 P0 Trigger Validated. Executing Automation...", flush=True)
            handle_p0_emergency(chat_id, user_id, token, lark_client)
            return 
        
        print("🤫 Condition not met or 'not p0' detected. Staying silent.", flush=True)
        return 

    # --- ROUTE 2: DOCS GROUP ---
    if chat_id == DOCS_GROUP_ID:
        handle_wiki_ai(incoming_text, chat_id, token, groq_key)
        return

    return