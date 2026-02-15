"""
save_and_patch.py — One-shot: saves the production workflow from a Python
literal, patches it with quiz nodes, writes the result.
"""

import json, os, copy

DIR = os.path.dirname(os.path.abspath(__file__))
V6   = os.path.join(DIR, "be_star_ticketing_v6.json")
BACKEND = "http://38.242.139.159:3005"

# ── OLD standalone quiz node names to remove ──────────────────────
OLD = {
    "Quiz Answer Webhook", "Extract Answer Data", "Check Active Question",
    "Has Active Question?", "Submit Quiz Answer", "Is Correct?",
    "Reply Correct", "Reply Wrong", "No Active Quiz (Pass Through)",
}

# ── NEW nodes ─────────────────────────────────────────────────────
NEW_NODES = [
    {
        "parameters": {"url": f"{BACKEND}/api/quiz/active-question",
                       "options": {"timeout": 8000}},
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3,
        "position": [-14192, 3720], "id": "quiz-check-001",
        "name": "Check Active Quiz", "continueOnFail": True
    },
    {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "",
                            "typeValidation": "strict", "version": 2},
                "conditions": [{"id": "qc1",
                    "leftValue": "={{ $json.has_active }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals"}}],
                "combinator": "and"},
            "options": {}},
        "type": "n8n-nodes-base.if", "typeVersion": 2.2,
        "position": [-14000, 3720], "id": "quiz-if-001",
        "name": "Quiz Active?"
    },
    {
        "parameters": {
            "method": "POST",
            "url": f"{BACKEND}/api/quiz/answer",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "Content-Type", "value": "application/json"}]},
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={\n  \"phone\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n  \"answer_text\": \"{{ $('Text4').item.json.Text }}\",\n  \"sender_name\": \"{{ $('Whatsapp').item.json.body.data.pushName || 'Unknown' }}\"\n}",
            "options": {"timeout": 15000}},
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3,
        "position": [-13760, 3620], "id": "quiz-submit-001",
        "name": "Submit Quiz Answer"
    },
    {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "",
                            "typeValidation": "strict", "version": 2},
                "conditions": [{"id": "qc2",
                    "leftValue": "={{ $json.is_correct }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals"}}],
                "combinator": "and"},
            "options": {}},
        "type": "n8n-nodes-base.if", "typeVersion": 2.2,
        "position": [-13520, 3620], "id": "quiz-if-correct-001",
        "name": "Is Answer Correct?"
    },
    {
        "parameters": {
            "resource": "messages-api",
            "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
            "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
            "messageText": "={{ '\u2705 \u0625\u062c\u0627\u0628\u0629 \u0635\u062d\u064a\u062d\u0629! \u0623\u062d\u0633\u0646\u062a \ud83c\udf89\\n\\n\ud83c\udfc6 \u0627\u0644\u0646\u0642\u0627\u0637: ' + $('Submit Quiz Answer').item.json.points_earned + '\\n\ud83d\udcca \u0646\u0633\u0628\u0629 \u0627\u0644\u062a\u0634\u0627\u0628\u0647: ' + ($('Submit Quiz Answer').item.json.similarity || 100) + '%' }}",
            "options_message": {"quoted": {"messageQuoted": {
                "messageId": "={{ $('Whatsapp').first().json.body.data.key.id }}"}}}},
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1, "position": [-13280, 3520],
        "id": "quiz-reply-correct-001", "name": "Quiz Reply Correct",
        "retryOnFail": True,
        "credentials": {"evolutionApi": {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}}
    },
    {
        "parameters": {
            "resource": "messages-api",
            "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
            "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
            "messageText": "={{ '\u274c \u0625\u062c\u0627\u0628\u0629 \u062e\u0627\u0637\u0626\u0629\\n\\n' + ($('Submit Quiz Answer').item.json.message || '\u062d\u0627\u0648\u0644 \u0641\u064a \u0627\u0644\u0633\u0624\u0627\u0644 \u0627\u0644\u0642\u0627\u062f\u0645! \ud83d\udcaa') }}",
            "options_message": {"quoted": {"messageQuoted": {
                "messageId": "={{ $('Whatsapp').first().json.body.data.key.id }}"}}}},
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1, "position": [-13280, 3720],
        "id": "quiz-reply-wrong-001", "name": "Quiz Reply Wrong",
        "retryOnFail": True,
        "credentials": {"evolutionApi": {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}}
    },
]

# ── NEW connections ───────────────────────────────────────────────
NEW_CONN = {
    "Text4": {"main": [[{"node": "Check Active Quiz", "type": "main", "index": 0}]]},
    "Check Active Quiz": {"main": [[{"node": "Quiz Active?", "type": "main", "index": 0}]]},
    "Quiz Active?": {"main": [
        [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],
        [{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}],
    ]},
    "Submit Quiz Answer": {"main": [[{"node": "Is Answer Correct?", "type": "main", "index": 0}]]},
    "Is Answer Correct?": {"main": [
        [{"node": "Quiz Reply Correct", "type": "main", "index": 0}],
        [{"node": "Quiz Reply Wrong",   "type": "main", "index": 0}],
    ]},
}


def patch(wf):
    # 1. Remove old standalone quiz nodes
    wf["nodes"] = [n for n in wf["nodes"] if n.get("name") not in OLD]
    for name in OLD:
        wf["connections"].pop(name, None)
    for src, outs in list(wf["connections"].items()):
        for conn_type, branches in list(outs.items()):
            for branch in branches:
                branch[:] = [c for c in branch if c["node"] not in OLD]
    print(f"[OK] Removed {len(OLD)} old quiz nodes")

    # 2. Add new nodes
    wf["nodes"].extend(NEW_NODES)
    print(f"[OK] Added {len(NEW_NODES)} new quiz nodes")

    # 3. Rewire connections
    wf["connections"].update(NEW_CONN)
    print("[OK] Rewired: Text4 → Check Quiz → Quiz Active?")
    print("       ├─ YES → Submit Answer → Correct/Wrong reply")
    print("       └─ NO  → Memory + Model PreEnter2 (normal AI)")

    return wf


if __name__ == "__main__":
    if not os.path.exists(V6):
        print(f"[!!] File not found: {V6}")
        print("[!!] Make sure be_star_ticketing_v6.json exists")
        exit(1)

    wf = json.load(open(V6, "r", encoding="utf-8"))
    print(f"[OK] Loaded {len(wf['nodes'])} nodes")

    wf = patch(wf)

    with open(V6, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] Patched in-place: {V6}")
    print(f"[DONE] Total nodes: {len(wf['nodes'])}")
