"""
Update VIP workflow nodes:
1. Expand VIP Message Type switch to handle Audio/Photos/Stickers
2. Convert Classify VIP Intent to full AI Agent (classify + generate reply)
3. Add AI-powered reaction reply (instead of fixed text)
4. Simplify send nodes to use AI-generated reply
"""
import json
import copy

with open("current_workflow.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

nodes = workflow["nodes"]
connections = workflow["connections"]

# ═══════════════════════════════════════════════════════════════
# 1. UPDATE VIP Message Type switch — add Audio, Photos, Stickers outputs
# ═══════════════════════════════════════════════════════════════

for node in nodes:
    if node.get("name") == "VIP Message Type":
        rules = node["parameters"]["rules"]["values"]
        # Add Audio condition
        rules.append({
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
        })
        # Add Photos condition
        rules.append({
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
        })
        # Add Stickers condition
        rules.append({
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
        })
        print("✅ Updated VIP Message Type switch with Audio/Photos/Stickers")
        break

# ═══════════════════════════════════════════════════════════════
# 2. UPDATE Classify VIP Intent → Full AI Agent with reply generation
# ═══════════════════════════════════════════════════════════════

ai_system_prompt = (
    "أنت مساعد مهذب وراقي جداً لإدارة دعوات كبار الزوار لفعالية خاصة.\\n\\n"
    "📋 معلومات الإيفنت:\\n"
    "{{ $('Get VIP Settings').first().json.inquiry_reply }}\\n\\n"
    "👍 أسلوب الرد على الريأكشن:\\n"
    "{{ $('Get VIP Settings').first().json.reaction_reply }}\\n\\n"
    "✅ أسلوب رسالة القبول:\\n"
    "{{ $('Get VIP Settings').first().json.accept_reply }}\\n\\n"
    "😔 أسلوب رسالة الرفض:\\n"
    "{{ $('Get VIP Settings').first().json.decline_reply }}\\n\\n"
    "👤 اسم الضيف: {{ $('Check Is VIP').first().json.guest.name }}\\n\\n"
    "مهمتك:\\n"
    "1. صنف رد الضيف لواحد من 3 تصنيفات:\\n"
    "   - will_attend: لو قال هحضر أو إن شاء الله أو موافق أو بعت تفاعل إيجابي\\n"
    "   - not_attending: لو قال مش هقدر أو مشغول أو معلش\\n"
    "   - inquiring: لو سأل عن تفاصيل أو مكان أو وقت أو أي استفسار\\n"
    "2. اكتب رد مهذب ومحترف ومنسق يناسب الموقف\\n"
    "3. استخدم اسم الضيف في الرد\\n"
    "4. لو بيسأل → رد من معلومات الإيفنت (مش تأليف!)\\n"
    "5. لو موافق → رد بأسلوب رسالة القبول مع ✅ واسمه\\n"
    "6. لو معتذر → رد بأسلوب رسالة الرفض مع 😔 واسمه\\n"
    "7. ضيف إيموجي مناسبة في الرد\\n\\n"
    "⚠️ رد بـ JSON فقط بالشكل ده:\\n"
    "{\\\\\\\"intent\\\\\\\": \\\\\\\"will_attend\\\\\\\", \\\\\\\"reply\\\\\\\": \\\\\\\"الرد المنسق هنا\\\\\\\"}\\n\\n"
    "ممنوع تكتب أي حاجة بره الـ JSON."
)

# Get the user message expression - handle text messages
user_message_expr = (
    "{{ $('Whatsapp').first().json.body.data.message.conversation "
    "?? $('Whatsapp').first().json.body.data.message.extendedTextMessage.text "
    "?? 'الضيف بعت تفاعل/ريأكشن/ستيكر/صورة على الدعوة' }}"
)

ai_json_body = (
    '={"model":"gpt-4.1-mini","messages":['
    '{"role":"system","content":"' + ai_system_prompt + '"},'
    '{"role":"user","content":"' + user_message_expr + '"}'
    '],"max_tokens":300,"temperature":0.7}'
)

for node in nodes:
    if node.get("name") == "Classify VIP Intent":
        node["parameters"]["jsonBody"] = ai_json_body
        print("✅ Updated Classify VIP Intent to full AI Agent")
        break

# ═══════════════════════════════════════════════════════════════
# 3. UPDATE Parse VIP Intent → Also extract reply
# ═══════════════════════════════════════════════════════════════

new_parse_code = (
    'const raw = $input.first().json.choices[0].message.content;\n'
    'let intent = "inquiring";\n'
    'let reply = "";\n'
    'try {\n'
    '  const parsed = JSON.parse(raw.trim());\n'
    '  intent = parsed.intent || "inquiring";\n'
    '  reply = parsed.reply || "";\n'
    '} catch(e) {\n'
    '  if (raw.includes("will_attend")) intent = "will_attend";\n'
    '  else if (raw.includes("not_attending")) intent = "not_attending";\n'
    '  else intent = "inquiring";\n'
    '  reply = raw.replace(/[{}"\\\\/]/g, "").trim();\n'
    '}\n'
    'return [{ json: { intent, reply } }];'
)

for node in nodes:
    if node.get("name") == "Parse VIP Intent":
        node["parameters"]["jsCode"] = new_parse_code
        print("✅ Updated Parse VIP Intent to extract reply")
        break

# ═══════════════════════════════════════════════════════════════
# 4. ADD a single "Send VIP AI Reply" node (replaces separate send nodes for each intent)
# ═══════════════════════════════════════════════════════════════

# Add a unified send node that sends the AI-generated reply
send_ai_reply_node = {
    "parameters": {
        "resource": "message-api",
        "operation": "send-text",
        "instanceName": "={{ $(\"Whatsapp\").first().json.body.instance }}",
        "remoteJid": "={{ $(\"Whatsapp\").first().json.body.data.key.remoteJid }}",
        "messageText": "={{ $('Parse VIP Intent').first().json.reply }}"
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [-58950, 33300],
    "id": "vip-send-ai-reply-001",
    "name": "Send VIP AI Reply",
    "credentials": {
        "evolutionApi": {
            "id": "IGwXyU5Jbou5S5V3",
            "name": "Business Number"
        }
    }
}

nodes.append(send_ai_reply_node)
print("✅ Added Send VIP AI Reply node")

# ═══════════════════════════════════════════════════════════════
# 5. UPDATE Connections - route all 3 intent update nodes to Send VIP AI Reply
# Also route Audio/Photos/Stickers from VIP Message Type to Classify VIP Intent
# ═══════════════════════════════════════════════════════════════

# Connect VIP Message Type Audio/Photos/Stickers outputs → Classify VIP Intent
# Output 0 = Reaction, Output 1 = Text, Output 2 = Audio, Output 3 = Photos, Output 4 = Stickers
vip_msg_connections = connections.get("VIP Message Type", {}).get("main", [])
# We need 5 outputs now
while len(vip_msg_connections) < 5:
    vip_msg_connections.append([])

# Outputs 2,3,4 (Audio, Photos, Stickers) → Classify VIP Intent
for i in [2, 3, 4]:
    vip_msg_connections[i] = [{"node": "Classify VIP Intent", "type": "main", "index": 0}]

connections["VIP Message Type"]["main"] = vip_msg_connections
print("✅ Connected Audio/Photos/Stickers to AI Agent")

# Connect all 3 update nodes → Send VIP AI Reply
for update_node_name in ["Update VIP Will Attend", "Update VIP Not Attending", "Update VIP Inquiring"]:
    connections[update_node_name] = {
        "main": [[{"node": "Send VIP AI Reply", "type": "main", "index": 0}]]
    }
print("✅ Connected all update nodes to Send VIP AI Reply")

# Remove old Send VIP Inquiry Reply connection (it's replaced by Send VIP AI Reply)
if "Send VIP Inquiry Reply" in connections:
    del connections["Send VIP Inquiry Reply"]

# ═══════════════════════════════════════════════════════════════
# 6. UPDATE Reaction Reply — use AI to generate response
# Replace Send VIP Reaction Reply fixed text with AI call
# ═══════════════════════════════════════════════════════════════

# Add a new node: VIP Reaction AI that generates a reply for reactions
reaction_ai_system = (
    "أنت مساعد مهذب لكبار الزوار. الضيف بعت ريأكشن (تفاعل) على دعوته.\\n\\n"
    "👤 اسم الضيف: {{ $('Check Is VIP').first().json.guest.name }}\\n\\n"
    "👍 أسلوب الرد:\\n"
    "{{ $('Get VIP Settings').first().json.reaction_reply }}\\n\\n"
    "اكتب رد مهذب وقصير ومنسق مستلهم من أسلوب الرد. استخدم اسم الضيف. ضيف إيموجي مناسبة.\\n"
    "رد بالنص مباشرة بدون JSON."
)

reaction_ai_json = (
    '={"model":"gpt-4.1-mini","messages":['
    '{"role":"system","content":"' + reaction_ai_system + '"},'
    '{"role":"user","content":"الضيف عمل ريأكشن على الدعوة"}'
    '],"max_tokens":200,"temperature":0.8}'
)

# Add VIP Reaction AI node
reaction_ai_node = {
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
        "jsonBody": reaction_ai_json,
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [-59650, 32950],
    "id": "vip-reaction-ai-001",
    "name": "VIP Reaction AI"
}
nodes.append(reaction_ai_node)

# Update Send VIP Reaction Reply to use AI output
for node in nodes:
    if node.get("name") == "Send VIP Reaction Reply":
        node["parameters"]["messageText"] = "={{ $json.choices[0].message.content }}"
        print("✅ Updated Send VIP Reaction Reply to use AI output")
        break

# Update connections: Update VIP Reacted → VIP Reaction AI → Send VIP Reaction Reply
connections["Update VIP Reacted"] = {
    "main": [[{"node": "VIP Reaction AI", "type": "main", "index": 0}]]
}
connections["VIP Reaction AI"] = {
    "main": [[{"node": "Send VIP Reaction Reply", "type": "main", "index": 0}]]
}
print("✅ Connected Update VIP Reacted → VIP Reaction AI → Send VIP Reaction Reply")

# ═══════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════

with open("current_workflow.json", "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=4)

print("\n🎉 Workflow updated successfully!")
print("Changes:")
print("  1. VIP Message Type now handles Audio/Photos/Stickers")
print("  2. Classify VIP Intent is now a full AI Agent (classify + reply)")
print("  3. Parse VIP Intent extracts both intent and reply")
print("  4. Added Send VIP AI Reply node (unified for all intents)")
print("  5. Reaction reply now uses AI instead of fixed text")
