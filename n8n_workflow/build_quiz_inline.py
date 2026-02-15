"""
build_quiz_inline.py

Takes the existing workflow and:
1. Removes ALL old quiz nodes (both inline and standalone)
2. Adds proper inline quiz routing in the text message path
3. Saves as be_star_ticketing_v6_quiz.json (ready to import in n8n)

Flow:
  Text4 → Check Active Quiz → Quiz Active?
           ├─ YES → Submit Quiz Answer → Is Correct? → Reply ✅/❌
           └─ NO  → Memory + Model PreEnter2 → ... → AI Agent
"""

import json, os

BACKEND_URL = "http://38.242.139.159:3005"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    src = os.path.join(SCRIPT_DIR, "be_star_ticketing_v6_with_quiz.json")
    out = os.path.join(SCRIPT_DIR, "be_star_ticketing_v6_quiz.json")

    with open(src, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    # ── 1. Remove ALL old quiz-related nodes ──
    old_quiz = {
        "Quiz Answer Webhook", "Extract Answer Data", "Check Active Question",
        "Has Active Question?", "No Active Quiz (Pass Through)",
        "Check Active Quiz", "Quiz Active?", "Submit Quiz Answer",
        "Is Correct?", "Is Answer Correct?", "Reply Correct", "Reply Wrong",
        "Quiz Reply", "Quiz Reply ✅", "Quiz Reply ❌", "Quiz Section Note",
    }
    wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in old_quiz]
    for name in list(wf["connections"].keys()):
        if name in old_quiz:
            del wf["connections"][name]

    # Restore Text4 → Memory + Model PreEnter2 (in case it was rewired)
    wf["connections"]["Text4"] = {
        "main": [[{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}]]
    }
    # Restore Set metadata2 → Be Star Ticketing Agent
    if "Set metadata2" in wf["connections"]:
        wf["connections"]["Set metadata2"] = {
            "main": [[{"node": "Be Star Ticketing Agent", "type": "main", "index": 0}]]
        }

    # ── 2. Add new inline quiz nodes ──
    new_nodes = [
        {
            "parameters": {
                "url": f"{BACKEND_URL}/api/quiz/active-question",
                "options": {"timeout": 10000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-14192, 3840],
            "id": "qi-check-001",
            "name": "Check Active Quiz",
            "continueOnFail": True
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"id": "qi-cond-001", "leftValue": "={{ $json.has_active }}", "rightValue": True,
                                    "operator": {"type": "boolean", "operation": "equals"}}],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-14032, 3840],
            "id": "qi-if-001",
            "name": "Quiz Active?"
        },
        {
            "parameters": {
                "method": "POST",
                "url": f"{BACKEND_URL}/api/quiz/answer",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Content-Type", "value": "application/json"}]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"phone\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n  \"answer_text\": \"{{ $('Text4').item.json.Text }}\",\n  \"sender_name\": \"{{ $('Whatsapp').first().json.body.data.pushName || 'Unknown' }}\"\n}",
                "options": {"timeout": 15000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-13872, 3700],
            "id": "qi-submit-001",
            "name": "Submit Quiz Answer"
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"id": "qi-correct-001", "leftValue": "={{ $json.is_correct }}", "rightValue": True,
                                    "operator": {"type": "boolean", "operation": "equals"}}],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-13712, 3700],
            "id": "qi-correct-if-001",
            "name": "Is Answer Correct?"
        },
        {
            "parameters": {
                "resource": "messages-api",
                "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
                "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
                "messageText": "={{ '✅ إجابة صحيحة! أحسنت 🎉\\n\\n🏆 النقاط: ' + $('Submit Quiz Answer').item.json.points_earned + '\\n📊 نسبة التشابه: ' + ($('Submit Quiz Answer').item.json.similarity || 100) + '%' }}",
                "options_message": {"quoted": {"messageQuoted": {"messageId": "={{ $('Whatsapp').first().json.body.data.key.id }}"}}}
            },
            "type": "n8n-nodes-evolution-api-english.evolutionApi",
            "typeVersion": 1,
            "position": [-13552, 3600],
            "id": "qi-reply-ok-001",
            "name": "Quiz Reply ✅",
            "retryOnFail": True,
            "credentials": {"evolutionApi": {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}}
        },
        {
            "parameters": {
                "resource": "messages-api",
                "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
                "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
                "messageText": "={{ '❌ إجابة خاطئة\\n\\n' + ($('Submit Quiz Answer').item.json.message || 'حاول في السؤال القادم! 💪') }}",
                "options_message": {"quoted": {"messageQuoted": {"messageId": "={{ $('Whatsapp').first().json.body.data.key.id }}"}}}
            },
            "type": "n8n-nodes-evolution-api-english.evolutionApi",
            "typeVersion": 1,
            "position": [-13552, 3800],
            "id": "qi-reply-no-001",
            "name": "Quiz Reply ❌",
            "retryOnFail": True,
            "credentials": {"evolutionApi": {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}}
        },
        {
            "parameters": {
                "content": "# 🎯 Quiz Mode\nText4 → Check Quiz → Active?\n✅ YES → Submit + Reply\n❌ NO → AI Agent",
                "height": 300, "width": 750, "color": 3
            },
            "type": "n8n-nodes-base.stickyNote",
            "position": [-14240, 3560],
            "typeVersion": 1,
            "id": "qi-sticky-001",
            "name": "Sticky Note Quiz"
        }
    ]
    wf["nodes"].extend(new_nodes)

    # ── 3. Rewire connections ──
    c = wf["connections"]

    # Text4 → Check Active Quiz (was → Memory + Model PreEnter2)
    c["Text4"] = {"main": [[{"node": "Check Active Quiz", "type": "main", "index": 0}]]}

    c["Check Active Quiz"] = {"main": [[{"node": "Quiz Active?", "type": "main", "index": 0}]]}

    # Quiz Active? → true: Submit Answer, false: Memory + Model PreEnter2
    c["Quiz Active?"] = {"main": [
        [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],
        [{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}]
    ]}

    c["Submit Quiz Answer"] = {"main": [[{"node": "Is Answer Correct?", "type": "main", "index": 0}]]}

    c["Is Answer Correct?"] = {"main": [
        [{"node": "Quiz Reply ✅", "type": "main", "index": 0}],
        [{"node": "Quiz Reply ❌", "type": "main", "index": 0}]
    ]}

    with open(out, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"[OK] Done! Output: {out}")
    print(f"Flow: Text4 -> Check Quiz -> Active?")
    print(f"  YES -> Submit Answer -> Correct? -> Reply OK/Wrong")
    print(f"  NO  -> Memory+Model -> AI Agent (unchanged)")
    return out

if __name__ == "__main__":
    build()
