import os, json, base64, hashlib, requests
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
from Crypto.Cipher import AES
import lark_oapi as lark
# Import the router from our main logic file
from lark_logic import process_message 

load_dotenv(override=True)
app = FastAPI()

APP_ID = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")
ENCRYPT_KEY = os.getenv("LARK_ENCRYPT_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the official Lark Client for VC/Meeting functions
lark_client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()
    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[16:])).decode("utf-8", "ignore")
    def _unpad(self, s):
        return s[:-s[-1]]

def get_tenant_token():
    """Fetches the token needed for IM and Wiki APIs."""
    url = "https://open-sg.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

@app.post("/lark/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    raw = await request.json()
    
    # Decrypt message if encryption is enabled in Lark Console
    data = json.loads(AESCipher(ENCRYPT_KEY).decrypt(raw["encrypt"])) if "encrypt" in raw else raw
    
    # URL Challenge for Webhook setup
    if data.get("type") == "url_verification": 
        return {"challenge": data["challenge"]}

    event = data.get("event", {})
    message = event.get("message", {})
    if not message: 
        return {"msg": "ok"}

    # Extracting core identifiers
    chat_id = message.get("chat_id")
    user_id = event.get("sender", {}).get("sender_id", {}).get("open_id")
    
    # Parse text from Lark's JSON content format
    try:
        content_json = json.loads(message.get("content", "{}"))
        incoming_text = content_json.get("text", "")
    except:
        incoming_text = ""
        
    token = get_tenant_token()

    # Offload processing to lark_logic.py (Router)
    # This keeps the P0 automation and Wiki AI responses fast
    background_tasks.add_task(
        process_message, 
        incoming_text, 
        chat_id, 
        user_id, 
        token, 
        lark_client, 
        GROQ_API_KEY
    )
    
    return {"msg": "ok"}