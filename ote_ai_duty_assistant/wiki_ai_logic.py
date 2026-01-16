import json, requests

WIKI_NODE_TOKEN = "O94kwR7YWiRyFkkTVf2lHHzpgbc"

def get_wiki_content(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        node_url = f"https://open-sg.larksuite.com/open-apis/wiki/v2/nodes/{WIKI_NODE_TOKEN}"
        node_res = requests.get(node_url, headers=headers).json()
        obj_token = node_res.get("data", {}).get("node", {}).get("obj_token")
        
        if obj_token:
            doc_url = f"https://open-sg.larksuite.com/open-apis/docx/v1/documents/{obj_token}/raw_content"
            doc_res = requests.get(doc_url, headers=headers).json()
            return doc_res.get("data", {}).get("content", "")
    except:
        pass
    return ""

def handle_wiki_ai(incoming_text, chat_id, token, groq_key):
    wiki_context = get_wiki_content(token)
    
    if not wiki_context:
        reply = "I cannot read the wiki, check permissions."
    else:
        payload = {
            "model": "llama-3.1-8b-instant", 
            "messages": [
                {"role": "system", "content": f"You are OSE-AI. Use this Wiki: {wiki_context}. Be concise."},
                {"role": "user", "content": incoming_text}
            ]
        }
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                headers={"Authorization": f"Bearer {groq_key}"}, json=payload).json()
            reply = res.get("choices", [{}])[0].get("message", {}).get("content", "AI Error.")
        except:
            reply = "AI Processing Error."

    requests.post(f"https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id", 
                  headers={"Authorization": f"Bearer {token}"}, 
                  json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": reply})})