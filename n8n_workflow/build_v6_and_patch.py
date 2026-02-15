"""
build_v6_and_patch.py

1. Loads v5 as the base
2. Applies the user's production changes:
   - Replaces Create Booking Tool with Save Draft Tool
   - Updates node positions to match production
   - Removes Approval Webhook, Send PDF Ticket, Send Confirmation Text (if not in production)
3. Adds quiz routing nodes inline (after Text4)
4. Saves as be_star_ticketing_v6.json
"""
import json, os, copy

DIR = os.path.dirname(os.path.abspath(__file__))
V5  = os.path.join(DIR, "be_star_ticketing_v5.json")
V6  = os.path.join(DIR, "be_star_ticketing_v6.json")
BACKEND = "http://38.242.139.159:3005"

# ── Load v5 ───────────────────────────────────────────────────────
wf = json.load(open(V5, "r", encoding="utf-8"))
print(f"[OK] Loaded v5: {len(wf['nodes'])} nodes")

# ── Step 1: Remove nodes NOT in user's production workflow ────────
# Based on user's pasted JSON, these nodes exist:
PRODUCTION_NODES = {
    "Whatsapp", "User Phone ID", "Access Control4", "If8", "Switch3",
    "Text4", "Get media in base1", "Convert to File", "Convert Audio Type3",
    "Transcribe a recording1", "Cost Calculator", "Voice",
    "Get Image Base64", "Analyze Image (Mistral)2", "Cost Calculator4", "image",
    "Get Stickers Base", "Analyze Strickers (Mistral)3", "Stickers",
    "Memory + Model PreEnter2", "Set metadata3", "Reformer", "Simple Memory",
    "Azure OpenAI Chat Model5", "Log Reformer Rekaz", "Set metadata4",
    "Information Extractor", "Azure OpenAI Chat Model7", "Log Reformer Rekaz4",
    "Edit Fields1", "Pinecone Vector Store1", "Embeddings Azure OpenAI",
    "Aggregate1", "Text3", "Set metadata2", "Be Star Ticketing Agent",
    "Azure OpenAI Chat Model4", "Postgres Chat Memory1", "Log Reformer Rekaz3",
    "Log Usr Messages", "Send presence1", "Splite the messages",
    "Send text", "Log AI Messages1", "Skip First One", "Loop Over Items",
    "No Operation, do nothing", "Send text1", "Log AI Messages", "If",
    # Sticky notes
    "Sticky Note18", "Sticky Note19", "Sticky Note25", "Sticky Note24",
    "Sticky Note6",
}

# Remove nodes not in production
removed = []
wf["nodes"] = [n for n in wf["nodes"]
               if n["name"] in PRODUCTION_NODES or n["name"].startswith("Sticky")]
for n in wf["nodes"]:
    if n["name"] not in PRODUCTION_NODES and not n["name"].startswith("Sticky"):
        removed.append(n["name"])

# Remove connections for removed nodes
REMOVED_NODES = {"Approval Webhook", "Send PDF Ticket", "Send Confirmation Text",
                 "Create Booking Tool"}
for name in REMOVED_NODES:
    wf["connections"].pop(name, None)
for src, outs in list(wf["connections"].items()):
    for conn_type, branches in list(outs.items()):
        for branch in branches:
            branch[:] = [c for c in branch if c["node"] not in REMOVED_NODES]
print(f"[OK] Cleaned non-production nodes")

# ── Step 2: Add Save Draft Tool ──────────────────────────────────
save_draft_tool = {
    "parameters": {
        "toolDescription": "Use this tool immediately after receiving ANY piece of information (Name, Phone, Type, Email, Payment). Pass user_phone, ticket_index (1-based), field (name/phone/type/email/payment), and value.",
        "method": "POST",
        "url": f"{BACKEND}/api/tickets/save-draft",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Content-Type", "value": "application/json"}]},
        "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{\n{\n  \"user_phone\": $('User Phone ID').first().json.User_phone_ID,\n  \"ticket_index\": $fromAI(\"ticket_index\", \"1\"),\n  \"field\": $fromAI(\"field\", \"name\"),\n  \"value\": (\n    ($fromAI(\"value\", \"\") || \"\").includes(\"\u0648\u0635\u0641 \u0627\u0644\u0635\u0648\u0631\u0629\") || \n    ($fromAI(\"value\", \"\") || \"\").includes(\"User sent image\") ||\n    ($fromAI(\"value\", \"\") || \"\").includes(\"\u0627\u0644\u0639\u0645\u064a\u0644 \u0628\u0639\u062a \u0635\u0648\u0631\u0629\")\n  ) && $('Get Image Base64') && $('Get Image Base64').first() ? \"data:image/jpeg;base64,\" + $('Get Image Base64').first().json.data.base64 : $fromAI(\"value\", \"\").replace(/```/g, \"\").trim()\n}\n}}",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequestTool", "typeVersion": 4.4,
    "position": [-11792, 4368], "id": "e0a0b8c4-dc89-407e-bfb2-e210165803e6",
    "name": "Save Draft Tool"
}
wf["nodes"].append(save_draft_tool)
wf["connections"]["Save Draft Tool"] = {
    "ai_tool": [[{"node": "Be Star Ticketing Agent", "type": "ai_tool", "index": 0}]]
}
print("[OK] Added Save Draft Tool")

# ── Step 3: Update node positions to match user's production ──────
POS_MAP = {
    "Whatsapp": [-17056, 3920],
    "If": [-16208, 3920],
    "User Phone ID": [-16032, 3904],
    "Access Control4": [-15872, 3904],
    "If8": [-15712, 3904],
    "Switch3": [-15472, 3856],
    "Text4": [-14352, 3840],
    "Get media in base1": [-15184, 3984],
    "Convert to File": [-15040, 3984],
    "Convert Audio Type3": [-14864, 3984],
    "Transcribe a recording1": [-14688, 3984],
    "Cost Calculator": [-14496, 3984],
    "Voice": [-14352, 3984],
    "Get Image Base64": [-15184, 4160],
    "Analyze Image (Mistral)2": [-14688, 4160],
    "Cost Calculator4": [-14496, 4160],
    "image": [-14352, 4160],
    "Get Stickers Base": [-15184, 4368],
    "Analyze Strickers (Mistral)3": [-14688, 4368],
    "Stickers": [-14352, 4368],
    "Memory + Model PreEnter2": [-14080, 4048],
    "Set metadata3": [-13840, 4048],
    "Reformer": [-13696, 4048],
    "Simple Memory": [-13536, 4272],
    "Azure OpenAI Chat Model5": [-13776, 4224],
    "Log Reformer Rekaz": [-13712, 4368],
    "Set metadata4": [-13424, 4048],
    "Information Extractor": [-13280, 4048],
    "Azure OpenAI Chat Model7": [-13312, 4224],
    "Log Reformer Rekaz4": [-13248, 4352],
    "Edit Fields1": [-12976, 4048],
    "Pinecone Vector Store1": [-12848, 4048],
    "Embeddings Azure OpenAI": [-12848, 4208],
    "Aggregate1": [-12576, 4048],
    "Text3": [-12448, 4048],
    "Set metadata2": [-12304, 4048],
    "Be Star Ticketing Agent": [-12032, 4048],
    "Azure OpenAI Chat Model4": [-12128, 4224],
    "Postgres Chat Memory1": [-11936, 4368],
    "Log Reformer Rekaz3": [-12080, 4368],
    "Log Usr Messages": [-11632, 4048],
    "Send presence1": [-11472, 4048],
    "Splite the messages": [-11312, 4048],
    "Send text": [-11056, 3968],
    "Log AI Messages1": [-10912, 3968],
    "Skip First One": [-11056, 4128],
    "Loop Over Items": [-10880, 4128],
    "No Operation, do nothing": [-10688, 3984],
    "Send text1": [-10704, 4144],
    "Log AI Messages": [-10528, 4144],
}
for n in wf["nodes"]:
    if n["name"] in POS_MAP:
        n["position"] = POS_MAP[n["name"]]
print("[OK] Updated node positions")

# ── Step 4: Update specific node parameters to match production ───
for n in wf["nodes"]:
    # Update webhook IDs and paths
    if n["name"] == "Whatsapp":
        n["id"] = "37dd2c0c-bc56-47ca-b8fb-1ff502b60986"
        n["webhookId"] = "d8fa5154-f391-43c2-ad0c-f5c7b3eb2737"
    # Update If node
    elif n["name"] == "If":
        n["id"] = "da57936c-8823-449e-b411-34a187ec85c3"
        n["typeVersion"] = 2.3

# ── Step 5: Add inline quiz routing nodes ─────────────────────────
QUIZ_NODES = [
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
            "method": "POST", "url": f"{BACKEND}/api/quiz/answer",
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

wf["nodes"].extend(QUIZ_NODES)
print(f"[OK] Added {len(QUIZ_NODES)} quiz nodes")

# ── Step 6: Rewire connections for quiz flow ──────────────────────
conn = wf["connections"]

# Text4 → Check Active Quiz (instead of Memory + Model PreEnter2)
conn["Text4"] = {"main": [[
    {"node": "Check Active Quiz", "type": "main", "index": 0}
]]}

# Check Active Quiz → Quiz Active?
conn["Check Active Quiz"] = {"main": [[
    {"node": "Quiz Active?", "type": "main", "index": 0}
]]}

# Quiz Active?: true → Submit Answer, false → Memory PreEnter (normal)
conn["Quiz Active?"] = {"main": [
    [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],
    [{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}],
]}

# Submit Quiz Answer → Is Answer Correct?
conn["Submit Quiz Answer"] = {"main": [[
    {"node": "Is Answer Correct?", "type": "main", "index": 0}
]]}

# Is Answer Correct?: true → Correct reply, false → Wrong reply
conn["Is Answer Correct?"] = {"main": [
    [{"node": "Quiz Reply Correct", "type": "main", "index": 0}],
    [{"node": "Quiz Reply Wrong",   "type": "main", "index": 0}],
]}

print("[OK] Rewired text message path:")
print("     Text4 -> Check Active Quiz -> Quiz Active?")
print("       YES -> Submit Answer -> Correct/Wrong reply")
print("       NO  -> Memory + Model PreEnter2 (normal AI)")

# ── Step 7: Update meta ──────────────────────────────────────────
wf["meta"] = {
    "templateCredsSetupCompleted": True,
    "instanceId": "8df4082ac81111d2321c538ef34013493a96dd3b14b3af10e13ce9c3849e34d3"
}

# ── Save ──────────────────────────────────────────────────────────
with open(V6, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=True, indent=2)

print(f"\n[DONE] Saved to {V6}")
print(f"[DONE] Total nodes: {len(wf['nodes'])}")
non_sticky = [n["name"] for n in wf["nodes"] if not n["name"].startswith("Sticky")]
print(f"[DONE] Non-sticky nodes: {len(non_sticky)}")
for name in non_sticky:
    print(f"  - {name}")
