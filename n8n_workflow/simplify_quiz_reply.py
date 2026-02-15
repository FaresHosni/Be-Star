"""
simplify_quiz_reply.py
Simplifies quiz reply: remove correct/wrong split, use single neutral reply.

BEFORE: Submit Quiz Answer -> Is Answer Correct? -> Correct/Wrong reply
AFTER:  Submit Quiz Answer -> Quiz Reply ("يتم مراجعة الإجابات")
"""
import json, os

DIR = os.path.dirname(os.path.abspath(__file__))
V6  = os.path.join(DIR, "be_star_ticketing_v6.json")

wf = json.load(open(V6, "r", encoding="utf-8"))
print(f"[OK] Loaded: {len(wf['nodes'])} nodes")

# 1. Remove: Is Answer Correct?, Quiz Reply Correct, Quiz Reply Wrong
REMOVE = {"Is Answer Correct?", "Quiz Reply Correct", "Quiz Reply Wrong"}
wf["nodes"] = [n for n in wf["nodes"] if n.get("name") not in REMOVE]
for name in REMOVE:
    wf["connections"].pop(name, None)
print(f"[OK] Removed 3 nodes: {REMOVE}")

# 2. Add single unified reply node
quiz_reply = {
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
        "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
        "messageText": "\u2705 \u062a\u0645 \u0627\u0633\u062a\u0644\u0627\u0645 \u0625\u062c\u0627\u0628\u062a\u0643\u060c \u064a\u062a\u0645 \u0645\u0631\u0627\u062c\u0639\u0629 \u0627\u0644\u0625\u062c\u0627\u0628\u0627\u062a \ud83d\udccb",
        "options_message": {
            "quoted": {
                "messageQuoted": {
                    "messageId": "={{ $('Whatsapp').first().json.body.data.key.id }}"
                }
            }
        }
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [-13280, 3620],
    "id": "quiz-reply-001",
    "name": "Quiz Reply",
    "retryOnFail": True,
    "credentials": {
        "evolutionApi": {
            "id": "IGwXyU5Jbou5S5V3",
            "name": "Business Number"
        }
    }
}
wf["nodes"].append(quiz_reply)
print("[OK] Added single 'Quiz Reply' node")

# 3. Rewire: Submit Quiz Answer -> Quiz Reply (directly, no If)
wf["connections"]["Submit Quiz Answer"] = {
    "main": [[{"node": "Quiz Reply", "type": "main", "index": 0}]]
}
print("[OK] Rewired: Submit Quiz Answer -> Quiz Reply")

# 4. Save
with open(V6, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=True, indent=2)

print(f"\n[DONE] Saved. Total nodes: {len(wf['nodes'])}")
