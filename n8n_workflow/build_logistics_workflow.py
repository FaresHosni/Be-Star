"""
build_logistics_workflow.py

V2 Update: Single Webhook Router Architecture
يبني workflow لموظف لوجستيات التشغيل (AI Logistics Coordinator)
يعتمد على webhook واحد (bestar-whatsapp) ويقوم بتوجيه الرسائل:
1. المدير -> مساعد المدير
2. الجروب المحدد -> مساعد الجروب
3. عملاء -> (مسار مستقبلي للحجز)

يتضمن:
1. Webhook موحد (bestar-whatsapp)
2. Router لتوجيه الرسائل بناءً على المرسل
3. AI Agents (Group & Manager)
4. Trigger للتذكيرات (مستقل)
"""
import json
import os
import uuid

DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(DIR, "logistics_coordinator_v1.json")

# ── Platform API base URL
BACKEND = "http://38.242.139.159:3005"

# ── Evolution API credentials
EVOLUTION_CREDS = {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}
AZURE_CREDS = {"id": "dHqEdXN0XQ09LqJi", "name": "Azure OpenAI"}

def uid():
    return str(uuid.uuid4())

# ═══════════════════════════════════════════
# بناء الـ Nodes
# ═══════════════════════════════════════════

nodes = []
connections = {}

# ── 1. Webhook الموحد: bestar-whatsapp ─────────────────────────
WEBHOOK_ID = "d8fa5154-f391-43c2-ad0c-f5c7b3eb2737"
nodes.append({
    "parameters": {
        "httpMethod": "POST",
        "path": "bestar-whatsapp",
        "responseMode": "responseNode",
        "options": {}
    },
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [0, 600],
    "id": uid(),
    "name": "Whatsapp",
    "webhookId": WEBHOOK_ID,
})

# ── 2. استخراج بيانات الرسالة (Unified) ────────────────────────
nodes.append({
    "parameters": {
        "mode": "raw",
        "jsonOutput": '={\n'
            '  "remoteJid": "{{ $json.body.data.key.remoteJid }}",\n'
            '  "sender_phone": "{{ $json.body.data.key.participant || $json.body.data.key.remoteJid }}",\n'
            '  "sender_name": "{{ $json.body.data.pushName || \'مجهول\' }}",\n'
            '  "message_text": "{{ $json.body.data.message.conversation || $json.body.data.message.extendedTextMessage?.text || \'\' }}",\n'
            '  "instance": "{{ $json.body.instance }}",\n'
            '  "is_group": {{ $json.body.data.key.remoteJid?.includes("@g.us") || false }}\n'
            '}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [240, 600],
    "id": uid(),
    "name": "Extract Message Data"
})

connections["Whatsapp"] = {
    "main": [[{"node": "Extract Message Data", "type": "main", "index": 0}]]
}

# ── 3. فلتر مبدئي للرسائل الفارغة ──────────────────────────────
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{
                "id": uid(),
                "leftValue": "={{ $json.message_text }}",
                "rightValue": "",
                "operator": {"type": "string", "operation": "isNotEmpty"}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [460, 600],
    "id": uid(),
    "name": "Is Not Empty?"
})

connections["Extract Message Data"] = {
    "main": [[{"node": "Is Not Empty?", "type": "main", "index": 0}]]
}

# ── 4. جلب الإعدادات (لتحديد التوجيه) ──────────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/checklist/settings",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [680, 600],
    "id": uid(),
    "name": "Get Routing Settings",
    "continueOnFail": True,
})

connections["Is Not Empty?"] = {
    "main": [
        [{"node": "Get Routing Settings", "type": "main", "index": 0}],
        [] # Empty messages -> Ignore
    ]
}

# ── 5. Router: توجيه الرسالة (Switch) ──────────────────────────
nodes.append({
   "parameters": {
      "rules": {
         "values": [
            {
               "id": uid(),
               # Route 1: Manager
               "v": "={{ $json.manager_phone + '@s.whatsapp.net' }}",
               "operator": "equal",
               "column": "={{ $('Extract Message Data').item.json.remoteJid }}"
            },
            {
               "id": uid(),
               # Route 2: Group
               "v": "={{ $json.whatsapp_group_id }}",
               "operator": "equal",
               "column": "={{ $('Extract Message Data').item.json.remoteJid }}"
            }
         ]
      },
      "fallbackSettings": { "fallbackMode": "unusedValue" } # Output 3: Clients (Default)
   },
   "type": "n8n-nodes-base.switch",
   "typeVersion": 3,
   "position": [900, 600],
   "id": uid(),
   "name": "Router"
})

connections["Get Routing Settings"] = {
    "main": [[{"node": "Router", "type": "main", "index": 0}]]
}

# ═══════════════════════════════════════════
# المسار 1: المدير (Manager Flow) (Output Index 0)
# ═══════════════════════════════════════════

# 1.1 جلب بيانات الشكاوى للمدير
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/complaints/summary",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [1150, 400],
    "id": uid(),
    "name": "Get Data for Manager",
    "continueOnFail": True,
})

# 1.2 جلب المهام للمدير
nodes.append({
    "parameters": {
        "url": f"={BACKEND}/api/checklist/?date_filter={{{{ new Date().toISOString().split('T')[0] }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [1350, 400],
    "id": uid(),
    "name": "Get Tasks for Manager",
    "continueOnFail": True,
})

connections["Get Data for Manager"] = {
    "main": [[{"node": "Get Tasks for Manager", "type": "main", "index": 0}]]
}

# 1.3 AI Agent للمدير
MANAGER_AI_PROMPT = """أنت مساعد ذكي للمدير. بتديله تقارير وملخصات عن شغل اليوم.

# بيانات الشكاوى:
{{ $('Get Data for Manager').first().json | stringify }}

# مهام اليوم:
{{ $('Get Tasks for Manager').first().json | stringify }}

# قواعدك:
- كلامك بالعربي المصري
- لو المدير سأل "إيه المشاكل؟" أو "فيه شكاوى؟" → اعرض الشكاوى المفتوحة بالتفصيل
- لو سأل "إيه حالة المهام؟" → اعرض ملخص المهام (مكتملة/معلقة)
- لو سأل سؤال عام → جاوبه بناءً على البيانات المتاحة
- كن مختصر ومحترف
- استخدم الإيموجي بشكل معتدل
"""

nodes.append({
    "parameters": {
        "promptType": "define",
        "text": "={{ $('Extract Message Data').item.json.message_text }}",
        "options": {
            "systemMessage": MANAGER_AI_PROMPT,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.7,
    "position": [1550, 400],
    "id": uid(),
    "name": "Manager AI Agent"
})

connections["Get Tasks for Manager"] = {
    "main": [[{"node": "Manager AI Agent", "type": "main", "index": 0}]]
}

# 1.4 Azure OpenAI (Manager)
nodes.append({
    "parameters": {
        "model": "gpt-4o-mini",
        "options": {"temperature": 0.3}
    },
    "type": "@n8n/n8n-nodes-langchain.lmChatAzureOpenAi",
    "typeVersion": 1,
    "position": [1400, 600],
    "id": uid(),
    "name": "Azure OpenAI (Manager)",
    "credentials": {"azureOpenAiApi": AZURE_CREDS}
})

connections["Azure OpenAI (Manager)"] = {
    "ai_languageModel": [[{"node": "Manager AI Agent", "type": "ai_languageModel", "index": 0}]]
}

# 1.5 إرسال رد للمدير
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Message Data').item.json.instance }}",
        "remoteJid": "={{ $('Extract Message Data').item.json.remoteJid }}",
        "messageText": "={{ $json.output }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1800, 400],
    "id": uid(),
    "name": "Send Reply to Manager",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Manager AI Agent"] = {
    "main": [[{"node": "Send Reply to Manager", "type": "main", "index": 0}]]
}


# ═══════════════════════════════════════════
# المسار 2: الجروب (Group Flow) (Output Index 1)
# ═══════════════════════════════════════════

# 2.1 جلب مهام اليوم للجروب
nodes.append({
    "parameters": {
        "url": f"={BACKEND}/api/checklist/?date_filter={{{{ new Date().toISOString().split('T')[0] }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [1150, 800],
    "id": uid(),
    "name": "Get Group Tasks",
    "continueOnFail": True,
})

# 2.2 جلب ملخص الشكاوى للجروب
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/complaints/summary",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [1350, 800],
    "id": uid(),
    "name": "Get Group Complaints",
    "continueOnFail": True,
})

connections["Get Group Tasks"] = {
    "main": [[{"node": "Get Group Complaints", "type": "main", "index": 0}]]
}

# 2.3 AI Agent للجروب
AI_SYSTEM_PROMPT = """أنت موظف لوجستيات تشغيل ذكي (AI Logistics Coordinator) تعمل في جروب واتساب لإدارة الإيفنتات.

# دورك:
1. **متابعة إتمام المهام**: لما حد يقول إنه خلّص مهمة، تتحقق من اسمها في قائمة المهام وتسأله "هل أنت متأكد إنك أنهيت مهمة [اسم المهمة]؟" ولو أكد تعمل عليها علامة ✅
2. **استقبال الشكاوى**: لو حد قدّم شكوى أو مشكلة، تسجلها فوراً وتصعدها للمدير
3. **الرد على الاستفسارات**: لو حد سأل عن المهام أو الأحداث تجاوبه

# المهام المتاحة اليوم:
{{ $('Get Group Tasks').first().json | stringify }}

# ملخص الشكاوى:
{{ $('Get Group Complaints').first().json | stringify }}

# إعدادات:
{{ $('Get Routing Settings').first().json | stringify }}

# قواعد مهمة:
- كلامك يكون بالعربي المصري
- لما حد يقول "خلصت" أو "أنهيت" أو "تمت" مع اسم مهمة → استخدم أداة البحث عن المهمة
- لما تلاقي المهمة → اسأل "هل أنت متأكد إنك أنهيت مهمة [الاسم]؟"
- لو أكد → استخدم أداة تعليم المهمة كمكتملة
- لو فيه شكوى أو مشكلة → استخدم أداة تسجيل الشكوى
- كن محترف ومختصر في ردودك
"""

nodes.append({
    "parameters": {
        "promptType": "define",
        "text": "={{ $('Extract Message Data').item.json.message_text }}",
        "options": {
            "systemMessage": AI_SYSTEM_PROMPT,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.7,
    "position": [1550, 800],
    "id": uid(),
    "name": "Group AI Agent"
})

connections["Get Group Complaints"] = {
    "main": [[{"node": "Group AI Agent", "type": "main", "index": 0}]]
}

# 2.4 Azure OpenAI (Group)
nodes.append({
    "parameters": {
        "model": "gpt-4o-mini",
        "options": {"temperature": 0.3}
    },
    "type": "@n8n/n8n-nodes-langchain.lmChatAzureOpenAi",
    "typeVersion": 1,
    "position": [1400, 1000],
    "id": uid(),
    "name": "Azure OpenAI (Group)",
    "credentials": {"azureOpenAiApi": AZURE_CREDS}
})

connections["Azure OpenAI (Group)"] = {
    "ai_languageModel": [[{"node": "Group AI Agent", "type": "ai_languageModel", "index": 0}]]
}

# 2.5 Tools للجروب
# Search Task Tool
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة للبحث عن مهمة بالاسم. أرسل task_name.",
        "method": "GET",
        "url": f"={BACKEND}/api/checklist/search?task_name={{{{ $fromAI('task_name', '') }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequestTool", "typeVersion": 4.4, "position": [1350, 1200], "id": uid(), "name": "Search Task Tool"
})

# Complete Task Tool
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة لتعليم مهمة كمكتملة. أرسل task_id.",
        "method": "PUT",
        "url": f"={BACKEND}/api/checklist/{{{{ $fromAI('task_id', '') }}}}/toggle",
        "sendBody": True, "specifyBody": "json",
        "jsonBody": '={\n  "is_completed": true,\n  "completed_by_phone": "{{ $(\'Extract Message Data\').item.json.sender_phone }}",\n  "completed_by_name": "{{ $(\'Extract Message Data\').item.json.sender_name }}"\n}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequestTool", "typeVersion": 4.4, "position": [1550, 1200], "id": uid(), "name": "Complete Task Tool"
})

# Register Complaint Tool
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة لتسجيل شكوى. أرسل complaint_text.",
        "method": "POST",
        "url": f"{BACKEND}/api/complaints/",
        "sendBody": True, "specifyBody": "json",
        "jsonBody": '={\n  "reporter_phone": "{{ $(\'Extract Message Data\').item.json.sender_phone }}",\n  "reporter_name": "{{ $(\'Extract Message Data\').item.json.sender_name }}",\n  "complaint_text": "{{ $fromAI(\'complaint_text\', \'\') }}"\n}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequestTool", "typeVersion": 4.4, "position": [1750, 1200], "id": uid(), "name": "Register Complaint Tool"
})

for tool in ["Search Task Tool", "Complete Task Tool", "Register Complaint Tool"]:
    connections[tool] = { "ai_tool": [[{"node": "Group AI Agent", "type": "ai_tool", "index": 0}]] }

# 2.6 إرسال رد للجروب
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Message Data').item.json.instance }}",
        "remoteJid": "={{ $('Extract Message Data').item.json.remoteJid }}",
        "messageText": "={{ $json.output }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1800, 800],
    "id": uid(),
    "name": "Send Reply to Group",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Group AI Agent"] = {
    "main": [[{"node": "Send Reply to Group", "type": "main", "index": 0}]]
}

# 2.7 تصعيد الشكوى للمدير (Check + Send)
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{ "id": uid(), "leftValue": "={{ $json.output }}", "rightValue": "شكوى", "operator": {"type": "string", "operation": "contains"} }],
            "combinator": "or"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [2000, 800], "id": uid(), "name": "Has Complaint?"
})

nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Message Data').item.json.instance }}",
        "remoteJid": "={{ $('Get Routing Settings').item.json.manager_phone + '@s.whatsapp.net' }}",
        "messageText": "=🔺 *شكوى جديدة!*\n\n👤 من: {{ $('Extract Message Data').item.json.sender_name }}\n📱 رقم: {{ $('Extract Message Data').item.json.sender_phone }}\n\n💬 {{ $('Extract Message Data').item.json.message_text }}\n\n⏰ {{ new Date().toLocaleString('ar-EG', {timeZone: 'Africa/Cairo'}) }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi", "typeVersion": 1, "position": [2200, 700], "id": uid(), "name": "Escalate to Manager",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Send Reply to Group"] = { "main": [[{"node": "Has Complaint?", "type": "main", "index": 0}]] }
connections["Has Complaint?"] = { "main": [[{"node": "Escalate to Manager", "type": "main", "index": 0}], []] }


# ═══════════════════════════════════════════
# ربط الـ Router بالمسارين
# ═══════════════════════════════════════════

connections["Router"] = {
    "main": [
        [{"node": "Get Data for Manager", "type": "main", "index": 0}], # Route 1: Manager
        [{"node": "Get Group Tasks", "type": "main", "index": 0}],      # Route 2: Group
        [{"node": "Manual Client Handling", "type": "main", "index": 0}] # Route 3: Client (Future)
    ]
}

# ═══════════════════════════════════════════
# المسار 3: العملاء (Client Flow) (Output Index 2)
# ═══════════════════════════════════════════
nodes.append({
    "parameters": {},
    "type": "n8n-nodes-base.noOp",
    "typeVersion": 1,
    "position": [1150, 1200],
    "id": uid(),
    "name": "Manual Client Handling"
})

# ═══════════════════════════════════════════
# جزء التذكيرات (Agenda Reminders) - مستقل
# ═══════════════════════════════════════════

# Every Minute Trigger
nodes.append({
    "parameters": { "rule": { "interval": [{"field": "minutes", "minutesInterval": 1}] } },
    "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [0, 1600], "id": uid(), "name": "Every Minute Trigger"
})

# Check Upcoming Events
nodes.append({
    "parameters": { "url": f"{BACKEND}/api/agenda/upcoming?minutes=10", "options": {"timeout": 8000} },
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3, "position": [200, 1600], "id": uid(), "name": "Check Upcoming Events", "continueOnFail": True
})

# Has Upcoming Events?
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{ "id": uid(), "leftValue": "={{ $json.count }}", "rightValue": 0, "operator": {"type": "number", "operation": "gt"} }],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [400, 1600], "id": uid(), "name": "Has Upcoming Events?"
})

# Get Settings for Reminder
nodes.append({
    "parameters": { "url": f"{BACKEND}/api/checklist/settings", "options": {"timeout": 8000} },
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3, "position": [600, 1500], "id": uid(), "name": "Get Settings for Reminder", "continueOnFail": True
})

# Split Events
nodes.append({
    "parameters": { "fieldToSplitOut": "={{ $('Check Upcoming Events').first().json.upcoming }}", "options": {} },
    "type": "n8n-nodes-base.splitOut", "typeVersion": 1, "position": [800, 1500], "id": uid(), "name": "Split Events"
})

# Send Reminder to Group
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "Mahmoud Magdy", # Used from user's provided data
        "remoteJid": "={{ $('Get Settings for Reminder').first().json.whatsapp_group_id }}",
        "messageText": "=⏰ *تذكير!*\n\n📌 باقي 10 دقائق على:\n\n🎯 *{{ $json.title }}*\n📍 المكان: {{ $json.location || 'غير محدد' }}\n🕐 الوقت: {{ new Date($json.event_time).toLocaleTimeString('ar-EG', {hour: '2-digit', minute: '2-digit', timeZone: 'Africa/Cairo'}) }}\n{{ $json.description ? '\\n📝 ' + $json.description : '' }}\n\nاستعدوا! 🚀",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi", "typeVersion": 1, "position": [1000, 1500], "id": uid(), "name": "Send Reminder to Group",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

# Mark Reminder Sent
nodes.append({
    "parameters": { "method": "PUT", "url": f"={BACKEND}/api/agenda/{{{{ $json.id }}}}/reminder-sent", "options": {} },
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3, "position": [1200, 1500], "id": uid(), "name": "Mark Reminder Sent"
})

connections["Every Minute Trigger"] = { "main": [[{"node": "Check Upcoming Events", "type": "main", "index": 0}]] }
connections["Check Upcoming Events"] = { "main": [[{"node": "Has Upcoming Events?", "type": "main", "index": 0}]] }
connections["Has Upcoming Events?"] = { "main": [[{"node": "Get Settings for Reminder", "type": "main", "index": 0}], []] }
connections["Get Settings for Reminder"] = { "main": [[{"node": "Split Events", "type": "main", "index": 0}]] }
connections["Split Events"] = { "main": [[{"node": "Send Reminder to Group", "type": "main", "index": 0}]] }
connections["Send Reminder to Group"] = { "main": [[{"node": "Mark Reminder Sent", "type": "main", "index": 0}]] }


# ═══════════════════════════════════════════
# تجميع الـ Workflow
# ═══════════════════════════════════════════

workflow = {
    "nodes": nodes,
    "connections": connections,
    "meta": {
        "templateCredsSetupCompleted": True,
        "instanceId": uid()
    }
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"============================================================")
print(f"[DONE] Saved: {OUTPUT}")
print(f"[DONE] Total nodes: {len(nodes)}")
print(f"[DONE] Total connections: {len(connections)}")
print(f"============================================================")
