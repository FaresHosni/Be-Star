import requests
import json
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

url = "http://38.242.139.159:3005/api/tickets/save-draft"
headers = {"Content-Type": "application/json"}

# Randomize phone to start fresh
import time
user_phone = f"2010{int(time.time())}"

fields = [
    {"field": "name", "value": "Draft System Tester"},
    {"field": "phone", "value": "01099988877"},
    {"field": "type", "value": "Student"},
    {"field": "email", "value": "draft@test.com"},
    # Last one triggers completion
    {"field": "payment", "value": "Draft Payment Proof 123"} 
]

print(f"Testing Draft System for User: {user_phone}")

for step, item in enumerate(fields, 1):
    payload = {
        "user_phone": user_phone,
        "ticket_index": 1,
        "field": item["field"],
        "value": item["value"]
    }
    
    print(f"\n[{step}/5] Sending {item['field']}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, ensure_ascii=False)}")
            
            if step == 5:
                if data.get("status") == "completed":
                    print("✅ SUCCESS: Ticket created automatically!")
                else:
                    print("❌ FAILURE: Ticket NOT created on last step.")
            else:
                if data.get("status") == "draft_saved":
                    print(f"✅ Saved. Missing: {data.get('missing_fields')}")
                else:
                    print(f"❌ Unexpected status: {data.get('status')}")
                    
        except:
            print(f"Raw Text: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
