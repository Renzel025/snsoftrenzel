import json, time, requests
import lark_oapi as lark
from lark_oapi.api.vc.v1 import *

DAVID_ID = "ou_cb50274ea2ff11149ba48d95c1803f01"
KAKA_ID = "ou_cb50274ea2ff11149ba48d95c1803f01"
WIKI_URL = "https://casinoplus.sg.larksuite.com/wiki/NQCYwsDE2i6aFikrdWhldSWHgLg"

def send_notification(receive_id, id_type, token, tag_id, tag_name, text):
    url = f"https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type={id_type}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"receive_id": receive_id, "msg_type": "text", "content": json.dumps({"text": f"<at user_id=\"{tag_id}\">{tag_name}</at> 🚨 {text}"})}
    requests.post(url, headers=headers, json=payload)

def handle_p0_emergency(chat_id, user_id, token, lark_client):
    try:
        req = ApplyReserveRequest.builder().user_id_type("open_id").request_body(
            ApplyReserveRequestBody.builder()
            .end_time(str(int(time.time()) + 3600))
            .owner_id(user_id)
            .meeting_settings(ReserveMeetingSetting.builder().topic("P0 Incident Bridge").meeting_initial_type(1).auto_record(True).build())
            .build()
        ).build()
        
        resp = lark_client.vc.v1.reserve.apply(req)
        link = json.loads(lark.JSON.marshal(resp.data)).get("reserve", {}).get("url")
        
        if link:
            card = {
                "config": {"wide_screen_mode": True},
                "header": {"title": {"tag": "plain_text", "content": "🚨 EMERGENCY: P0 INCIDENT ISSUE"}, "template": "red"},
                "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": f"<at id=all></at>\n**P0 Incident Declared.**\n\n📖 [Wiki]({WIKI_URL})"}},
                             {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "JOIN NOW"}, "url": link, "type": "primary"}]}]
            }
            requests.post(f"https://open-sg.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id", 
                          headers={"Authorization": f"Bearer {token}"}, 
                          json={"receive_id": chat_id, "msg_type": "interactive", "content": json.dumps(card)})
            
            time.sleep(10)
            send_notification(chat_id, "chat_id", token, DAVID_ID, "Sir David", "10s P0 Alert")
            time.sleep(10)
            send_notification(chat_id, "chat_id", token, KAKA_ID, "Sir Kaka", "20s P0 Alert")
            return True
    except Exception as e:
        print(f"🚨 P0 Logic Error: {str(e)}")
    return False