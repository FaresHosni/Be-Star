import json

with open("current_workflow.json", "r", encoding="utf-8") as f:
    wf = json.load(f)

nodes = wf["nodes"]
connections = wf["connections"]

# ======================================================================
# TASK 1: Add Reaction output to Switch3
# ======================================================================
for node in nodes:
    if node["name"] == "Switch3":
        # Add Reaction rule at the BEGINNING (index 0)
        reaction_rule = {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                "conditions": [{
                    "id": "vip-sw-react",
                    "leftValue": "={{ $('Whatsapp').first().json.body.data.messageType }}",
                    "rightValue": "reactionMessage",
                    "operator": {"type": "string", "operation": "equals"}
                }],
                "combinator": "and"
            },
            "renameOutput": True,
            "outputKey": "Reaction"
        }
        # Insert at beginning so Reaction is output 0
        node["parameters"]["rules"]["values"].insert(0, reaction_rule)
        print("OK: Added Reaction output to Switch3 (output index 0)")
        break

# Update Switch3 connections - shift existing outputs by 1 and add Reaction at index 0
old_switch3_conns = connections.get("Switch3", {}).get("main", [])
# Old: [Text(0), Audio(1), Photos(2), Stickers(3)]
# New: [Reaction(0), Text(1), Audio(2), Photos(3), Stickers(4)]
new_switch3_conns = [[]]  # Reaction output - empty for now, will be connected to VIP system later
new_switch3_conns.extend(old_switch3_conns)  # Shift all existing connections by 1
connections["Switch3"]["main"] = new_switch3_conns
print("OK: Updated Switch3 connections (Reaction at index 0, existing shifted)")

# ======================================================================
# TASK 2: Add VIP system after "Is VIP?"
# ======================================================================

# --- VIP Nodes to Add ---
# Position them after Is VIP? which is at [-1120, 2992]
vip_nodes = [
    # 1. Get VIP Settings
    {
        "parameters": {
            "method": "GET",
            "url": "http://38.242.139.159:3005/api/vip/settings",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-880, 2880],
        "id": "vip-settings-001",
        "name": "Get VIP Settings"
    },
    # 2. VIP Message Type Switch
    {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{
                                "id": "vip-sw-react",
                                "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                "rightValue": "reactionMessage",
                                "operator": {"type": "string", "operation": "equals"}
                            }],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Reaction"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [
                                {
                                    "id": "vip-sw-text1",
                                    "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                    "rightValue": "conversation",
                                    "operator": {"type": "string", "operation": "equals"}
                                },
                                {
                                    "id": "vip-sw-text2",
                                    "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                    "rightValue": "extendedTextMessage",
                                    "operator": {"type": "string", "operation": "equals"}
                                }
                            ],
                            "combinator": "or"
                        },
                        "renameOutput": True,
                        "outputKey": "Text"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{
                                "id": "vip-sw-audio",
                                "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                "rightValue": "audioMessage",
                                "operator": {"type": "string", "operation": "equals"}
                            }],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Audio"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{
                                "id": "vip-sw-photos",
                                "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                "rightValue": "imageMessage",
                                "operator": {"type": "string", "operation": "equals"}
                            }],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Photos"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{
                                "id": "vip-sw-stickers",
                                "leftValue": "={{ $(\"Whatsapp\").first().json.body.data.messageType }}",
                                "rightValue": "stickerMessage",
                                "operator": {"type": "string", "operation": "equals"}
                            }],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Stickers"
                    }
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.2,
        "position": [-640, 2880],
        "id": "vip-switch-001",
        "name": "VIP Message Type"
    },
    # 3. Update VIP Reacted (for Reaction path)
    {
        "parameters": {
            "method": "POST",
            "url": "=http://38.242.139.159:3005/api/vip/webhook/status?phone={{ $(\"User Phone ID\").item.json.User_phone_ID }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "{\"status\": \"reacted\", \"source\": \"n8n\"}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-400, 2720],
        "id": "vip-update-react-001",
        "name": "Update VIP Reacted"
    },
    # 4. VIP Reaction AI
    {
        "parameters": {
            "method": "POST",
            "url": "https://mrai-openai.openai.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2024-08-01-preview",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "api-key", "value": "5zSQL871XpyGNXgzSx0LPwzkCrPqYj52L5ODHMA0bs6stZlhi35xJQQJ99BKACfhMk5XJ3w3AAABACOGk5RF"},
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\"model\":\"gpt-4.1-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"\\u0623\\u0646\\u062a \\u0645\\u0633\\u0627\\u0639\\u062f \\u0645\\u0647\\u0630\\u0628 \\u0644\\u0643\\u0628\\u0627\\u0631 \\u0627\\u0644\\u0632\\u0648\\u0627\\u0631. \\u0627\\u0644\\u0636\\u064a\\u0641 \\u0628\\u0639\\u062a \\u0631\\u064a\\u0623\\u0643\\u0634\\u0646 (\\u062a\\u0641\\u0627\\u0639\\u0644) \\u0639\\u0644\\u0649 \\u062f\\u0639\\u0648\\u062a\\u0647.\\n\\n\\ud83d\\udc64 \\u0627\\u0633\\u0645 \\u0627\\u0644\\u0636\\u064a\\u0641: {{ $('Check Is VIP').first().json.guest.name }}\\n\\n\\ud83d\\udc4d \\u0623\\u0633\\u0644\\u0648\\u0628 \\u0627\\u0644\\u0631\\u062f:\\n{{ $('Get VIP Settings').first().json.reaction_reply }}\\n\\n\\u0627\\u0643\\u062a\\u0628 \\u0631\\u062f \\u0645\\u0647\\u0630\\u0628 \\u0648\\u0642\\u0635\\u064a\\u0631 \\u0648\\u0645\\u0646\\u0633\\u0642 \\u0645\\u0633\\u062a\\u0644\\u0647\\u0645 \\u0645\\u0646 \\u0623\\u0633\\u0644\\u0648\\u0628 \\u0627\\u0644\\u0631\\u062f. \\u0627\\u0633\\u062a\\u062e\\u062f\\u0645 \\u0627\\u0633\\u0645 \\u0627\\u0644\\u0636\\u064a\\u0641. \\u0636\\u064a\\u0641 \\u0625\\u064a\\u0645\\u0648\\u062c\\u064a \\u0645\\u0646\\u0627\\u0633\\u0628\\u0629.\\n\\u0631\\u062f \\u0628\\u0627\\u0644\\u0646\\u0635 \\u0645\\u0628\\u0627\\u0634\\u0631\\u0629 \\u0628\\u062f\\u0648\\u0646 JSON.\"},{\"role\":\"user\",\"content\":\"\\u0627\\u0644\\u0636\\u064a\\u0641 \\u0639\\u0645\\u0644 \\u0631\\u064a\\u0623\\u0643\\u0634\\u0646 \\u0639\\u0644\\u0649 \\u0627\\u0644\\u062f\\u0639\\u0648\\u0629\"}],\"max_tokens\":200,\"temperature\":0.8}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-160, 2720],
        "id": "vip-reaction-ai-001",
        "name": "VIP Reaction AI"
    },
    # 5. Send VIP Reaction Reply
    {
        "parameters": {
            "resource": "messages-api",
            "instanceName": "={{ $(\"Whatsapp\").first().json.body.instance }}",
            "remoteJid": "={{ $(\"Whatsapp\").first().json.body.data.key.remoteJid }}",
            "messageText": "={{ $json.choices[0].message.content }}",
            "options_message": {}
        },
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [80, 2720],
        "id": "vip-send-react-001",
        "name": "Send VIP Reaction Reply",
        "credentials": {
            "evolutionApi": {
                "id": "IGwXyU5Jbou5S5V3",
                "name": "Business Number"
            }
        }
    },
    # 6. Classify VIP Intent (AI Agent for Text/Audio/Photos/Stickers)
    {
        "parameters": {
            "method": "POST",
            "url": "https://mrai-openai.openai.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2024-08-01-preview",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "api-key", "value": "5zSQL871XpyGNXgzSx0LPwzkCrPqYj52L5ODHMA0bs6stZlhi35xJQQJ99BKACfhMk5XJ3w3AAABACOGk5RF"},
                    {"name": "Content-Type", "value": "application/json"}
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\"model\":\"gpt-4.1-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"\\u0623\\u0646\\u062a \\u0645\\u0633\\u0627\\u0639\\u062f \\u0645\\u0647\\u0630\\u0628 \\u0648\\u0631\\u0627\\u0642\\u064a \\u062c\\u062f\\u0627\\u064b \\u0644\\u0625\\u062f\\u0627\\u0631\\u0629 \\u062f\\u0639\\u0648\\u0627\\u062a \\u0643\\u0628\\u0627\\u0631 \\u0627\\u0644\\u0632\\u0648\\u0627\\u0631 \\u0644\\u0641\\u0639\\u0627\\u0644\\u064a\\u0629 \\u062e\\u0627\\u0635\\u0629.\\n\\n\\ud83d\\udccb \\u0645\\u0639\\u0644\\u0648\\u0645\\u0627\\u062a \\u0627\\u0644\\u0625\\u064a\\u0641\\u0646\\u062a:\\n{{ $('Get VIP Settings').first().json.inquiry_reply }}\\n\\n\\ud83d\\udc4d \\u0623\\u0633\\u0644\\u0648\\u0628 \\u0627\\u0644\\u0631\\u062f \\u0639\\u0644\\u0649 \\u0627\\u0644\\u0631\\u064a\\u0623\\u0643\\u0634\\u0646:\\n{{ $('Get VIP Settings').first().json.reaction_reply }}\\n\\n\\u2705 \\u0623\\u0633\\u0644\\u0648\\u0628 \\u0631\\u0633\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0642\\u0628\\u0648\\u0644:\\n{{ $('Get VIP Settings').first().json.accept_reply }}\\n\\n\\ud83d\\ude14 \\u0623\\u0633\\u0644\\u0648\\u0628 \\u0631\\u0633\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0631\\u0641\\u0636:\\n{{ $('Get VIP Settings').first().json.decline_reply }}\\n\\n\\ud83d\\udc64 \\u0627\\u0633\\u0645 \\u0627\\u0644\\u0636\\u064a\\u0641: {{ $('Check Is VIP').first().json.guest.name }}\\n\\n\\u0645\\u0647\\u0645\\u062a\\u0643:\\n1. \\u0635\\u0646\\u0641 \\u0631\\u062f \\u0627\\u0644\\u0636\\u064a\\u0641 \\u0644\\u0648\\u0627\\u062d\\u062f \\u0645\\u0646 3 \\u062a\\u0635\\u0646\\u064a\\u0641\\u0627\\u062a:\\n   - will_attend: \\u0644\\u0648 \\u0642\\u0627\\u0644 \\u0647\\u062d\\u0636\\u0631 \\u0623\\u0648 \\u0625\\u0646 \\u0634\\u0627\\u0621 \\u0627\\u0644\\u0644\\u0647 \\u0623\\u0648 \\u0645\\u0648\\u0627\\u0641\\u0642\\n   - not_attending: \\u0644\\u0648 \\u0642\\u0627\\u0644 \\u0645\\u0634 \\u0647\\u0642\\u062f\\u0631 \\u0623\\u0648 \\u0645\\u0634\\u063a\\u0648\\u0644 \\u0623\\u0648 \\u0645\\u0639\\u0644\\u0634\\n   - inquiring: \\u0644\\u0648 \\u0633\\u0623\\u0644 \\u0639\\u0646 \\u062a\\u0641\\u0627\\u0635\\u064a\\u0644 \\u0623\\u0648 \\u0645\\u0643\\u0627\\u0646 \\u0623\\u0648 \\u0648\\u0642\\u062a\\n2. \\u0627\\u0643\\u062a\\u0628 \\u0631\\u062f \\u0645\\u0647\\u0630\\u0628 \\u0648\\u0645\\u062d\\u062a\\u0631\\u0641 \\u064a\\u0646\\u0627\\u0633\\u0628 \\u0627\\u0644\\u0645\\u0648\\u0642\\u0641\\n3. \\u0627\\u0633\\u062a\\u062e\\u062f\\u0645 \\u0627\\u0633\\u0645 \\u0627\\u0644\\u0636\\u064a\\u0641\\n4. \\u0644\\u0648 \\u0628\\u064a\\u0633\\u0623\\u0644 \\u2192 \\u0631\\u062f \\u0645\\u0646 \\u0645\\u0639\\u0644\\u0648\\u0645\\u0627\\u062a \\u0627\\u0644\\u0625\\u064a\\u0641\\u0646\\u062a\\n5. \\u0644\\u0648 \\u0645\\u0648\\u0627\\u0641\\u0642 \\u2192 \\u0631\\u062f \\u0628\\u0623\\u0633\\u0644\\u0648\\u0628 \\u0631\\u0633\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0642\\u0628\\u0648\\u0644\\n6. \\u0644\\u0648 \\u0645\\u0639\\u062a\\u0630\\u0631 \\u2192 \\u0631\\u062f \\u0628\\u0623\\u0633\\u0644\\u0648\\u0628 \\u0631\\u0633\\u0627\\u0644\\u0629 \\u0627\\u0644\\u0631\\u0641\\u0636\\n7. \\u0636\\u064a\\u0641 \\u0625\\u064a\\u0645\\u0648\\u062c\\u064a \\u0645\\u0646\\u0627\\u0633\\u0628\\u0629\\n\\n\\u26a0\\ufe0f \\u0631\\u062f \\u0628\\u0640 JSON \\u0641\\u0642\\u0637:\\n{\\\\\\\"intent\\\\\\\": \\\\\\\"will_attend\\\\\\\", \\\\\\\"reply\\\\\\\": \\\\\\\"\\u0627\\u0644\\u0631\\u062f \\u0627\\u0644\\u0645\\u0646\\u0633\\u0642 \\u0647\\u0646\\u0627\\\\\\\"}\\n\\n\\u0645\\u0645\\u0646\\u0648\\u0639 \\u062a\\u0643\\u062a\\u0628 \\u0623\\u064a \\u062d\\u0627\\u062c\\u0629 \\u0628\\u0631\\u0647 \\u0627\\u0644\\u0640 JSON.\"},{\"role\":\"user\",\"content\":\"{{ $('Whatsapp').first().json.body.data.message.conversation ?? $('Whatsapp').first().json.body.data.message.extendedTextMessage.text ?? '\\u0627\\u0644\\u0636\\u064a\\u0641 \\u0628\\u0639\\u062a \\u062a\\u0641\\u0627\\u0639\\u0644/\\u0631\\u064a\\u0623\\u0643\\u0634\\u0646/\\u0633\\u062a\\u064a\\u0643\\u0631/\\u0635\\u0648\\u0631\\u0629 \\u0639\\u0644\\u0649 \\u0627\\u0644\\u062f\\u0639\\u0648\\u0629' }}\"}],\"max_tokens\":300,\"temperature\":0.7}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-400, 2920],
        "id": "vip-classify-001",
        "name": "Classify VIP Intent"
    },
    # 7. Parse VIP Intent
    {
        "parameters": {
            "jsCode": "const raw = $input.first().json.choices[0].message.content;\nlet intent = \"inquiring\";\nlet reply = \"\";\ntry {\n  const parsed = JSON.parse(raw.trim());\n  intent = parsed.intent || \"inquiring\";\n  reply = parsed.reply || \"\";\n} catch(e) {\n  if (raw.includes(\"will_attend\")) intent = \"will_attend\";\n  else if (raw.includes(\"not_attending\")) intent = \"not_attending\";\n  else intent = \"inquiring\";\n  reply = raw.replace(/[{}\"\\\\]/g, \"\").trim();\n}\nreturn [{ json: { intent, reply } }];"
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-160, 2920],
        "id": "vip-parse-001",
        "name": "Parse VIP Intent"
    },
    # 8. VIP Intent Router
    {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"id": "vip-int-attend", "leftValue": "={{ $json.intent }}", "rightValue": "will_attend", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Will Attend"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"id": "vip-int-not", "leftValue": "={{ $json.intent }}", "rightValue": "not_attending", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Not Attending"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"id": "vip-int-inq", "leftValue": "={{ $json.intent }}", "rightValue": "inquiring", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Inquiring"
                    }
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.2,
        "position": [80, 2920],
        "id": "vip-intent-switch-001",
        "name": "VIP Intent Router"
    },
    # 9. Update VIP Will Attend
    {
        "parameters": {
            "method": "POST",
            "url": "=http://38.242.139.159:3005/api/vip/webhook/status?phone={{ $(\"User Phone ID\").item.json.User_phone_ID }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "{\"status\": \"will_attend\", \"source\": \"n8n\"}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [320, 2800],
        "id": "vip-update-attend-001",
        "name": "Update VIP Will Attend"
    },
    # 10. Update VIP Not Attending
    {
        "parameters": {
            "method": "POST",
            "url": "=http://38.242.139.159:3005/api/vip/webhook/status?phone={{ $(\"User Phone ID\").item.json.User_phone_ID }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "{\"status\": \"not_attending\", \"source\": \"n8n\"}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [320, 2920],
        "id": "vip-update-not-001",
        "name": "Update VIP Not Attending"
    },
    # 11. Update VIP Inquiring
    {
        "parameters": {
            "method": "POST",
            "url": "=http://38.242.139.159:3005/api/vip/webhook/status?phone={{ $(\"User Phone ID\").item.json.User_phone_ID }}",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "{\"status\": \"inquiring\", \"source\": \"n8n\"}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [320, 3040],
        "id": "vip-update-inq-001",
        "name": "Update VIP Inquiring"
    },
    # 12. Send VIP AI Reply (unified for all intents)
    {
        "parameters": {
            "resource": "messages-api",
            "instanceName": "={{ $(\"Whatsapp\").first().json.body.instance }}",
            "remoteJid": "={{ $(\"Whatsapp\").first().json.body.data.key.remoteJid }}",
            "messageText": "={{ $('Parse VIP Intent').first().json.reply }}",
            "options_message": {}
        },
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [560, 2920],
        "id": "vip-send-ai-reply-001",
        "name": "Send VIP AI Reply",
        "credentials": {
            "evolutionApi": {
                "id": "IGwXyU5Jbou5S5V3",
                "name": "Business Number"
            }
        }
    }
]

# Add all VIP nodes
nodes.extend(vip_nodes)
print(f"OK: Added {len(vip_nodes)} VIP nodes")

# --- VIP Connections ---
# Is VIP? true (index 0) -> Get VIP Settings
connections["Is VIP?"]["main"][0] = [{"node": "Get VIP Settings", "type": "main", "index": 0}]

# Get VIP Settings -> VIP Message Type
connections["Get VIP Settings"] = {"main": [[{"node": "VIP Message Type", "type": "main", "index": 0}]]}

# VIP Message Type: Reaction(0)->Update VIP Reacted, Text(1)->Classify, Audio(2)->Classify, Photos(3)->Classify, Stickers(4)->Classify
connections["VIP Message Type"] = {
    "main": [
        [{"node": "Update VIP Reacted", "type": "main", "index": 0}],    # Reaction
        [{"node": "Classify VIP Intent", "type": "main", "index": 0}],   # Text
        [{"node": "Classify VIP Intent", "type": "main", "index": 0}],   # Audio
        [{"node": "Classify VIP Intent", "type": "main", "index": 0}],   # Photos
        [{"node": "Classify VIP Intent", "type": "main", "index": 0}]    # Stickers
    ]
}

# Update VIP Reacted -> VIP Reaction AI
connections["Update VIP Reacted"] = {"main": [[{"node": "VIP Reaction AI", "type": "main", "index": 0}]]}

# VIP Reaction AI -> Send VIP Reaction Reply
connections["VIP Reaction AI"] = {"main": [[{"node": "Send VIP Reaction Reply", "type": "main", "index": 0}]]}

# Classify VIP Intent -> Parse VIP Intent
connections["Classify VIP Intent"] = {"main": [[{"node": "Parse VIP Intent", "type": "main", "index": 0}]]}

# Parse VIP Intent -> VIP Intent Router
connections["Parse VIP Intent"] = {"main": [[{"node": "VIP Intent Router", "type": "main", "index": 0}]]}

# VIP Intent Router: Will Attend(0)->Update Will Attend, Not Attending(1)->Update Not, Inquiring(2)->Update Inq
connections["VIP Intent Router"] = {
    "main": [
        [{"node": "Update VIP Will Attend", "type": "main", "index": 0}],
        [{"node": "Update VIP Not Attending", "type": "main", "index": 0}],
        [{"node": "Update VIP Inquiring", "type": "main", "index": 0}]
    ]
}

# All Update nodes -> Send VIP AI Reply
connections["Update VIP Will Attend"] = {"main": [[{"node": "Send VIP AI Reply", "type": "main", "index": 0}]]}
connections["Update VIP Not Attending"] = {"main": [[{"node": "Send VIP AI Reply", "type": "main", "index": 0}]]}
connections["Update VIP Inquiring"] = {"main": [[{"node": "Send VIP AI Reply", "type": "main", "index": 0}]]}

print("OK: Added all VIP connections")

# ======================================================================
# Save
# ======================================================================
with open("current_workflow.json", "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=4, ensure_ascii=False)

print("\nDone! Changes:")
print("  1. Switch3 now has Reaction output (index 0)")
print("  2. Full VIP AI system added after Is VIP? node")
print("     Flow: Is VIP? -> Get VIP Settings -> VIP Message Type ->")
print("       Reaction: Update VIP Reacted -> VIP Reaction AI -> Send VIP Reaction Reply")
print("       Text/Audio/Photos/Stickers: Classify VIP Intent -> Parse VIP Intent -> VIP Intent Router ->")
print("         Update Status -> Send VIP AI Reply")
