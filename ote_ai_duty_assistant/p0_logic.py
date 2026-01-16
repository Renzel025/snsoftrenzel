import json, time, requests, threading
import lark_oapi as lark
from lark_oapi.api.vc.v1 import *

# Target IDs
DAVID_ID = "ou_cb50274ea2ff11149ba48d95c1803f01"
KAKA_ID = "ou_cb50274ea2ff11149ba48d95c1803f01"
WIKI_URL = "https://casinoplus.sg.larksuite.com/wiki/NQCYwsDE2i6aFikrdWhldSWHgLg"

def send_escalation(chat_id, token, tag_id, tag_name, text, meeting_link):
    """Sends notification to Group Chat (Tag) AND Private DM (Link)."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    
    # --- 1. SEND TO GROUP (TAGGING) ---
    group_url = "https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id"
    group_payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": f'<at user_id="{tag_id}">{tag_name}</at> 🚨 {text}'})
    }
    requests.post(group_url, headers=headers, json=group_payload)

    # --- 2. SEND PRIVATE DM (MEETING LINK) ---
    dm_url = "https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=open_id"
    dm_payload = {
        "receive_id": tag_id,
        "msg_type": "text",
        "content": json.dumps({"text": f"🚨 P0 ESCALATION ALERT\n{text}\n\nJoin Bridge: {meeting_link}"})
    }
    requests.post(dm_url, headers=headers, json=dm_payload)

def escalation_timer(chat_id, token, meeting_link):
    """Automatic background timing."""
    # Alert David: 10 seconds for test
    time.sleep(10) 
    send_escalation(chat_id, token, DAVID_ID, "Sir David", "emergency meeting still ongoing already 10mins since started please contact sir david", meeting_link)
    
    # Alert Kaka: 20 seconds total for test
    time.sleep(10)
    send_escalation(chat_id, token, KAKA_ID, "Sir Kaka", "emergency meeting still ongoing already 20mins since started please contact sir kaka", meeting_link)

def handle_p0_emergency(chat_id, user_id, token, lark_client):
    try:
        # 1. Create VC Bridge with AUTO-RECORD
        req = ApplyReserveRequest.builder().user_id_type("open_id").request_body(
            ApplyReserveRequestBody.builder()
            .end_time(str(int(time.time()) + 3600))
            .owner_id(user_id)
            .meeting_settings(ReserveMeetingSetting.builder()
                .topic("P0 Incident Bridge").meeting_initial_type(1).auto_record(True).build())
            .build()
        ).build()
        
        resp = lark_client.vc.v1.reserve.apply(req)
        link = json.loads(lark.JSON.marshal(resp.data)).get("reserve", {}).get("url")
        
        if link:
            # 2. Main Red Card with JOIN NOW Button in Group
            card = {
                "config": {"wide_screen_mode": True},
                "header": {"title": {"tag": "plain_text", "content": "🚨 EMERGENCY: P0 INCIDENT ISSUE"}, "template": "red"},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"<at id=all></at>\n**P0 Incident Declared.**\n\n📖 [Wiki]({WIKI_URL})"}},
                    {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "JOIN NOW"}, "url": link, "type": "primary"}]}
                ]
            }
            requests.post("https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id",
                          headers={"Authorization": f"Bearer {token}"},
                          json={"receive_id": chat_id, "msg_type": "interactive", "content": json.dumps(card)})
            
            # 3. Start Automatic Background Escalation
            threading.Thread(target=escalation_timer, args=(chat_id, token, link), daemon=True).start()
            return True
    except Exception as e:
        print(f"🚨 P0 Logic Error: {str(e)}", flush=True)
    return False