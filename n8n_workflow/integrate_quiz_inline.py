"""
integrate_quiz_inline.py

Modifies be_star_ticketing_v6.json to add INLINE quiz checking.

Flow change:
  Before: Text4 → Memory + Model PreEnter2 → ... → AI Agent
  After:  Text4 → Check Active Quiz → Quiz Active?
                   ├─ YES → Submit Answer → Is Correct? → Reply ✅ / Reply ❌
                   └─ NO  → Memory + Model PreEnter2 → ... → AI Agent (unchanged)

Also removes standalone quiz webhook nodes (redundant).
"""

import json
import os

BACKEND_URL = "http://38.242.139.159:3005"

def transform(input_file, output_file=None):
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_quiz_inline{ext}"

    with open(input_file, 'r', encoding='utf-8') as f:
        wf = json.load(f)

    # ─── 1. REMOVE standalone quiz webhook nodes ───
    remove_names = {
        "Quiz Answer Webhook", "Extract Answer Data", "Check Active Question",
        "Has Active Question?", "Submit Quiz Answer", "Is Correct?",
        "Reply Correct", "Reply Wrong", "No Active Quiz (Pass Through)",
    }

    wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in remove_names]

    # Remove their connections
    for name in list(wf["connections"].keys()):
        if name in remove_names:
            del wf["connections"][name]

    # ─── 2. ADD inline quiz nodes ───
    # Positions: Text4 is at (-14352, 3840), Memory+Model at (-14080, 4048)
    # Place quiz nodes between them, using the vertical space above

    new_nodes = [
        # ── Check Active Quiz (HTTP GET) ──
        {
            "parameters": {
                "url": f"{BACKEND_URL}/api/quiz/active-question",
                "options": {"timeout": 10000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-14192, 3840],
            "id": "quiz-inline-check-001",
            "name": "Check Active Quiz",
            "continueOnFail": True
        },

        # ── Quiz Active? (If node) ──
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [{
                        "id": "quiz-active-cond-001",
                        "leftValue": "={{ $json.has_active }}",
                        "rightValue": True,
                        "operator": {"type": "boolean", "operation": "equals"}
                    }],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-14032, 3840],
            "id": "quiz-inline-if-001",
            "name": "Quiz Active?"
        },

        # ── Submit Quiz Answer (HTTP POST) ──
        {
            "parameters": {
                "method": "POST",
                "url": f"{BACKEND_URL}/api/quiz/answer",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [{"name": "Content-Type", "value": "application/json"}]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n"
                    "  \"phone\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n"
                    "  \"answer_text\": \"{{ $('Text4').item.json.Text }}\",\n"
                    "  \"sender_name\": \"{{ $('Whatsapp').first().json.body.data.pushName || 'Unknown' }}\"\n"
                    "}",
                "options": {"timeout": 15000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-13872, 3700],
            "id": "quiz-inline-submit-001",
            "name": "Submit Quiz Answer"
        },

        # ── Is Answer Correct? (If node) ──
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [{
                        "id": "quiz-correct-cond-001",
                        "leftValue": "={{ $json.is_correct }}",
                        "rightValue": True,
                        "operator": {"type": "boolean", "operation": "equals"}
                    }],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-13712, 3700],
            "id": "quiz-inline-correct-if-001",
            "name": "Is Answer Correct?"
        },

        # ── Quiz Reply ✅ (Evolution API - Correct) ──
        {
            "parameters": {
                "resource": "messages-api",
                "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
                "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
                "messageText": "={{ '✅ إجابة صحيحة! أحسنت 🎉\\n\\n🏆 النقاط: ' + $('Submit Quiz Answer').item.json.points_earned + '\\n📊 نسبة التشابه: ' + ($('Submit Quiz Answer').item.json.similarity || 100) + '%' }}",
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
            "position": [-13552, 3600],
            "id": "quiz-inline-reply-correct-001",
            "name": "Quiz Reply ✅",
            "retryOnFail": True,
            "credentials": {
                "evolutionApi": {
                    "id": "IGwXyU5Jbou5S5V3",
                    "name": "Business Number"
                }
            }
        },

        # ── Quiz Reply ❌ (Evolution API - Wrong) ──
        {
            "parameters": {
                "resource": "messages-api",
                "instanceName": "={{ $('Whatsapp').first().json.body.instance }}",
                "remoteJid": "={{ $('Whatsapp').first().json.body.data.key.remoteJid }}",
                "messageText": "={{ '❌ إجابة خاطئة\\n\\n' + ($('Submit Quiz Answer').item.json.message || 'حاول في السؤال القادم! 💪') }}",
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
            "position": [-13552, 3800],
            "id": "quiz-inline-reply-wrong-001",
            "name": "Quiz Reply ❌",
            "retryOnFail": True,
            "credentials": {
                "evolutionApi": {
                    "id": "IGwXyU5Jbou5S5V3",
                    "name": "Business Number"
                }
            }
        },

        # ── Sticky Note for Quiz Section ──
        {
            "parameters": {
                "content": "# 🎯 Quiz Mode Check\nIf active quiz → submit answer & reply.\nIf no quiz → continue to AI Agent.",
                "height": 320,
                "width": 880,
                "color": 3
            },
            "type": "n8n-nodes-base.stickyNote",
            "position": [-14240, 3560],
            "typeVersion": 1,
            "id": "quiz-inline-sticky-001",
            "name": "Quiz Section Note"
        }
    ]

    wf["nodes"].extend(new_nodes)

    # ─── 3. REWIRE CONNECTIONS ───
    connections = wf["connections"]

    # Text4 was → Memory + Model PreEnter2
    # Now: Text4 → Check Active Quiz
    connections["Text4"] = {
        "main": [[{"node": "Check Active Quiz", "type": "main", "index": 0}]]
    }

    # Check Active Quiz → Quiz Active?
    connections["Check Active Quiz"] = {
        "main": [[{"node": "Quiz Active?", "type": "main", "index": 0}]]
    }

    # Quiz Active?
    #   true (index 0) → Submit Quiz Answer
    #   false (index 1) → Memory + Model PreEnter2 (original flow)
    connections["Quiz Active?"] = {
        "main": [
            [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],
            [{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}]
        ]
    }

    # Submit Quiz Answer → Is Answer Correct?
    connections["Submit Quiz Answer"] = {
        "main": [[{"node": "Is Answer Correct?", "type": "main", "index": 0}]]
    }

    # Is Answer Correct?
    #   true → Quiz Reply ✅
    #   false → Quiz Reply ❌
    connections["Is Answer Correct?"] = {
        "main": [
            [{"node": "Quiz Reply ✅", "type": "main", "index": 0}],
            [{"node": "Quiz Reply ❌", "type": "main", "index": 0}]
        ]
    }

    wf["connections"] = connections

    # ─── 4. SAVE ───
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"✅ Quiz inline integration complete!")
    print(f"📄 Output: {output_file}")
    print(f"")
    print(f"🔄 Flow changed:")
    print(f"   Text4 → Check Active Quiz → Quiz Active?")
    print(f"     ├─ YES → Submit Answer → Correct? → Reply ✅/❌")
    print(f"     └─ NO  → Memory + Model PreEnter2 → AI Agent (unchanged)")
    print(f"")
    print(f"🗑️  Removed standalone quiz webhook nodes")
    print(f"🆕 Added 6 inline quiz nodes + sticky note")

    return output_file


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "be_star_ticketing_v6.json")
    transform(input_file)
