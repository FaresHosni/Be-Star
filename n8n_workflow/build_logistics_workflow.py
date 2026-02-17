"""
build_logistics_workflow.py

يبني workflow جديد لموظف لوجستيات التشغيل (AI Logistics Coordinator)
يتضمن:
1. Webhook لاستقبال رسائل جروب واتساب
2. AI Agent لتصنيف النية (إتمام مهمة / شكوى / سؤال عام)
3. التحقق من المهام على المنصة وتأكيد الإتمام
4. Trigger كل دقيقة للتذكيرات (10 دقائق قبل الحدث)
5. معالجة الشكاوى وتصعيدها للمدير
6. محادثة المدير مع AI للملخصات

ملاحظة: هذا workflow مستقل تماماً ولا يعدل على أي workflow موجود
"""
import json
import os
import uuid

DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(DIR, "logistics_coordinator_v1.json")

# ── Platform API base URL (same as existing workflows)
BACKEND = "http://38.242.139.159:3005"

# ── Evolution API credentials (same as existing)
EVOLUTION_CREDS = {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}


def uid():
    return str(uuid.uuid4())


# ═══════════════════════════════════════════
# بناء الـ Nodes
# ═══════════════════════════════════════════

nodes = []
connections = {}

# ── 1. Webhook: استقبال رسائل جروب واتساب (WhatsApp Group) ──────
WEBHOOK_ID = uid()
nodes.append({
    "parameters": {
        "httpMethod": "POST",
        "path": "logistics-group-webhook",
        "responseMode": "responseNode",
        "options": {}
    },
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [0, 300],
    "id": uid(),
    "name": "WhatsApp Group Webhook",
    "webhookId": WEBHOOK_ID,
})

# ── 2. استخراج بيانات الرسالة ──────────────────────────────────
nodes.append({
    "parameters": {
        "mode": "raw",
        "jsonOutput": '={\n'
            '  "sender_phone": "{{ $json.body.data.key.participant || $json.body.data.key.remoteJid }}",\n'
            '  "sender_name": "{{ $json.body.data.pushName || \'مجهول\' }}",\n'
            '  "message_text": "{{ $json.body.data.message.conversation || $json.body.data.message.extendedTextMessage?.text || \'\' }}",\n'
            '  "group_id": "{{ $json.body.data.key.remoteJid }}",\n'
            '  "instance": "{{ $json.body.instance }}",\n'
            '  "is_group": {{ $json.body.data.key.remoteJid?.includes("@g.us") || false }}\n'
            '}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [240, 300],
    "id": uid(),
    "name": "Extract Message Data"
})

connections["WhatsApp Group Webhook"] = {
    "main": [[{"node": "Extract Message Data", "type": "main", "index": 0}]]
}

# ── 3. فلتر: هل الرسالة من جروب؟ ──────────────────────────────
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [
                {
                    "id": uid(),
                    "leftValue": "={{ $json.is_group }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals"}
                },
                {
                    "id": uid(),
                    "leftValue": "={{ $json.message_text }}",
                    "rightValue": "",
                    "operator": {"type": "string", "operation": "isNotEmpty"}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [480, 300],
    "id": uid(),
    "name": "Is Group Message?"
})

connections["Extract Message Data"] = {
    "main": [[{"node": "Is Group Message?", "type": "main", "index": 0}]]
}

# ── 4. جلب إعدادات اللوجستيات (Group ID + Manager Phone) ───────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/checklist/settings",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [720, 200],
    "id": uid(),
    "name": "Get Logistics Settings",
    "continueOnFail": True,
})

connections["Is Group Message?"] = {
    "main": [
        [{"node": "Get Logistics Settings", "type": "main", "index": 0}],
        [],  # false branch
    ]
}

# ── 4.5. فلتر: هل هو الجروب الصحيح؟ ──────────────────────────
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [
                {
                    "id": uid(),
                    "leftValue": "={{ $json.whatsapp_group_id }}",
                    "rightValue": "={{ $('Extract Message Data').item.json.group_id }}",
                    "operator": {"type": "string", "operation": "equals"}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [960, 200],
    "id": uid(),
    "name": "Is Correct Group?"
})

connections["Get Logistics Settings"] = {
    "main": [
        [{"node": "Is Correct Group?", "type": "main", "index": 0}],
        []
    ]
}

nodes.append({
    "parameters": {
        "url": f"={BACKEND}/api/checklist/?date_filter={{{{ new Date().toISOString().split('T')[0] }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [960, 200],
    "id": uid(),
    "name": "Get Today Tasks",
    "continueOnFail": True,
})

connections["Is Correct Group?"] = {
    "main": [
        [{"node": "Get Today Tasks", "type": "main", "index": 0}],
        []
    ]
}

# ── 6. جلب ملخص الشكاوى (لو المدير بيسأل) ────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/complaints/summary",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [960, 400],
    "id": uid(),
    "name": "Get Complaints Summary",
    "continueOnFail": True,
})

# ── 7. AI Agent - تصنيف + رد ──────────────────────────────────

AI_SYSTEM_PROMPT = """أنت موظف لوجستيات تشغيل ذكي (AI Logistics Coordinator) تعمل في جروب واتساب لإدارة الإيفنتات.

# دورك:
1. **متابعة إتمام المهام**: لما حد يقول إنه خلّص مهمة، تتحقق من اسمها في قائمة المهام وتسأله "هل أنت متأكد إنك أنهيت مهمة [اسم المهمة]؟" ولو أكد تعمل عليها علامة ✅
2. **استقبال الشكاوى**: لو حد قدّم شكوى أو مشكلة، تسجلها فوراً وتصعدها للمدير
3. **الرد على الاستفسارات**: لو حد سأل عن المهام أو الأحداث تجاوبه

# المهام المتاحة اليوم:
{{ $('Get Today Tasks').first().json | stringify }}

# ملخص الشكاوى:
{{ $('Get Complaints Summary').first().json | stringify }}

# إعدادات:
{{ $('Get Logistics Settings').first().json | stringify }}

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
        "text": "={{ $('Extract Message Data').first().json.message_text }}",
        "options": {
            "systemMessage": AI_SYSTEM_PROMPT,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.7,
    "position": [1200, 300],
    "id": uid(),
    "name": "Logistics AI Agent"
})

connections["Get Today Tasks"] = {
    "main": [[{"node": "Get Complaints Summary", "type": "main", "index": 0}]]
}

connections["Get Complaints Summary"] = {
    "main": [[{"node": "Logistics AI Agent", "type": "main", "index": 0}]]
}

# ── 8. Azure OpenAI Chat Model للـ Agent ────────────────────────
nodes.append({
    "parameters": {
        "model": "gpt-4o-mini",
        "options": {
            "temperature": 0.3,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.lmChatAzureOpenAi",
    "typeVersion": 1,
    "position": [1100, 520],
    "id": uid(),
    "name": "Azure OpenAI (Logistics)",
    "credentials": {
        "azureOpenAiApi": {"id": "dHqEdXN0XQ09LqJi", "name": "Azure OpenAI"}
    }
})

connections["Azure OpenAI (Logistics)"] = {
    "ai_languageModel": [[{"node": "Logistics AI Agent", "type": "ai_languageModel", "index": 0}]]
}

# ── 9. Tool: البحث عن مهمة بالاسم ──────────────────────────────
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة للبحث عن مهمة بالاسم في قائمة مهام اليوم. أرسل task_name (اسم المهمة أو جزء منه).",
        "method": "GET",
        "url": f"={BACKEND}/api/checklist/search?task_name={{{{ $fromAI('task_name', '') }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequestTool",
    "typeVersion": 4.4,
    "position": [1000, 680],
    "id": uid(),
    "name": "Search Task Tool"
})

connections["Search Task Tool"] = {
    "ai_tool": [[{"node": "Logistics AI Agent", "type": "ai_tool", "index": 0}]]
}

# ── 10. Tool: تعليم مهمة كمكتملة ───────────────────────────────
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة لتعليم مهمة كمكتملة بعد تأكيد العميل. أرسل task_id (رقم المهمة).",
        "method": "PUT",
        "url": f"={BACKEND}/api/checklist/{{{{ $fromAI('task_id', '') }}}}/toggle",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Content-Type", "value": "application/json"}
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n'
            '  "is_completed": true,\n'
            '  "completed_by_phone": "{{ $(\'Extract Message Data\').first().json.sender_phone }}",\n'
            '  "completed_by_name": "{{ $(\'Extract Message Data\').first().json.sender_name }}"\n'
            '}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequestTool",
    "typeVersion": 4.4,
    "position": [1200, 680],
    "id": uid(),
    "name": "Complete Task Tool"
})

connections["Complete Task Tool"] = {
    "ai_tool": [[{"node": "Logistics AI Agent", "type": "ai_tool", "index": 0}]]
}

# ── 11. Tool: تسجيل شكوى ──────────────────────────────────────
nodes.append({
    "parameters": {
        "toolDescription": "استخدم هذه الأداة لتسجيل شكوى جديدة من عميل. أرسل complaint_text (نص الشكوى).",
        "method": "POST",
        "url": f"{BACKEND}/api/complaints/",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Content-Type", "value": "application/json"}
        ]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": '={\n'
            '  "reporter_phone": "{{ $(\'Extract Message Data\').first().json.sender_phone }}",\n'
            '  "reporter_name": "{{ $(\'Extract Message Data\').first().json.sender_name }}",\n'
            '  "complaint_text": "{{ $fromAI(\'complaint_text\', \'\') }}"\n'
            '}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequestTool",
    "typeVersion": 4.4,
    "position": [1400, 680],
    "id": uid(),
    "name": "Register Complaint Tool"
})

connections["Register Complaint Tool"] = {
    "ai_tool": [[{"node": "Logistics AI Agent", "type": "ai_tool", "index": 0}]]
}

# ── 12. إرسال رد AI على واتساب ────────────────────────────────
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Message Data').first().json.instance }}",
        "remoteJid": "={{ $('Extract Message Data').first().json.group_id }}",
        "messageText": "={{ $json.output }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1500, 300],
    "id": uid(),
    "name": "Send AI Reply to Group",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Logistics AI Agent"] = {
    "main": [[{"node": "Send AI Reply to Group", "type": "main", "index": 0}]]
}

# ── 13. بعد إرسال الرد → تصعيد الشكوى للمدير (لو فيه شكوى) ──
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{
                "id": uid(),
                "leftValue": "={{ $json.output }}",
                "rightValue": "شكوى",
                "operator": {"type": "string", "operation": "contains"}
            }],
            "combinator": "or"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [1740, 300],
    "id": uid(),
    "name": "Has Complaint?"
})

connections["Send AI Reply to Group"] = {
    "main": [[{"node": "Has Complaint?", "type": "main", "index": 0}]]
}

# ── 14. إرسال الشكوى للمدير مباشرة ────────────────────────────
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Message Data').first().json.instance }}",
        "remoteJid": "={{ $('Get Logistics Settings').first().json.manager_phone + '@s.whatsapp.net' }}",
        "messageText": "=🔺 *شكوى جديدة!*\n\n👤 من: {{ $('Extract Message Data').first().json.sender_name }}\n📱 رقم: {{ $('Extract Message Data').first().json.sender_phone }}\n\n💬 {{ $('Extract Message Data').first().json.message_text }}\n\n⏰ {{ new Date().toLocaleString('ar-EG', {timeZone: 'Africa/Cairo'}) }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1980, 200],
    "id": uid(),
    "name": "Escalate to Manager",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Has Complaint?"] = {
    "main": [
        [{"node": "Escalate to Manager", "type": "main", "index": 0}],
        [],  # false - no complaint, do nothing
    ]
}

# ═══════════════════════════════════════════
# جزء التذكيرات (Agenda Reminders)
# ═══════════════════════════════════════════

# ── 15. Schedule Trigger: كل دقيقة ─────────────────────────────
nodes.append({
    "parameters": {
        "rule": {
            "interval": [{"field": "minutes", "minutesInterval": 1}]
        }
    },
    "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2,
    "position": [0, 800],
    "id": uid(),
    "name": "Every Minute Trigger"
})

# ── 16. جلب الأحداث القادمة (10 دقائق) ─────────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/agenda/upcoming?minutes=10",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [240, 800],
    "id": uid(),
    "name": "Check Upcoming Events",
    "continueOnFail": True,
})

connections["Every Minute Trigger"] = {
    "main": [[{"node": "Check Upcoming Events", "type": "main", "index": 0}]]
}

# ── 17. هل فيه أحداث قادمة؟ ────────────────────────────────────
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{
                "id": uid(),
                "leftValue": "={{ $json.count }}",
                "rightValue": 0,
                "operator": {"type": "number", "operation": "gt"}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [480, 800],
    "id": uid(),
    "name": "Has Upcoming Events?"
})

connections["Check Upcoming Events"] = {
    "main": [[{"node": "Has Upcoming Events?", "type": "main", "index": 0}]]
}

# ── 18. جلب إعدادات (للحصول على Group ID) ──────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/checklist/settings",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [720, 700],
    "id": uid(),
    "name": "Get Settings for Reminder",
    "continueOnFail": True,
})

connections["Has Upcoming Events?"] = {
    "main": [
        [{"node": "Get Settings for Reminder", "type": "main", "index": 0}],
        [],  # no events
    ]
}

# ── 19. Split items (كل حدث لوحده) ─────────────────────────────
nodes.append({
    "parameters": {
        "fieldToSplitOut": "={{ $('Check Upcoming Events').first().json.upcoming }}",
        "options": {}
    },
    "type": "n8n-nodes-base.splitOut",
    "typeVersion": 1,
    "position": [960, 700],
    "id": uid(),
    "name": "Split Events"
})

connections["Get Settings for Reminder"] = {
    "main": [[{"node": "Split Events", "type": "main", "index": 0}]]
}

# ── 20. إرسال تذكير للجروب ────────────────────────────────────
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('WhatsApp Group Webhook').first().json.body?.instance || 'default' }}",
        "remoteJid": "={{ $('Get Settings for Reminder').first().json.whatsapp_group_id }}",
        "messageText": "=⏰ *تذكير!*\n\n📌 باقي 10 دقائق على:\n\n🎯 *{{ $json.title }}*\n📍 المكان: {{ $json.location || 'غير محدد' }}\n🕐 الوقت: {{ new Date($json.event_time).toLocaleTimeString('ar-EG', {hour: '2-digit', minute: '2-digit', timeZone: 'Africa/Cairo'}) }}\n{{ $json.description ? '\\n📝 ' + $json.description : '' }}\n\nاستعدوا! 🚀",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1200, 700],
    "id": uid(),
    "name": "Send Reminder to Group",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Split Events"] = {
    "main": [[{"node": "Send Reminder to Group", "type": "main", "index": 0}]]
}

# ── 21. تعليم التذكير كمرسل ───────────────────────────────────
nodes.append({
    "parameters": {
        "method": "PUT",
        "url": f"={BACKEND}/api/agenda/{{{{ $json.id }}}}/reminder-sent",
        "options": {}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [1440, 700],
    "id": uid(),
    "name": "Mark Reminder Sent"
})

connections["Send Reminder to Group"] = {
    "main": [[{"node": "Mark Reminder Sent", "type": "main", "index": 0}]]
}

# ═══════════════════════════════════════════
# جزء محادثة المدير (Manager Private Chat)
# ═══════════════════════════════════════════

# ── 22. Webhook: رسائل المدير الخاصة ──────────────────────────
MANAGER_WEBHOOK_ID = uid()
nodes.append({
    "parameters": {
        "httpMethod": "POST",
        "path": "logistics-manager-webhook",
        "responseMode": "responseNode",
        "options": {}
    },
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [0, 1300],
    "id": uid(),
    "name": "Manager WhatsApp Webhook",
    "webhookId": MANAGER_WEBHOOK_ID,
})

# ── 23. استخراج بيانات رسالة المدير ────────────────────────────
nodes.append({
    "parameters": {
        "mode": "raw",
        "jsonOutput": '={\n'
            '  "manager_phone": "{{ $json.body.data.key.remoteJid }}",\n'
            '  "message_text": "{{ $json.body.data.message.conversation || $json.body.data.message.extendedTextMessage?.text || \'\' }}",\n'
            '  "instance": "{{ $json.body.instance }}"\n'
            '}\n',
        "options": {}
    },
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [240, 1300],
    "id": uid(),
    "name": "Extract Manager Message"
})

connections["Manager WhatsApp Webhook"] = {
    "main": [[{"node": "Extract Manager Message", "type": "main", "index": 0}]]
}

# ── 23.5. التحقق من هوية المدير ────────────────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/checklist/settings",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [480, 1300],
    "id": uid(),
    "name": "Get Manager Settings",
    "continueOnFail": True,
})

connections["Extract Manager Message"] = {
    "main": [[{"node": "Get Manager Settings", "type": "main", "index": 0}]]
}

nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [
                {
                    "id": uid(),
                    "leftValue": "={{ $json.manager_phone + '@s.whatsapp.net' }}",
                    "rightValue": "={{ $('Extract Manager Message').item.json.manager_phone }}",
                    "operator": {"type": "string", "operation": "equals"}
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [720, 1300],
    "id": uid(),
    "name": "Is Manager?"
})

connections["Get Manager Settings"] = {
    "main": [
        [{"node": "Is Manager?", "type": "main", "index": 0}],
        []
    ]
}

# ── 24. جلب البيانات للمدير ────────────────────────────────────
nodes.append({
    "parameters": {
        "url": f"{BACKEND}/api/complaints/summary",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [960, 1300],
    "id": uid(),
    "name": "Get Data for Manager",
    "continueOnFail": True,
})

connections["Is Manager?"] = {
    "main": [[{"node": "Get Data for Manager", "type": "main", "index": 0}]]
}



# ── 25. جلب مهام اليوم للمدير ──────────────────────────────────
nodes.append({
    "parameters": {
        "url": f"={BACKEND}/api/checklist/?date_filter={{{{ new Date().toISOString().split('T')[0] }}}}",
        "options": {"timeout": 8000}
    },
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.3,
    "position": [720, 1300],
    "id": uid(),
    "name": "Get Tasks for Manager",
    "continueOnFail": True,
})

connections["Get Data for Manager"] = {
    "main": [[{"node": "Get Tasks for Manager", "type": "main", "index": 0}]]
}

# ── 26. AI Agent للمدير ────────────────────────────────────────

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
        "text": "={{ $('Extract Manager Message').first().json.message_text }}",
        "options": {
            "systemMessage": MANAGER_AI_PROMPT,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.7,
    "position": [960, 1300],
    "id": uid(),
    "name": "Manager AI Agent"
})

connections["Get Tasks for Manager"] = {
    "main": [[{"node": "Manager AI Agent", "type": "main", "index": 0}]]
}

# ── 27. Azure OpenAI للمدير ────────────────────────────────────
nodes.append({
    "parameters": {
        "model": "gpt-4o-mini",
        "options": {
            "temperature": 0.3,
        }
    },
    "type": "@n8n/n8n-nodes-langchain.lmChatAzureOpenAi",
    "typeVersion": 1,
    "position": [860, 1520],
    "id": uid(),
    "name": "Azure OpenAI (Manager)",
    "credentials": {
        "azureOpenAiApi": {"id": "dHqEdXN0XQ09LqJi", "name": "Azure OpenAI"}
    }
})

connections["Azure OpenAI (Manager)"] = {
    "ai_languageModel": [[{"node": "Manager AI Agent", "type": "ai_languageModel", "index": 0}]]
}

# ── 28. إرسال رد للمدير ────────────────────────────────────────
nodes.append({
    "parameters": {
        "resource": "messages-api",
        "instanceName": "={{ $('Extract Manager Message').first().json.instance }}",
        "remoteJid": "={{ $('Extract Manager Message').first().json.manager_phone }}",
        "messageText": "={{ $json.output }}",
        "options_message": {}
    },
    "type": "n8n-nodes-evolution-api-english.evolutionApi",
    "typeVersion": 1,
    "position": [1200, 1300],
    "id": uid(),
    "name": "Send Reply to Manager",
    "credentials": {"evolutionApi": EVOLUTION_CREDS}
})

connections["Manager AI Agent"] = {
    "main": [[{"node": "Send Reply to Manager", "type": "main", "index": 0}]]
}

# ═══════════════════════════════════════════
# Sticky Notes للتوضيح
# ═══════════════════════════════════════════

STICKY_NOTES = [
    {
        "parameters": {"content": "# 📋 جروب واتساب - إتمام المهام والشكاوى\nيستقبل رسائل الجروب → يصنف النية → يتحقق من المهام → يسجل الشكاوى"},
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
        "position": [-100, 100], "id": uid(), "name": "Sticky Note 1"
    },
    {
        "parameters": {"content": "# ⏰ التذكيرات التلقائية\nكل دقيقة يتحقق من الأحداث القادمة → يبعت تذكير قبل 10 دقائق"},
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
        "position": [-100, 650], "id": uid(), "name": "Sticky Note 2"
    },
    {
        "parameters": {"content": "# 👔 محادثة المدير الخاصة\nالمدير يقدر يسأل عن الشكاوى والمهام ويحصل على ملخصات"},
        "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
        "position": [-100, 1150], "id": uid(), "name": "Sticky Note 3"
    },
]

nodes.extend(STICKY_NOTES)

# ═══════════════════════════════════════════
# تجميع الـ Workflow
# ═══════════════════════════════════════════

workflow = {
    "name": "AI Logistics Coordinator - موظف لوجستيات التشغيل",
    "nodes": nodes,
    "connections": connections,
    "active": False,
    "settings": {
        "executionOrder": "v1",
        "saveManualExecutions": True,
        "callerPolicy": "workflowsFromSameOwner",
    },
    "versionId": uid(),
    "meta": {
        "templateCredsSetupCompleted": True,
        "instanceId": "8df4082ac81111d2321c538ef34013493a96dd3b14b3af10e13ce9c3849e34d3"
    },
    "tags": [{"name": "logistics"}, {"name": "be-star"}],
}

# ── حفظ ──
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"[DONE] Saved: {OUTPUT}")
print(f"[DONE] Total nodes: {len(nodes)}")
print(f"[DONE] Total connections: {len(connections)}")
print(f"{'='*60}")
print("\nNodes:")
for n in nodes:
    if not n["name"].startswith("Sticky"):
        print(f"  > {n['name']} ({n['type']})")

print("\n[NOTE] This workflow is standalone and does not modify any existing workflow")
print("[NOTE] Credentials may need to be configured on the server")
