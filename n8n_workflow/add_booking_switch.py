"""
add_booking_switch.py

Adds a deterministic booking switch after the AI agent:
1. Updates the AI system prompt to include BOOKING_COMPLETE marker
2. Adds a Code node after the AI to detect the marker
3. Adds an If node to split on booking_complete flag
4. Adds a fixed reply node for completed bookings
5. Rewires connections

BEFORE:
  Be Star Ticketing Agent -> Log Usr Messages -> Send presence1 -> ...

AFTER:
  Be Star Ticketing Agent -> Detect Booking Complete (Code)
    -> Booking Complete? (If)
      YES -> Fixed Booking Reply (Evolution API)
      NO  -> Log Usr Messages -> Send presence1 -> ... (normal)
"""
import json, os

DIR = os.path.dirname(os.path.abspath(__file__))
V6  = os.path.join(DIR, "be_star_ticketing_v6.json")

wf = json.load(open(V6, "r", encoding="utf-8"))
print(f"[OK] Loaded: {len(wf['nodes'])} nodes")

# ── Step 1: Update AI system prompt ──────────────────────────────
# Find the Be Star Ticketing Agent node and update its system prompt
for node in wf["nodes"]:
    if node.get("name") == "Be Star Ticketing Agent":
        old_prompt = node["parameters"]["options"]["systemMessage"]

        # Add BOOKING_COMPLETE instruction to the system prompt
        booking_complete_instruction = (
            "\n\n"
            "\U0001f534\U0001f534\U0001f534 **\u0642\u0627\u0639\u062f\u0629 \u0627\u0644\u0625\u0646\u0647\u0627\u0621 (CRITICAL):** \U0001f534\U0001f534\U0001f534\n"
            "\u0644\u0645\u0627 \u062a\u062c\u0645\u0639 \u0643\u0644 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0625\u062c\u0628\u0627\u0631\u064a\u0629 (\u0627\u0633\u0645\u060c \u0646\u0648\u0639 \u062a\u0630\u0643\u0631\u0629\u060c \u0631\u0642\u0645 \u062a\u0644\u064a\u0641\u0648\u0646) \u0648\u062a\u0633\u062a\u0644\u0645 \u0635\u0648\u0631\u0629 \u0625\u062b\u0628\u0627\u062a \u0627\u0644\u062f\u0641\u0639\u060c\n"
            "\u0648\u062a\u062d\u0641\u0638 \u0643\u0644 \u062d\u0627\u062c\u0629 \u0628\u0640 save_draft\u060c\n"
            "\u064a\u0628\u0642\u0649 \u0622\u062e\u0631 \u0631\u062f \u0644\u064a\u0643 \u0644\u0627\u0632\u0645 \u064a\u0643\u0648\u0646 \u0628\u0627\u0644\u0638\u0628\u0637:\n"
            "BOOKING_COMPLETE\n"
            "\u0645\u0634 \u062a\u0636\u064a\u0641 \u0623\u064a \u0643\u0644\u0627\u0645 \u062a\u0627\u0646\u064a. \u0641\u0642\u0637 \u0627\u0644\u0643\u0644\u0645\u0629 \u062f\u064a.\n"
            "\u0644\u0648 \u0644\u0633\u0647 \u0646\u0627\u0642\u0635 \u0628\u064a\u0627\u0646\u0627\u062a \u0623\u0648 \u0645\u0634 \u0627\u0633\u062a\u0644\u0645\u062a \u0635\u0648\u0631\u0629 \u0627\u0644\u062f\u0641\u0639\u060c \u0643\u0645\u0644 \u0639\u0627\u062f\u064a \u0648\u0627\u0637\u0644\u0628 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0646\u0627\u0642\u0635\u0629."
        )

        node["parameters"]["options"]["systemMessage"] = old_prompt + booking_complete_instruction
        print("[OK] Updated AI system prompt with BOOKING_COMPLETE instruction")
        break

# ── Step 2: Add new nodes ────────────────────────────────────────

# Code node to detect BOOKING_COMPLETE marker
detect_node = {
    "parameters": {
        "jsCode": (
            "const rawOutput = $('Be Star Ticketing Agent').first().json.output || '';\n"
            "const trimmed = rawOutput.trim();\n"
            "const isComplete = trimmed === 'BOOKING_COMPLETE' || trimmed.includes('BOOKING_COMPLETE');\n"
            "return [{ json: { output: rawOutput, booking_complete: isComplete } }];"
        )
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [-11820, 4048],
    "id": "detect-booking-001",
    "name": "Detect Booking Complete"
}

# If node to check booking_complete flag
if_booking_node = {
    "parameters": {
        "conditions": {
            "options": {
                "caseSensitive": True,
                "leftValue": "",
                "typeValidation": "strict",
                "version": 2
            },
            "conditions": [{
                "id": "booking-cond-001",
                "leftValue": "={{ $json.booking_complete }}",
                "rightValue": True,
                "operator": {"type": "boolean", "operation": "equals"}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [-11632, 4048],
    "id": "if-booking-001",
    "name": "Booking Complete?"
}

# Fixed reply node for completed bookings
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
    "position": [-11380, 3900],
    "id": "fixed-reply-booking-001",
    "name": "Fixed Booking Reply",
    "retryOnFail": True,
    "credentials": {
        "evolutionApi": {
            "id": "IGwXyU5Jbou5S5V3",
            "name": "Business Number"
        }
    }
}

wf["nodes"].extend([detect_node, if_booking_node, fixed_reply_node])
print("[OK] Added 3 nodes: Detect Booking Complete, Booking Complete?, Fixed Booking Reply")

# ── Step 3: Rewire connections ───────────────────────────────────
conn = wf["connections"]

# BEFORE: Be Star Ticketing Agent -> Log Usr Messages
# AFTER:  Be Star Ticketing Agent -> Detect Booking Complete -> Booking Complete?
#           YES -> Fixed Booking Reply
#           NO  -> Log Usr Messages (normal flow)

conn["Be Star Ticketing Agent"]["main"] = [[
    {"node": "Detect Booking Complete", "type": "main", "index": 0}
]]

conn["Detect Booking Complete"] = {
    "main": [[{"node": "Booking Complete?", "type": "main", "index": 0}]]
}

conn["Booking Complete?"] = {
    "main": [
        [{"node": "Fixed Booking Reply", "type": "main", "index": 0}],   # true
        [{"node": "Log Usr Messages", "type": "main", "index": 0}],      # false
    ]
}

# Also move Log Usr Messages position slightly to make room
for node in wf["nodes"]:
    if node["name"] == "Log Usr Messages":
        node["position"] = [-11380, 4148]

print("[OK] Rewired:")
print("     AI Agent -> Detect Booking -> Complete?")
print("       YES -> Fixed Reply")
print("       NO  -> Log Usr Messages (normal)")

# ── Save ─────────────────────────────────────────────────────────
with open(V6, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=True, indent=2)

print(f"\n[DONE] Saved. Total nodes: {len(wf['nodes'])}")
