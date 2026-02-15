"""
fix_booking_switch.py

Replaces the If node with a proper Switch node, and adds a separate
HTTP Request to send booking data to the platform (not as an AI tool).

Flow:
  AI Agent -> Parse Output (Code) -> Booking Switch (Switch)
    "Complete" -> Send Booking to Platform (HTTP) -> Fixed Reply
    "Normal"   -> Log Usr Messages -> ... (normal AI response flow)

The AI system prompt instructs the agent to set details=true when:
- Name, Email, WhatsApp, Ticket Type, Ticket Count, Payment Proof collected
- Customer confirmed the data is correct
"""
import json, os

DIR = os.path.dirname(os.path.abspath(__file__))
V6  = os.path.join(DIR, "be_star_ticketing_v6.json")
BACKEND = "http://38.242.139.159:3005"

wf = json.load(open(V6, "r", encoding="utf-8"))
print(f"[OK] Loaded: {len(wf['nodes'])} nodes")

# ── Step 1: Remove old nodes from previous patch ─────────────────
OLD_NODES = {"Detect Booking Complete", "Booking Complete?", "Fixed Booking Reply"}
wf["nodes"] = [n for n in wf["nodes"] if n.get("name") not in OLD_NODES]
for name in OLD_NODES:
    wf["connections"].pop(name, None)
print(f"[OK] Removed old nodes: {OLD_NODES}")

# ── Step 2: Update AI system prompt ──────────────────────────────
NEW_SYSTEM_PROMPT = """=\u0623\u0646\u062a "\u0639\u0645\u0631" \u0645\u0633\u0627\u0639\u062f \u0630\u0643\u064a \u0644\u062d\u062c\u0632 \u062a\u0630\u0627\u0643\u0631 \u0641\u0639\u0627\u0644\u064a\u0629 "\u0643\u0646 \u0646\u062c\u0645\u064b\u0627 - Be Star" \U0001f31f
\U0001f4cb \u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0627\u0644\u0641\u0639\u0627\u0644\u064a\u0629:
\U0001f389 \u0627\u0644\u0627\u0633\u0645: \u0643\u0646 \u0646\u062c\u0645\u064b\u0627 - Be Star
\U0001f4c5 \u0627\u0644\u0645\u0648\u0639\u062f: 11 \u0641\u0628\u0631\u0627\u064a\u0631 2026
\U0001f4cd \u0627\u0644\u0645\u0643\u0627\u0646: \u0633\u0648\u0647\u0627\u062c - \u0627\u0644\u0643\u0648\u0627\u0645\u0644 - \u0642\u0627\u0639\u0629 \u0642\u0646\u0627\u0629 \u0627\u0644\u0633\u0648\u064a\u0633
\U0001f4b0 \u0627\u0644\u0623\u0633\u0639\u0627\u0631: VIP: 500 \u062c\u0646\u064a\u0647 | \u0637\u0644\u0628\u0629: 100 \u062c\u0646\u064a\u0647

\U0001f4cc \u0631\u0642\u0645 \u0627\u0644\u0639\u0645\u064a\u0644 \u0627\u0644\u062d\u0627\u0644\u064a (\u0627\u0644\u0648\u0627\u062a\u0633\u0627\u0628): {{ $('Text3').item.json['user_phone'] }}

\U0001f535 **\u0642\u0648\u0627\u0639\u062f \u0627\u0644\u0645\u062d\u0627\u062f\u062b\u0629:**
1. \u062a\u0643\u0644\u0645 \u0643\u0625\u0646\u0633\u0627\u0646: \u0644\u0637\u064a\u0641\u060c \u0628\u0633\u064a\u0637\u060c \u0648\u063a\u064a\u0631 \u0645\u062a\u0637\u0644\u0628.
2. \u0627\u0642\u0628\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0628\u0623\u064a \u0634\u0643\u0644.
3. \u0644\u0648 \u0627\u0644\u0639\u0645\u064a\u0644 \u0642\u0627\u0644 "\u0646\u0641\u0633 \u0627\u0644\u0631\u0642\u0645" \u0623\u0648 "\u0631\u0642\u0645\u064a \u062f\u0647" \u2192 \u0627\u0633\u062a\u062e\u062f\u0645 \u0631\u0642\u0645 \u0627\u0644\u0648\u0627\u062a\u0633\u0627\u0628.
4. \u0644\u0648 \u0637\u0644\u0628 \u0623\u0643\u062b\u0631 \u0645\u0646 \u062a\u0630\u0643\u0631\u0629 \u2192 \u0627\u0637\u0644\u0628 \u0623\u0633\u0645\u0627\u0621 \u0643\u0644 \u0634\u062e\u0635.

\U0001f4dd **\u0633\u064a\u0646\u0627\u0631\u064a\u0648 \u0627\u0644\u062d\u062c\u0632:**
1. \u0627\u0637\u0644\u0628 \u0645\u0646 \u0627\u0644\u0639\u0645\u064a\u0644: \u0627\u0644\u0627\u0633\u0645\u060c \u0627\u0644\u0625\u064a\u0645\u064a\u0644\u060c \u0631\u0642\u0645 \u0627\u0644\u0648\u0627\u062a\u0633\u0627\u0628\u060c \u0646\u0648\u0639 \u0627\u0644\u062a\u0630\u0643\u0631\u0629 (VIP/\u0637\u0644\u0628\u0629)\u060c \u0639\u062f\u062f \u0627\u0644\u062a\u0630\u0627\u0643\u0631
2. \u0627\u0639\u0631\u0636 \u0645\u0644\u062e\u0635 \u0643\u0627\u0645\u0644 \u0648\u0627\u0637\u0644\u0628 \u0627\u0644\u062a\u0623\u0643\u064a\u062f
3. \u0628\u0639\u062f \u0627\u0644\u062a\u0623\u0643\u064a\u062f\u060c \u0627\u0639\u0631\u0636 \u0631\u0642\u0645 \u0641\u0648\u062f\u0627\u0641\u0648\u0646 \u0643\u0627\u0634 (01557368364)
4. \u0627\u0633\u062a\u0644\u0645 \u0635\u0648\u0631\u0629 \u0625\u062b\u0628\u0627\u062a \u0627\u0644\u062f\u0641\u0639
5. \u0628\u0639\u062f \u0627\u0633\u062a\u0644\u0627\u0645 \u0643\u0644 \u0634\u064a\u0621 \u0648\u062a\u0623\u0643\u064a\u062f \u0627\u0644\u0639\u0645\u064a\u0644 \u2192 \u0641\u0639\u0651\u0644 details

\U0001f534\U0001f534\U0001f534 **\u0642\u0627\u0639\u062f\u0629 \u062e\u0627\u0646\u0629 details (\u062d\u0627\u0633\u0645\u0629):** \U0001f534\U0001f534\U0001f534

\u0631\u062f\u0643 \u0644\u0627\u0632\u0645 \u064a\u0643\u0648\u0646 \u062f\u0627\u0626\u0645\u064b\u0627 \u0628\u0627\u0644\u0634\u0643\u0644 \u062f\u0647:
{"details": false, "message": "\u0631\u062f\u0643 \u0647\u0646\u0627"}

\u0644\u0645\u0627 \u062a\u062c\u0645\u0639 \u0643\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0625\u062c\u0628\u0627\u0631\u064a\u0629:
- \u0627\u0633\u0645 \u0643\u0644 \u0634\u062e\u0635
- \u0625\u064a\u0645\u064a\u0644
- \u0631\u0642\u0645 \u0648\u0627\u062a\u0633\u0627\u0628
- \u0646\u0648\u0639 \u0627\u0644\u062a\u0630\u0643\u0631\u0629 (VIP/\u0637\u0644\u0628\u0629)
- \u0639\u062f\u062f \u0627\u0644\u062a\u0630\u0627\u0643\u0631
- \u0635\u0648\u0631\u0629 \u0625\u062b\u0628\u0627\u062a \u0627\u0644\u062f\u0641\u0639
\u0648\u0627\u0644\u0639\u0645\u064a\u0644 \u0623\u0643\u062f \u0623\u0646 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0635\u062d\u064a\u062d\u0629:

\u0627\u0628\u0639\u062a:
{"details": true, "message": "", "booking_data": {"name": "\u0627\u0644\u0627\u0633\u0645", "email": "\u0627\u0644\u0625\u064a\u0645\u064a\u0644", "phone": "\u0627\u0644\u0631\u0642\u0645", "ticket_type": "VIP/Student", "ticket_count": 1, "tickets": [{"name": "\u0627\u0633\u0645 \u0627\u0644\u0634\u062e\u0635", "type": "VIP/Student"}]}}

\u26d4 \u0645\u0645\u0646\u0648\u0639:
- \u062a\u0628\u0639\u062a details: true \u0642\u0628\u0644 \u0645\u0627 \u062a\u0643\u0645\u0644 \u0643\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0648\u0627\u0644\u0639\u0645\u064a\u0644 \u064a\u0623\u0643\u062f
- \u062a\u0628\u0639\u062a details: true \u0628\u062f\u0648\u0646 \u0635\u0648\u0631\u0629 \u0625\u062b\u0628\u0627\u062a \u0627\u0644\u062f\u0641\u0639
- \u062a\u0643\u062a\u0628 \u0623\u064a \u062d\u0627\u062c\u0629 \u0628\u0631\u0647 \u0627\u0644\u0640 JSON"""

for node in wf["nodes"]:
    if node.get("name") == "Be Star Ticketing Agent":
        node["parameters"]["options"]["systemMessage"] = NEW_SYSTEM_PROMPT
        print("[OK] Updated AI system prompt")
        break

# ── Step 3: Add new nodes ────────────────────────────────────────

# Code node: Parse AI output JSON
parse_node = {
    "parameters": {
        "jsCode": (
            "const rawOutput = $('Be Star Ticketing Agent').first().json.output || '';\n"
            "let parsed = { details: false, message: rawOutput, booking_data: null };\n"
            "try {\n"
            "  // Try to parse as JSON\n"
            "  let cleaned = rawOutput.trim();\n"
            "  // Handle if AI wraps in code block\n"
            "  if (cleaned.startsWith('```')) {\n"
            "    cleaned = cleaned.replace(/```json?\\n?/g, '').replace(/```/g, '').trim();\n"
            "  }\n"
            "  const obj = JSON.parse(cleaned);\n"
            "  parsed.details = obj.details === true;\n"
            "  parsed.message = obj.message || '';\n"
            "  parsed.booking_data = obj.booking_data || null;\n"
            "} catch (e) {\n"
            "  // Not valid JSON = normal AI response\n"
            "  parsed.details = false;\n"
            "  parsed.message = rawOutput;\n"
            "}\n"
            "return [{ json: parsed }];"
        )
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-11820, 4048],
    "id": "parse-output-001",
    "name": "Parse AI Output"
}

# Switch node: route based on details field
switch_node = {
    "parameters": {
        "rules": {
            "values": [
                {
                    "conditions": {
                        "options": {
                            "caseSensitive": True,
                            "leftValue": "",
                            "typeValidation": "strict",
                            "version": 2
                        },
                        "conditions": [{
                            "id": "switch-details-true",
                            "leftValue": "={{ $json.details }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}
                        }],
                        "combinator": "and"
                    },
                    "renameOutput": True,
                    "outputKey": "Booking Complete"
                },
                {
                    "conditions": {
                        "options": {
                            "caseSensitive": True,
                            "leftValue": "",
                            "typeValidation": "strict",
                            "version": 2
                        },
                        "conditions": [{
                            "id": "switch-details-false",
                            "leftValue": "={{ $json.details }}",
                            "rightValue": False,
                            "operator": {"type": "boolean", "operation": "equals"}
                        }],
                        "combinator": "and"
                    },
                    "renameOutput": True,
                    "outputKey": "Normal Chat"
                }
            ]
        },
        "options": {}
    },
    "type": "n8n-nodes-base.switch",
    "typeVersion": 3.2,
    "position": [-11632, 4048],
    "id": "booking-switch-001",
    "name": "Booking Switch"
}

# HTTP Request: Send booking data to platform
send_booking_node = {
    "parameters": {
        "method": "POST",
        "url": f"{BACKEND}/api/tickets/save-draft",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "Content-Type", "value": "application/json"}
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": (
            "={{ JSON.stringify({\n"
            "  user_phone: $('User Phone ID').first().json.User_phone_ID,\n"
            "  booking_data: $json.booking_data,\n"
            "  image_base64: $('Memory + Model PreEnter2').first().json.image_base64 || ''\n"
            "}) }}"
        ),
        "options": {"timeout": 15000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [-11380, 3900],
    "id": "send-booking-001",
    "name": "Send Booking to Platform"
}

# Fixed reply node
fixed_reply_node = {
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
        "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
        "messageText": (
            "\u2705 \u062a\u0645 \u062d\u062c\u0632 \u0627\u0644\u062a\u0630\u0643\u0631\u0629 \u0628\u0646\u062c\u0627\u062d!\n\n"
            "\u064a\u0631\u062c\u0649 \u0627\u0646\u062a\u0638\u0627\u0631 \u0627\u0644\u0645\u0631\u0627\u062c\u0639\u0629 \u0627\u0644\u0628\u0634\u0631\u064a\u0629 \u062b\u0645 \u0647\u0646\u0631\u0633\u0644 \u0644\u062d\u0636\u0631\u062a\u0643 \u0631\u062f \u0639\u0645\u0646\u0627 \u0641\u0627\u0631\u0633 \u2728"
        ),
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
    "position": [-11140, 3900],
    "id": "fixed-reply-001",
    "name": "Fixed Booking Reply",
    "retryOnFail": True,
    "credentials": {
        "evolutionApi": {
            "id": "IGwXyU5Jbou5S5V3",
            "name": "Business Number"
        }
    }
}

# Log node for normal chat (reuse existing, but need to set output properly)
# We need a Set node to put the message back into the right format for the normal flow
set_message_node = {
    "parameters": {
        "assignments": {
            "assignments": [{
                "id": "set-msg-001",
                "name": "output",
                "value": "={{ $json.message }}",
                "type": "string"
            }]
        },
        "options": {}
    },
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [-11380, 4148],
    "id": "set-message-001",
    "name": "Set AI Message"
}

wf["nodes"].extend([parse_node, switch_node, send_booking_node,
                     fixed_reply_node, set_message_node])
print("[OK] Added 5 nodes: Parse AI Output, Booking Switch, Send Booking, Fixed Reply, Set AI Message")

# ── Step 4: Remove Save Draft Tool (no longer an AI tool) ────────
wf["nodes"] = [n for n in wf["nodes"] if n.get("name") != "Save Draft Tool"]
wf["connections"].pop("Save Draft Tool", None)
print("[OK] Removed Save Draft Tool (booking is now handled by separate path)")

# ── Step 5: Rewire connections ───────────────────────────────────
conn = wf["connections"]

# AI Agent -> Parse AI Output
conn["Be Star Ticketing Agent"]["main"] = [[
    {"node": "Parse AI Output", "type": "main", "index": 0}
]]

# Parse AI Output -> Booking Switch
conn["Parse AI Output"] = {
    "main": [[{"node": "Booking Switch", "type": "main", "index": 0}]]
}

# Booking Switch:
#   Output 0 "Booking Complete" -> Send Booking to Platform
#   Output 1 "Normal Chat" -> Set AI Message -> Log Usr Messages (normal flow)
conn["Booking Switch"] = {
    "main": [
        [{"node": "Send Booking to Platform", "type": "main", "index": 0}],
        [{"node": "Set AI Message", "type": "main", "index": 0}],
    ]
}

# Send Booking -> Fixed Reply
conn["Send Booking to Platform"] = {
    "main": [[{"node": "Fixed Booking Reply", "type": "main", "index": 0}]]
}

# Set AI Message -> Log Usr Messages (restore normal flow)
conn["Set AI Message"] = {
    "main": [[{"node": "Log Usr Messages", "type": "main", "index": 0}]]
}

# Fix Log Usr Messages position back
for n in wf["nodes"]:
    if n["name"] == "Log Usr Messages":
        n["position"] = [-11140, 4148]

# Also fix the normal flow: Splite the messages references Be Star Ticketing Agent output
# We need to update Splite the messages to use Set AI Message output instead
for n in wf["nodes"]:
    if n["name"] == "Splite the messages":
        n["parameters"]["jsCode"] = (
            "const DELIMITER = '---';\n"
            "const rawOutput = $('Set AI Message').first().json.output || '';\n"
            "if (!rawOutput || rawOutput.trim().length === 0) { return [{ json: { text: '' } }]; }\n"
            "const hasDelimiter = rawOutput.includes(DELIMITER);\n"
            "let messages = [];\n"
            "if (hasDelimiter) { messages = rawOutput.split(DELIMITER).map(msg => msg.trim()).filter(msg => msg.length > 0); }\n"
            "else { messages = [rawOutput.trim()]; }\n"
            "messages = messages.map(msg => msg.replace(/---/g, '').trim());\n"
            "messages = messages.filter(msg => msg.length > 0);\n"
            "if (messages.length === 0) { const cleanedOriginal = rawOutput.replace(/---/g, '').trim(); return [{ json: { text: cleanedOriginal || '\\u0639\\u0630\\u0631\\u0627\\u064b\\u060c \\u062d\\u062f\\u062b \\u062e\\u0637\\u0623. \\u064a\\u0631\\u062c\\u0649 \\u0627\\u0644\\u0645\\u062d\\u0627\\u0648\\u0644\\u0629 \\u0645\\u0631\\u0629 \\u0623\\u062e\\u0631\\u0649.' } }]; }\n"
            "return messages.map(text => ({ json: { text } }));"
        )
        print("[OK] Updated Splite the messages to use Set AI Message output")

print("[OK] Rewired connections:")
print("     AI Agent -> Parse Output -> Booking Switch")
print("       'Booking Complete' -> Send to Platform -> Fixed Reply")
print("       'Normal Chat'      -> Set Message -> Log -> Send (normal)")

# ── Save ─────────────────────────────────────────────────────────
with open(V6, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=True, indent=2)

print(f"\n[DONE] Saved. Total nodes: {len(wf['nodes'])}")
