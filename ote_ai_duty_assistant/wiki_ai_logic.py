import json, requests

# Direct Document Token from the URL
OBJ_TOKEN = "O94kwR7YWiRyFkkTVf2lHHzpgbc" 

def get_wiki_content(token):
    """
    Fetches text directly from the Docx API.
    Bypasses the Wiki Node API to avoid permission errors from the Wiki Space.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        # Direct call to Docx raw_content endpoint
        doc_url = f"https://open-sg.larksuite.com/open-apis/docx/v1/documents/{OBJ_TOKEN}/raw_content"
        doc_res = requests.get(doc_url, headers=headers).json()
        
        # Access content directly from the data object
        content = doc_res.get("data", {}).get("content", "")
        if content:
            return content
            
        print(f"⚠️ Docx API Access Issue: {doc_res.get('msg')}")
    except Exception as e:
        print(f"🚨 Docx Read Error: {str(e)}")
    return ""

def handle_wiki_ai(incoming_text, chat_id, token, groq_key):
    """
    Uses the fetched Docx content to provide AI-generated answers via Groq.
    """
    wiki_context = get_wiki_content(token)
    
    if not wiki_context:
        # This triggers if the Docx API returns no content
        reply = "I cannot read the document, please check if the bot has 'Viewer' access to the Doc."
    else:
        # Inject document content into the AI system prompt
        payload = {
            "model": "llama-3.1-8b-instant", 
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are OSE-AI. Strictly use this document context to answer: {wiki_context}. Be concise."
                },
                {"role": "user", "content": incoming_text}
            ]
        }
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {groq_key}"}, 
                json=payload
            ).json()
            reply = res.get("choices", [{}])[0].get("message", {}).get("content", "AI Error.")
        except Exception as e:
            print(f"🚨 Groq API Error: {str(e)}")
            reply = "AI Processing Error."

    # Send the response back to the Lark chat
    requests.post(
        f"https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id", 
        headers={"Authorization": f"Bearer {token}"}, 
        json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": reply})}
    )