"""
inject_quiz_nodes.py
Adds Quiz Answer Check nodes into be_star_ticketing_v6.json

This script modifies the existing v6 workflow to:
1. Add a "Check Quiz" HTTP Request node (calls /api/quiz/active-question)
2. Add a "Quiz Router" If node to check if quiz is active
3. Add a "Submit Quiz Answer" HTTP Request node
4. Add a "Quiz Reply" HTTP Request node to send result to user
5. Rewire: Set metadata2 -> Quiz Router -> (true) Submit Quiz Answer -> Quiz Reply
                                          -> (false) Be Star Ticketing Agent (original flow)
"""

import json
import sys
import os
import copy

def inject_quiz_nodes(input_file, output_file=None):
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_with_quiz{ext}"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # ====== NEW NODES ======
    
    check_quiz_node = {
        "parameters": {
            "url": "={{ $env.BACKEND_URL || 'http://backend:8000' }}/api/quiz/active-question",
            "options": {
                "timeout": 10000
            }
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-3000, 2500],
        "id": "quiz-check-inline-001",
        "name": "Check Active Quiz",
        "continueOnFail": True
    }
    
    quiz_router_node = {
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
                        "id": "quiz-route-cond-001",
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
        "position": [-2800, 2500],
        "id": "quiz-router-inline-001",
        "name": "Quiz Active?"
    }
    
    submit_answer_node = {
        "parameters": {
            "method": "POST",
            "url": "={{ $env.BACKEND_URL || 'http://backend:8000' }}/api/quiz/answer",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    }
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"phone\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n  \"answer_text\": \"{{ $('Set metadata2').item.json.Text || $('Set metadata2').item.json.chatInput || '' }}\",\n  \"sender_name\": \"{{ $('Set metadata2').item.json.pushName || 'Unknown' }}\"\n}",
            "options": {
                "timeout": 15000
            }
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-2600, 2400],
        "id": "quiz-submit-inline-001",
        "name": "Submit Quiz Answer"
    }
    
    quiz_reply_node = {
        "parameters": {
            "method": "POST",
            "url": "={{ $env.EVOLUTION_API_URL }}/message/sendText/{{ $env.EVOLUTION_INSTANCE_NAME }}",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {
                        "name": "apikey",
                        "value": "={{ $env.EVOLUTION_API_KEY }}"
                    },
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    }
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={\n  \"number\": \"{{ $('User Phone ID').item.json.User_phone_ID }}\",\n  \"text\": \"{{ $json.is_correct ? '\\u2705 \\u0625\\u062c\\u0627\\u0628\\u0629 \\u0635\\u062d\\u064a\\u062d\\u0629! \\u0623\\u062d\\u0633\\u0646\\u062a \\ud83c\\udf89\\\\n\\\\n\\ud83c\\udfc6 \\u0627\\u0644\\u0646\\u0642\\u0627\\u0637: ' + $json.points_earned + '\\\\n\\ud83d\\udcca \\u0646\\u0633\\u0628\\u0629 \\u0627\\u0644\\u062a\\u0634\\u0627\\u0628\\u0647: ' + ($json.similarity || 100) + '%' : '\\u274c \\u0625\\u062c\\u0627\\u0628\\u0629 \\u062e\\u0627\\u0637\\u0626\\u0629\\\\n\\\\n' + ($json.message || '\\u062d\\u0627\\u0648\\u0644 \\u0641\\u064a \\u0627\\u0644\\u0633\\u0624\\u0627\\u0644 \\u0627\\u0644\\u0642\\u0627\\u062f\\u0645!') }}\"\n}",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [-2400, 2400],
        "id": "quiz-reply-inline-001",
        "name": "Quiz Reply"
    }
    
    # ====== ADD NODES ======
    workflow["nodes"].extend([
        check_quiz_node,
        quiz_router_node,
        submit_answer_node,
        quiz_reply_node,
    ])
    
    connections = workflow.get("connections", {})
    
    # ====== REWIRE CONNECTIONS ======
    # Original: Set metadata2 -> Be Star Ticketing Agent
    # New: Set metadata2 -> Check Active Quiz -> Quiz Active? 
    #        -> (true) Submit Quiz Answer -> Quiz Reply
    #        -> (false) Be Star Ticketing Agent
    
    # 1. Redirect Set metadata2 to Check Active Quiz (instead of Be Star Ticketing Agent)
    if "Set metadata2" in connections:
        connections["Set metadata2"]["main"] = [
            [{"node": "Check Active Quiz", "type": "main", "index": 0}]
        ]
    
    # 2. Check Active Quiz -> Quiz Active?
    connections["Check Active Quiz"] = {
        "main": [
            [{"node": "Quiz Active?", "type": "main", "index": 0}]
        ]
    }
    
    # 3. Quiz Active? -> true: Submit Quiz Answer, false: Be Star Ticketing Agent
    connections["Quiz Active?"] = {
        "main": [
            [{"node": "Submit Quiz Answer", "type": "main", "index": 0}],  # true
            [{"node": "Be Star Ticketing Agent", "type": "main", "index": 0}]  # false
        ]
    }
    
    # 4. Submit Quiz Answer -> Quiz Reply
    connections["Submit Quiz Answer"] = {
        "main": [
            [{"node": "Quiz Reply", "type": "main", "index": 0}]
        ]
    }
    
    workflow["connections"] = connections
    
    # ====== SAVE ======
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Quiz nodes injected successfully!")
    print(f"[OK] Output: {output_file}")
    print(f"[OK] Nodes added: Check Active Quiz, Quiz Active?, Submit Quiz Answer, Quiz Reply")
    print(f"[OK] Flow: Set metadata2 -> Check Quiz -> Router -> (quiz) Answer + Reply")
    print(f"[OK]                                              -> (normal) AI Agent")
    return output_file

if __name__ == "__main__":
    input_file = os.path.join(os.path.dirname(__file__), "be_star_ticketing_v6.json")
    inject_quiz_nodes(input_file)
