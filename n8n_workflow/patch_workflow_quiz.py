"""
patch_workflow_quiz.py
Modifies the ACTUAL production n8n workflow to inject quiz routing
into the main text message path.

BEFORE:
  Text4 → Memory + Model PreEnter2 → ... → AI Agent

AFTER:
  Text4 → Check Active Quiz (HTTP) → Quiz Active? (If)
    ├─ YES → Submit Quiz Answer (HTTP) → Is Correct? (If)
    │         ├─ ✅ → Send Correct Reply (Evolution API)
    │         └─ ❌ → Send Wrong Reply (Evolution API)
    └─ NO  → Memory + Model PreEnter2 → ... → AI Agent (unchanged)

Also removes the separate Quiz Answer Webhook path since it's now
handled inline in the main flow.
"""

import json
import sys
import os

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "be_star_ticketing_v6.json")

def load_workflow(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_workflow(wf, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved → {path}")

# ── Names of old standalone quiz nodes to REMOVE ──────────────────
OLD_QUIZ_NODES = {
    "Quiz Answer Webhook",
    "Extract Answer Data",
    "Check Active Question",
    "Has Active Question?",
    "Submit Quiz Answer",
    "Is Correct?",
    "Reply Correct",
    "Reply Wrong",
    "No Active Quiz (Pass Through)",
}

# ── New nodes to ADD ──────────────────────────────────────────────

BACKEND_URL = "http://38.242.139.159:3005"

def new_nodes():
    """Return the list of nodes to inject."""
    return [
        # 1. HTTP Request — check if there is an active quiz question
        {
            "parameters": {
                "url": f"{BACKEND_URL}/api/quiz/active-question",
                "options": {"timeout": 8000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-14192, 3720],
            "id": "quiz-check-001",
            "name": "Check Active Quiz",
            "continueOnFail": True
        },

        # 2. If — has_active == true?
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [
                        {
                            "id": "quiz-cond-active",
                            "leftValue": "={{ $json.has_active }}",
                            "rightValue": True,
                            "operator": {
                                "type": "boolean",
                                "operation": "equals"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-14000, 3720],
            "id": "quiz-if-active-001",
            "name": "Quiz Active?"
        },

        # 3. HTTP Request — submit quiz answer to backend
        {
            "parameters": {
                "method": "POST",
                "url": f"{BACKEND_URL}/api/quiz/answer",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Content-Type", "value": "application/json"}
                    ]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"phone\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n  \"answer_text\": \"{{ $('Text4').item.json.Text }}\",\n  \"sender_name\": \"{{ $('Whatsapp').item.json.body.data.pushName || 'Unknown' }}\"\n}",
                "options": {"timeout": 15000}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [-13760, 3620],
            "id": "quiz-submit-001",
            "name": "Submit Quiz Answer"
        },

        # 4. If — is_correct?
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [
                        {
                            "id": "quiz-cond-correct",
                            "leftValue": "={{ $json.is_correct }}",
                            "rightValue": True,
                            "operator": {
                                "type": "boolean",
                                "operation": "equals"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [-13520, 3620],
            "id": "quiz-if-correct-001",
            "name": "Is Answer Correct?"
        },

        # 5. Evolution API — send ✅ correct reply
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
            "position": [-13280, 3520],
            "id": "quiz-reply-correct-001",
            "name": "Quiz Reply Correct",
            "retryOnFail": True,
            "credentials": {
                "evolutionApi": {
                    "id": "IGwXyU5Jbou5S5V3",
                    "name": "Business Number"
                }
            }
        },

        # 6. Evolution API — send ❌ wrong reply
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
            "position": [-13280, 3720],
            "id": "quiz-reply-wrong-001",
            "name": "Quiz Reply Wrong",
            "retryOnFail": True,
            "credentials": {
                "evolutionApi": {
                    "id": "IGwXyU5Jbou5S5V3",
                    "name": "Business Number"
                }
            }
        },
    ]


def patch(wf):
    # ── 1. Remove old standalone quiz nodes ───────────────────────
    wf["nodes"] = [n for n in wf["nodes"] if n.get("name") not in OLD_QUIZ_NODES]
    for name in OLD_QUIZ_NODES:
        wf["connections"].pop(name, None)
    # Also clean any connection targets pointing to removed nodes
    for src, outs in list(wf["connections"].items()):
        for conn_type, branches in list(outs.items()):
            for branch in branches:
                branch[:] = [c for c in branch if c["node"] not in OLD_QUIZ_NODES]

    print("[OK] Removed old standalone quiz nodes")

    # ── 2. Add new inline quiz nodes ──────────────────────────────
    wf["nodes"].extend(new_nodes())
    print("[OK] Added 6 new quiz nodes inline")

    # ── 3. Rewire connections ─────────────────────────────────────

    # BEFORE: Text4 → Memory + Model PreEnter2
    # AFTER:  Text4 → Check Active Quiz → Quiz Active?
    #           ├─ YES → Submit Quiz Answer → Is Answer Correct?
    #           │         ├─ ✅ → Quiz Reply Correct
    #           │         └─ ❌ → Quiz Reply Wrong
    #           └─ NO  → Memory + Model PreEnter2

    conn = wf["connections"]

    # Text4 now goes to Check Active Quiz
    conn["Text4"] = {
        "main": [[
            {"node": "Check Active Quiz", "type": "main", "index": 0}
        ]]
    }

    # Check Active Quiz → Quiz Active?
    conn["Check Active Quiz"] = {
        "main": [[
            {"node": "Quiz Active?", "type": "main", "index": 0}
        ]]
    }

    # Quiz Active?:
    #   true  (output 0) → Submit Quiz Answer
    #   false (output 1) → Memory + Model PreEnter2  (original flow)
    conn["Quiz Active?"] = {
        "main": [
            [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],
            [{"node": "Memory + Model PreEnter2", "type": "main", "index": 0}],
        ]
    }

    # Submit Quiz Answer → Is Answer Correct?
    conn["Submit Quiz Answer"] = {
        "main": [[
            {"node": "Is Answer Correct?", "type": "main", "index": 0}
        ]]
    }

    # Is Answer Correct?:
    #   true  → Quiz Reply Correct
    #   false → Quiz Reply Wrong
    conn["Is Answer Correct?"] = {
        "main": [
            [{"node": "Quiz Reply Correct", "type": "main", "index": 0}],
            [{"node": "Quiz Reply Wrong",   "type": "main", "index": 0}],
        ]
    }

    print("[OK] Rewired connections:")
    print("     Text4 → Check Active Quiz → Quiz Active?")
    print("       ├─ YES → Submit Answer → Correct/Wrong reply")
    print("       └─ NO  → Memory + Model PreEnter2 (normal AI)")

    return wf


def main():
    src = INPUT_FILE
    if len(sys.argv) > 1:
        src = sys.argv[1]

    # Always write to the SAME file
    dst = src

    print(f"[..] Loading {src}")
    wf = load_workflow(src)
    print(f"[OK] {len(wf['nodes'])} nodes loaded")

    wf = patch(wf)

    save_workflow(wf, dst)
    print(f"\n[DONE] Workflow patched in-place: {dst}")
    print(f"[DONE] Total nodes now: {len(wf['nodes'])}")


if __name__ == "__main__":
    main()
