import json
import os

def create_n8n_workflow():
    # Common Credentials
    EVOLUTION_CREDS = {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}
    AZURE_OPENAI_CREDS = {"id": "L4HdmJ5bGz2Owawh", "name": "Azure Open AI account"}
    
    # -------------------------------------------------------------------------
    # Nodes
    # -------------------------------------------------------------------------
    nodes = []
    
    # 1. Webhook: WhatsApp Messages
    nodes.append({
        "parameters": {
            "httpMethod": "POST",
            "path": "bestar-whatsapp",
            "options": {}
        },
        "name": "WhatsApp Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [460, 300],
        "id": "webhook-whatsapp"
    })

    # 2. Webhook: Ticket Approval (Backend Trigger)
    nodes.append({
        "parameters": {
            "httpMethod": "POST",
            "path": "bestar-approval",
            "options": {}
        },
        "name": "Approval Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [460, 800],
        "id": "webhook-approval"
    })

    # -------------------------------------------------------------------------
    # Approval Flow
    # -------------------------------------------------------------------------

    # 3. Evolution API: Send PDF (Document)
    nodes.append({
        "parameters": {
            "resource": "messages-api",
            "operation": "send-media",
            "instanceName": "Mr. AI",
            "remoteJid": "={{ $json.phone }}@s.whatsapp.net",
            "mediaUrl": "={{ $json.pdf_url }}",
            "mediaType": "document",
            "fileName": "={{ $json.code }}.pdf",
            "caption": "🎫 تذكرتك جاهزة! نتمنى لك وقتاً ممتعاً في كن نجماً",
            "options_message": {}
        },
        "name": "Send PDF Ticket",
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [700, 800],
        "id": "send-pdf",
        "credentials": {"evolutionApi": EVOLUTION_CREDS}
    })

    # 4. Evolution API: Send Text Confirmation (Optional, implies in caption usually but safe to have)
    nodes.append({
        "parameters": {
            "resource": "messages-api",
            "instanceName": "Mr. AI",
            "remoteJid": "={{ $json.phone }}@s.whatsapp.net",
            "messageText": "✅ تم تأكيد حجزك بنجاح!\n\nاسم الحضور: {{ $json.name }}\nنوع التذكرة: {{ $json.ticket_type }}\nكود التذكرة: {{ $json.code }}\n\n📍 العنوان: {{ $json.location }}\n📅 الموعد: {{ $json.event_date }}",
            "options_message": {}
        },
        "name": "Send Confirmation Text",
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [950, 800],
        "id": "send-confirmation",
        "credentials": {"evolutionApi": EVOLUTION_CREDS}
    })

    # -------------------------------------------------------------------------
    # WhatsApp Incoming Flow
    # -------------------------------------------------------------------------

    # 5. Code Node: Extract Data
    nodes.append({
        "parameters": {
            "jsCode": """
const body = $input.first().json.body || $input.first().json;
let phone = '';
let messageType = 'text';
let messageContent = '';
let senderName = '';

if (body.data) {
  phone = body.data.key?.remoteJid?.replace('@s.whatsapp.net', '') || '';
  senderName = body.data.pushName || '';
  messageType = body.data.messageType || 'conversation';
  
  if (messageType === 'conversation' || messageType === 'extendedTextMessage') {
      messageContent = body.data.message?.conversation || body.data.message?.extendedTextMessage?.text || '';
  } else if (messageType === 'imageMessage') {
      messageContent = 'IMAGE'; 
  } else if (messageType === 'audioMessage') {
      messageContent = 'AUDIO';
  } else if (messageType === 'stickerMessage') {
      messageContent = 'STICKER';
  }
}

// Normalize Phone
phone = phone.replace(/[^0-9]/g, '');
if (phone.startsWith('20')) phone = phone.substring(2);
if (!phone.startsWith('0') && phone.length === 10) phone = '0' + phone;

return { phone, messageType, messageContent, senderName, fullBody: body };
            """
        },
        "name": "Extract Message Data",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [700, 300],
        "id": "extract-data"
    })

    # 6. Switch: Message Type
    # Note: We use a single "Text" output for both conversation types by routing them to the same index 0
    nodes.append({
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [
                                {"leftValue": "={{ $json.messageType }}", "rightValue": "conversation", "operator": {"type": "string", "operation": "equals"}},
                                {"leftValue": "={{ $json.messageType }}", "rightValue": "extendedTextMessage", "operator": {"type": "string", "operation": "equals"}}
                            ],
                            "combinator": "or"
                        },
                        "renameOutput": True,
                        "outputKey": "Text"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"leftValue": "={{ $json.messageType }}", "rightValue": "audioMessage", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Audio"
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                            "conditions": [{"leftValue": "={{ $json.messageType }}", "rightValue": "imageMessage", "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "Image"
                    }
                ]
            }
        },
        "name": "Switch Message Type",
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3,
        "position": [950, 300],
        "id": "switch-type"
    })

    # -------------------------------------------------------------------------
    # Audio Processing (Azure OpenAI)
    # -------------------------------------------------------------------------
    
    # 7. Evolution API: Get Audio Base64
    nodes.append({
        "parameters": {
            "resource": "chat-api",
            "operation": "get-media-base64",
            "instanceName": "Mr. AI",
            "messageId": "={{ $json.fullBody.data.key.id }}",
            "convertToMp4": False 
        },
        "name": "Get Audio Media",
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [1200, 450],
        "id": "get-audio",
        "credentials": {"evolutionApi": EVOLUTION_CREDS}
    })

    # 8. OpenAI: Whisper Transcription -> Switched to Azure OpenAI (using HTTP Request if specific node missing or standard node with azure creds)
    # n8n's standard OpenAI node supports Azure if configured in credentials.
    # However, user explicitly asked for "Azure". We will use the standard node but map it to Azure credentials.
    # Checks: standard openAi node has "resource" param. 
    
    # For Audio Transcription, standard OpenAI node in n8n can work with Azure if credentials are Azure OpenAI.
    # Let's check if we can use the "microsoftAzureOpenAi" node or similar. 
    # n8n has "n8n-nodes-base.microsoftAzureOpenAi".
    
    nodes.append({
        "parameters": {
            "resource": "audio",
            "operation": "transcribe",
            "binaryPropertyName": "data"
        },
        "name": "Azure Whisper",
        "type": "n8n-nodes-base.microsoftAzureOpenAi",
        "typeVersion": 1,
        "position": [1600, 450],
        "id": "whisper",
        "credentials": {"microsoftAzureOpenAi": AZURE_OPENAI_CREDS}
    })
    
    # Need to convert Base64 to Binary for Whisper
    nodes.append({
        "parameters": {
            "jsCode": """
const items = $input.all();
const binaryData = [];

for (const item of items) {
  const base64String = item.json.data.base64; 
  const buffer = Buffer.from(base64String, 'base64');
  
  binaryData.push({
    json: { ...item.json },
    binary: {
      data: {
        data: base64String,
        mimeType: 'audio/ogg', # Whatsapp audio usually ogg
        fileName: 'audio.ogg'
      }
    }
  });
}
return binaryData;
            """
        },
        "name": "Convert Base64 to Binary",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1400, 450],
        "id": "convert-binary"
    })


    # -------------------------------------------------------------------------
    # Image/Sticker Processing
    # -------------------------------------------------------------------------

    # 9. Evolution API: Get Image Base64
    nodes.append({
        "parameters": {
            "resource": "chat-api",
            "operation": "get-media-base64",
            "instanceName": "Mr. AI",
            "messageId": "={{ $json.fullBody.data.key.id }}"
        },
        "name": "Get Image Media",
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [1200, 600],
        "id": "get-image",
        "credentials": {"evolutionApi": EVOLUTION_CREDS}
    })

    # 10. Azure OpenAI: Vision Analysis
    # Azure OpenAI node might not support Vision directly in older versions, 
    # but let's try to use the chat resource with GPT-4V model deployment.
    nodes.append({
       "parameters": {
            "resource": "chat",
            "operation": "completion", # or similar
            # If standard node doesn't support image input easily, logic remains:
            # We often use HTTP Request for Vision to be safe.
            # But let's try to keep it consistent. If we use HTTP Request, we target Azure endpoint.
            "method": "POST",
            "url": "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-02-15-preview",
            # We will use HTTP Request for Azure Vision to ensure we can pass the image payload correctly
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "microsoftAzureOpenAi",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": """={
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Analyze this image. If it's a payment receipt, extract details. Respond in Arabic."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,{{ $json.data.base64 }}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
}""",
            "options": {}
        },
        "name": "Analyze Image (Azure GPT-4o)",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4,
        "position": [1400, 600],
        "id": "vision-analysis",
        "credentials": {"microsoftAzureOpenAi": AZURE_OPENAI_CREDS}
    })


    # -------------------------------------------------------------------------
    # Main Logic (AI Agent)
    # -------------------------------------------------------------------------
    
    # 11. Merge Inputs
    nodes.append({
        "parameters": {
            "jsCode": """
// Normalize input to a single "query" field
const input = $input.first().json;
let query = '';

if (input.text) query = input.text; // From Whisper
else if (input.choices) query = "Customer sent an image: " + input.choices[0].message.content; // From Vision
else if (input.messageContent) query = input.messageContent; // From Text Switch

return { query, phone: $('Extract Message Data').first().json.phone, senderName: $('Extract Message Data').first().json.senderName };
            """
        },
        "name": "Merge Inputs",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1800, 300],
        "id": "prepare-context"
    })

    # 12. AI Agent (Langchain)
    nodes.append({
        "parameters": {
            "promptType": "define",
            "text": "={{ $json.query }}",
            "options": {
                "systemMessage": """You are 'Be Star' Ticket Assistant. 
Event: Be Star - كن نجماً
Date: 11 Feb 2026
Location: Sohag - Canal of Suez Hall
Prices: VIP 500 EGP, Student 100 EGP.
Payment: Vodafone Cash 01557368364.

Your goals:
1. Answer questions about the event.
2. If user wants to book, ask for Name, Email, Ticket Type.
3. If user sends payment proof (image), thank them and say "Admin will review it".
4. If user sends Ticket Code (6 digits), tell them "This is an automated activation line, please use the 6-digit code to activate if needed or just show up."

Speak Egyptian Arabic. Be friendly.
"""
            }
        },
        "name": "Be Star Agent",
        "type": "@n8n/n8n-nodes-langchain.agent",
        "typeVersion": 1,
        "position": [2000, 300],
        "id": "ai-agent"
    })
    
    # 13. Azure OpenAI Chat Model (attached to Agent)
    nodes.append({
        "parameters": {
            "modelName": "gpt-4o", # Model deployment name in Azure
            "options": {}
        },
        "name": "Azure OpenAI Model",
        "type": "@n8n/n8n-nodes-langchain.lmChatAzureOpenAi",
        "typeVersion": 1,
        "position": [2000, 500],
        "id": "openai-model",
        "credentials": {"microsoftAzureOpenAi": AZURE_OPENAI_CREDS}
    })

    
    # 14. Memory (Postgres) (attached to Agent)
    nodes.append({
        "parameters": {
            "sessionIdType": "customKey",
            "sessionKey": "={{ $('Extract Message Data').first().json.phone }}",
            "tableName": "bestar_chat_history"
        },
        "name": "Postgres Memory",
        "type": "@n8n/n8n-nodes-langchain.memoryPostgresChat",
        "typeVersion": 1,
        "position": [2000, 650],
        "id": "postgres-memory",
        "credentials": {"postgres": {"id": "nZpi0ecZbdqHX8nL", "name": "Postgres account"}}
    })

    # 15. Evolution API: Send Reply
    nodes.append({
        "parameters": {
            "resource": "messages-api",
            "instanceName": "Mr. AI",
            "remoteJid": "={{ $('Extract Message Data').first().json.phone }}@s.whatsapp.net",
            "messageText": "={{ $json.output }}",
            "options_message": {}
        },
        "name": "Send Reply",
        "type": "n8n-nodes-evolution-api-english.evolutionApi",
        "typeVersion": 1,
        "position": [2300, 300],
        "id": "send-reply",
        "credentials": {"evolutionApi": EVOLUTION_CREDS}
    })

    # -------------------------------------------------------------------------
    # Connections (Edges)
    # -------------------------------------------------------------------------
    connections = {
        "WhatsApp Webhook": {"main": [[{"node": "Extract Message Data", "type": "main", "index": 0}]]},
        "Extract Message Data": {"main": [[{"node": "Switch Message Type", "type": "main", "index": 0}]]},
        "Switch Message Type": {
            "main": [
                [{"node": "prepare-context", "type": "main", "index": 0}], # Text
                [{"node": "prepare-context", "type": "main", "index": 0}], # Text (Extended)
                [{"node": "Get Audio Media", "type": "main", "index": 0}], # Audio
                [{"node": "Get Image Media", "type": "main", "index": 0}]  # Image
            ]
        },
        "Get Audio Media": {"main": [[{"node": "Convert Base64 to Binary", "type": "main", "index": 0}]]},
        "Convert Base64 to Binary": {"main": [[{"node": "Whisper Transcribe", "type": "main", "index": 0}]]},
        "Whisper Transcribe": {"main": [[{"node": "prepare-context", "type": "main", "index": 0}]]},
        "Get Image Media": {"main": [[{"node": "Analyze Image (GPT-4o)", "type": "main", "index": 0}]]},
        "Analyze Image (GPT-4o)": {"main": [[{"node": "prepare-context", "type": "main", "index": 0}]]},
        "prepare-context": {"main": [[{"node": "Be Star Agent", "type": "main", "index": 0}]]},
        "Be Star Agent": {"main": [[{"node": "Send Reply", "type": "main", "index": 0}]]},
        "OpenAI Model": {"ai_languageModel": [[{"node": "Be Star Agent", "type": "ai_languageModel", "index": 0}]]},
        "Postgres Memory": {"ai_memory": [[{"node": "Be Star Agent", "type": "ai_memory", "index": 0}]]},
        
        # Approval Flow
        "Approval Webhook": {"main": [[{"node": "Send PDF Ticket", "type": "main", "index": 0}]]},
        "Send PDF Ticket": {"main": [[{"node": "Send Confirmation Text", "type": "main", "index": 0}]]}
    }

    workflow = {
        "nodes": nodes,
        "connections": connections,
        "meta": {"name": "Be Star Ticketing Agent V2"}
    }
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), '../../n8n_workflow/be_star_ticketing_v2.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    print(f"Workflow generated at: {output_path}")

if __name__ == "__main__":
    create_n8n_workflow()
