"""
Generate Be Star Ticketing Workflow v3
Based on mentor's workflow template with minimal modifications.
"""
import json
import os

# === CREDENTIALS ===
EVO_CREDS = {"id": "IGwXyU5Jbou5S5V3", "name": "Business Number"}
AZURE_CREDS = {"id": "L4HdmJ5bGz2Owawh", "name": "Azure Open AI account"}
POSTGRES_CREDS = {"id": "nZpi0ecZbdqHX8nL", "name": "Postgres account"}
PINECONE_CREDS = {"id": "swltCt6gosR03VPd", "name": "GH_Sales"}
BEARER_CREDS = {"id": "J4gutsAvdiO7kN8M", "name": "Bearer Auth account"}
GSHEETS_CREDS = {"id": "uQ46ohym4MGqAgfH", "name": "Abdelrahman"}

# === API Keys ===
AZURE_API_KEY = "5zSQL871XpyGNXgzSx0LPwzkCrPqYj52L5ODHMA0bs6stZlhi35xJQQJ99BKACfhMk5XJ3w3AAABACOGk5RF"
ACCESS_API_KEY = "Pi7HbQnp7lml2Ok30bBYq06dDbzD3oxxNEAdOQqeT38"
CLIENT_ID = "Be-Star"
MEMORY_TABLE = "bestar_chat_history"

nodes = []

# ============================================================
# SECTION 1: TRIGGERS + ACCESS CONTROL
# ============================================================

# WhatsApp Webhook (modified path for Be Star)
nodes.append({"parameters":{"httpMethod":"POST","path":"bestar-whatsapp","options":{}},"type":"n8n-nodes-base.webhook","typeVersion":2.1,"position":[5936,5504],"id":"ab6a4ceb-3288-4e0d-8946-a93ffdd797ee","name":"Whatsapp","webhookId":"d8fa5154-f391-43c2-ad0c-f5c7b3eb2737"})

# Approval Webhook (NEW for Be Star)
nodes.append({"parameters":{"httpMethod":"POST","path":"bestar-approval","options":{}},"type":"n8n-nodes-base.webhook","typeVersion":2.1,"position":[5936,6600],"id":"3945bd27-149a-4e85-8949-aca70e6b78ad","name":"Approval Webhook","webhookId":"9e913b19-87ad-44f4-9dc4-4bdb4ae0f556"})

# User Phone ID
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"803c1504-5ff1-4d19-8d9b-7c933466e48d","name":"User_phone_ID","value":"={{\n(() => {\n  const data = $json.body?.data?.key;\n  let rawNumber = '';\n  if (data?.remoteJidAlt?.includes('@s.whatsapp.net')) {\n    rawNumber = data.remoteJidAlt.split('@')[0];\n  } else if (data?.remote3lidAlt?.includes('@s.whatsapp.net')) {\n    rawNumber = data.remote3lidAlt.split('@')[0];\n  } else if (data?.remoteJid?.includes('@s.whatsapp.net')) {\n    rawNumber = data.remoteJid.split('@')[0];\n  } else {\n    rawNumber = (data?.remoteJid || '').split('@')[0];\n  }\n  rawNumber = rawNumber.trim();\n  if (rawNumber.startsWith('20')) {\n    return '0' + rawNumber.slice(2);\n  }\n  return '+' + rawNumber;\n})()\n}}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[6160,5504],"id":"c4405af0-30f2-4787-99c2-3a580c5dfc0a","name":"User Phone ID"})

# Access Control
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/check-access","sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},"sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({\"api_key\": \""+ACCESS_API_KEY+"\", \"user_id\": $('User Phone ID').item.json.User_phone_ID, \"platform_type\": \"Whatsapp\", \"user_name\": $('Whatsapp').item.json.body.data.pushName}) }}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[6384,5504],"id":"61bb6090-63d9-4c16-9ab2-7219347c94e9","name":"Access Control4"})

# If8 (access check)
nodes.append({"parameters":{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},"conditions":[{"id":"857ccdd3-662c-44c6-aff6-9660ffa633fe","leftValue":"={{ $json.access }}","rightValue":True,"operator":{"type":"boolean","operation":"equals"}}],"combinator":"and"},"options":{}},"type":"n8n-nodes-base.if","typeVersion":2.2,"position":[6672,5504],"id":"1693036d-7840-4f11-bf4e-5415fb177ef6","name":"If8"})

# Switch3 (MODIFIED: added extendedTextMessage as OR with conversation)
nodes.append({"parameters":{"rules":{"values":[{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},"conditions":[{"leftValue":"={{ $('Whatsapp').first().json.body.data.messageType }}","rightValue":"conversation","operator":{"type":"string","operation":"equals"},"id":"35588a02-6475-400d-b869-da05d7ed0f3a"},{"leftValue":"={{ $('Whatsapp').first().json.body.data.messageType }}","rightValue":"extendedTextMessage","operator":{"type":"string","operation":"equals"},"id":"ext-text-msg-001"}],"combinator":"or"},"renameOutput":True,"outputKey":"Text"},{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},"conditions":[{"id":"83b9e800-99d0-4e31-8032-ae81aebe86d1","leftValue":"={{ $('Whatsapp').first().json.body.data.messageType }}","rightValue":"audioMessage","operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"Audio"},{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},"conditions":[{"id":"b70e2cfc-8de2-4f4c-a6c0-77c2028ba78f","leftValue":"={{ $('Whatsapp').first().json.body.data.messageType }}","rightValue":"imageMessage","operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"Photos"},{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},"conditions":[{"id":"8c9c8324-851d-4d68-ab24-34d545eb07da","leftValue":"={{ $('Whatsapp').item.json.body.data.messageType }}","rightValue":"stickerMessage","operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":"Stickers"}]},"options":{}},"type":"n8n-nodes-base.switch","typeVersion":3.2,"position":[7200,5488],"id":"c94c0911-6ae7-4e59-9bf8-80c4fd0b83bb","name":"Switch3","alwaysOutputData":False,"executeOnce":False})

# ============================================================
# SECTION 2: INPUT PROCESSING
# ============================================================

# Text4 (MODIFIED: WhatsApp only, added extendedTextMessage support)
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"2f35809b-3889-4ef7-a8d5-a4d934842631","name":"Text","value":"={{ $('Whatsapp').first().json.body?.data?.message?.conversation ?? $('Whatsapp').first().json.body?.data?.message?.extendedTextMessage?.text ?? '' }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[7888,4992],"id":"2f0f4adf-6101-4620-8ed9-a7aa6830e391","name":"Text4"})

# --- Audio Pipeline (WhatsApp) ---
# Get media in base1
nodes.append({"parameters":{"resource":"chat-api","operation":"get-media-base64","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","messageId":"={{ $('Whatsapp').first().json.body.data.key.id }}"},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[7456,5504],"id":"0ccb1e75-be62-4000-a099-8357f202eb8b","name":"Get media in base1","retryOnFail":True,"alwaysOutputData":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Convert to File
nodes.append({"parameters":{"operation":"toBinary","sourceProperty":"data.base64","options":{}},"type":"n8n-nodes-base.convertToFile","typeVersion":1.1,"position":[7600,5504],"id":"0de261a8-acfa-4f5a-9355-7df38831cce6","name":"Convert to File","executeOnce":False,"alwaysOutputData":False,"retryOnFail":True})

# Convert Audio Type3
nodes.append({"parameters":{"method":"POST","url":"http://38.242.139.159:5555/convert","sendBody":True,"contentType":"binaryData","inputDataFieldName":"data","options":{"response":{"response":{"responseFormat":"file"}}}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[7776,5504],"id":"318e8b70-ed9f-4b49-a284-1a18fbb2c749","name":"Convert Audio Type3"})

# Transcribe a recording1
nodes.append({"parameters":{"method":"POST","url":"https://mrai-openai.openai.azure.com/openai/deployments/gpt-4o-transcribe/audio/transcriptions?api-version=2025-03-01-preview","sendHeaders":True,"headerParameters":{"parameters":[{"name":"api-key","value":AZURE_API_KEY}]},"sendBody":True,"contentType":"multipart-form-data","bodyParameters":{"parameters":[{"parameterType":"formBinaryData","name":"file","inputDataFieldName":"data"},{"name":"model","value":"gpt-4o-transcribe"},{"name":"prompt","value":"\"Transcribe accurately. Speaker uses Arabic with English words mixed in. Keep English terms in English.\""}]},"options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[7952,5504],"id":"643b1719-0253-44c3-8df1-4264f42fe7e8","name":"Transcribe a recording1"})

# Cost Calculator (audio transcription cost)
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/log-usage","sendBody":True,"bodyParameters":{"parameters":[{"name":"api_key","value":ACCESS_API_KEY},{"name":"execution_id","value":"={{ $execution.id }}"},{"name":"request_type","value":"transcription"},{"name":"model","value":"gpt-4o-transcribe"},{"name":"input_tokens","value":"={{ $json.usage?.prompt_tokens ?? 0 }}"},{"name":"output_tokens","value":"={{ $json.usage?.completion_tokens ?? 0 }}"},{"name":"platform_user_id","value":"={{ $('User Phone ID').item.json.User_phone_ID }}"}]},"options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[8144,5504],"id":"4e59102e-3aaa-4f42-9849-363043d38f67","name":"Cost Calculator"})

# Voice (MODIFIED: simplified, removed Facebook reference)
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"2f35809b-3889-4ef7-a8d5-a4d934842631","name":"Voice","value":"={{ $('Transcribe a recording1').item.json.text }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[8304,5232],"id":"e6d01f7b-a751-4960-9b33-6ef686b7edfd","name":"Voice"})

# --- Image Pipeline ---
# Get Image Base64
nodes.append({"parameters":{"resource":"chat-api","operation":"get-media-base64","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","messageId":"={{ $('Whatsapp').first().json.body.data.key.id }}"},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[7488,5872],"id":"bfa001d0-abca-437b-bb22-19bd32161552","name":"Get Image Base64","retryOnFail":True,"alwaysOutputData":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Analyze Image (Mistral)2
nodes.append({"parameters":{"method":"POST","url":"https://mrai-openai.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview","sendHeaders":True,"headerParameters":{"parameters":[{"name":"api-key","value":AZURE_API_KEY},{"name":"Content-Type","value":"application/json"},{"name":"x-ms-model-mesh-model-name","value":"mistral-medium-2505"}]},"sendBody":True,"specifyBody":"json","jsonBody":"={\"model\":\"mistral-medium-2505\",\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"وصف الصورة دي بالعربي بشكل مختصر. لو فيها نص أو كلام، اكتبه. لو فيها منتج أو خدمة أو شعار، وصفه.\"},{\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/jpeg;base64,{{ $json.data.base64 }}\"}}]}],\"max_tokens\":500}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[7984,5872],"id":"dc54c8b9-7e40-498a-8e87-1a4fc2ded6bd","name":"Analyze Image (Mistral)2"})

# Cost Calculator4 (image analysis cost)
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/log-usage","sendBody":True,"bodyParameters":{"parameters":[{"name":"api_key","value":ACCESS_API_KEY},{"name":"execution_id","value":"=n8n-exec-{{$executionId}}"},{"name":"request_type","value":"chat"},{"name":"model","value":"mistral-medium-2505"},{"name":"input_tokens","value":"={{ $json.usage.prompt_tokens }}"},{"name":"output_tokens","value":"={{ $json.usage.completion_tokens }}"},{"name":"platform_user_id","value":"={{ $('User Phone ID').item.json.User_phone_ID }}"}]},"options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[8128,5872],"id":"14ee61b8-3845-4d04-b1c1-13faf89264cc","name":"Cost Calculator4"})

# image (set)
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"2f35809b-3889-4ef7-a8d5-a4d934842631","name":"image","value":"={{ $json.choices[0].message.content }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[8272,5872],"id":"1f1383c6-a02b-45a8-b36e-e22c3f63f9b5","name":"image"})

# --- Stickers Pipeline ---
# Get Stickers Base
nodes.append({"parameters":{"resource":"chat-api","operation":"get-media-base64","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","messageId":"={{ $('Whatsapp').first().json.body.data.key.id }}"},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[7488,6240],"id":"bb5a4262-70ad-4792-b8f7-8a26b5fddd86","name":"Get Stickers Base","retryOnFail":True,"alwaysOutputData":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Analyze Strickers (Mistral)3
nodes.append({"parameters":{"method":"POST","url":"https://mrai-openai.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview","sendHeaders":True,"headerParameters":{"parameters":[{"name":"api-key","value":AZURE_API_KEY},{"name":"Content-Type","value":"application/json"},{"name":"x-ms-model-mesh-model-name","value":"mistral-medium-2505"}]},"sendBody":True,"specifyBody":"json","jsonBody":"={\"model\":\"mistral-medium-2505\",\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"وصف الصورة دي بالعربي بشكل مختصر. لو فيها نص أو كلام، اكتبه. لو فيها منتج أو خدمة أو شعار، وصفه.\"},{\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/jpeg;base64,{{ $json.data.base64 }}\"}}]}],\"max_tokens\":500}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[7984,6240],"id":"a10ffb1a-6bcc-4d0b-a8d9-31fb4f47730f","name":"Analyze Strickers (Mistral)3"})

# Stickers (set)
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"2f35809b-3889-4ef7-a8d5-a4d934842631","name":"Stickers","value":"={{ $json.choices[0].message.content }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[8272,6240],"id":"eed6d3d3-4579-40d4-847d-e9f56a7ea11e","name":"Stickers"})

# Memory + Model PreEnter2 (MODIFIED: WhatsApp only)
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"a63db671-77e6-4370-b11f-92fc2767ee58","name":"Memory Key","value":"={{ $('User Phone ID').item.json.User_phone_ID }}","type":"string"},{"id":"a12d20c8-7931-470c-a7df-70473f0be258","name":"Input","value":"={{ $if($('Text4').isExecuted, $('Text4').first().json.Text, \n   $if($('Voice').isExecuted, $('Voice').first().json.Voice, \n   $if($('image').isExecuted, 'العميل بعت صورة. وصف الصورة: ' + $('image').first().json.image, \n   'العميل بعت sticker: ' + $('Stickers').first().json.Stickers))) }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[8528,5024],"id":"3f811a31-e70d-4582-8de2-a8949e4e49de","name":"Memory + Model PreEnter2"})

# ============================================================
# SECTION 3: RAG PIPELINE (kept as-is, only client_id changed)
# ============================================================

# Set metadata3
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"ca1744cf-69e7-4a85-81d3-2fb2b936e496","name":"workflow_id","value":"={{ $workflow.id }}","type":"string"},{"id":"205c7c4d-2dfa-471f-9306-33d30e16722a","name":"execution_id","value":"={{ $execution.id }}","type":"string"},{"id":"3fa4932f-c3cc-41a8-90a4-d1b3a2d32cdd","name":"client_id","value":CLIENT_ID,"type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[8720,5024],"id":"4c014f39-d1d5-47d5-ab88-712a4867f509","name":"Set metadata3"})

# Reformer Agent
REFORMER_PROMPT = "You are a deterministic router+query-reformer for Mr. AI RAG.\nInputs:\n- current_message (string)\n- previous_messages (array of {role,content})\n- last_namespace (string|null)\n- detected_language (\"ar\"|\"en\")\n\nTask A — classify:\nChoose EXACTLY one label: Who_Are_We_And_Related_Information | Terms_And_Conditions_Data_Privacy_Policy | Practical_Case_Studies_and_why_us.\nRules: if vague/ack (\"تمام\",\"more?\") → continue last_namespace; if multi-intent → pick the primary intent; if confidence <0.5 → Who_Are_We_And_Related_Information; greetings fall under Who_Are_We_And_Related_Information.\n\nTask B — reform:\nRewrite a concise semantic search query for the chosen label using context.\nKeep 5–20 tokens; preserve proper names, numbers, currency; add ≤2 helpful synonyms/domain terms; remove filler/pronouns; keep constraints (expert/service, date/time, locale, language).\nIf too vague, add a short HyDE (≤25 tokens) describing what a relevant doc would say.\n\nStrict output (one line, minified JSON only):\n{\"category\":\"<label>\",\"query\":\"<short query>\",\"alternates\":[\"...\"],\"negative_terms\":[\"...\"],\"hyde\":\"...\",\"language\":\"ar|en\"}\n\nHard limits: total output ≤ ~80 tokens; no text outside JSON; no line breaks; no explanations; temperature low for stable routing.\n"
nodes.append({"parameters":{"promptType":"define","text":"={{ $('Memory + Model PreEnter2').item.json.Input }}","options":{"systemMessage":REFORMER_PROMPT}},"type":"@n8n/n8n-nodes-langchain.agent","typeVersion":3,"position":[8864,5024],"id":"47e9e27f-8298-4b07-90d9-d02b4c946c74","name":"Reformer"})

# Simple Memory (for Reformer)
nodes.append({"parameters":{"sessionIdType":"customKey","sessionKey":"={{ $('Memory + Model PreEnter2').item.json['Memory Key'] }}"},"type":"@n8n/n8n-nodes-langchain.memoryBufferWindow","typeVersion":1.3,"position":[9024,5232],"id":"f43f3ab3-c3c4-452b-8215-cd88a4009ae5","name":"Simple Memory"})

# Azure OpenAI Chat Model5 (LLM for Reformer - code node with cost tracking)
LLM_CODE_TEMPLATE = """const {{ AzureChatOpenAI }} = require("@langchain/openai");
const azureOpenAIApiKey = "{api_key}";
const azureOpenAIApiInstanceName = "mrai-openai";
const azureOpenAIApiDeploymentName = "gpt-4.1-mini";
const azureOpenAIApiVersion = "{api_version}";
const input_token_cost = 0.40;
const output_token_cost = 1.60;
const tools = await this.getInputConnectionData('ai_tool', 0);
const googleSheetTool = tools[0];
const {{ workflow_id, execution_id, client_id }} = $('{metadata_node}').first().json;
const llm = new AzureChatOpenAI({{
  azureOpenAIApiKey, azureOpenAIApiInstanceName, azureOpenAIApiDeploymentName, azureOpenAIApiVersion,
  temperature: {temperature},
  callbacks: [{{ handleLLMEnd: async function(output, runId, parentId) {{
    const generation = output.generations[0][0];
    const message = generation.message;
    const input_tokens = message.usage_metadata.input_tokens;
    const output_tokens = message.usage_metadata.output_tokens;
    const total_tokens = message.usage_metadata.total_tokens;
    const input_cost_val = (input_tokens / 1_000_000) * input_token_cost;
    const output_cost_val = (output_tokens / 1_000_000) * output_token_cost;
    const total_cost = input_cost_val + output_cost_val;
    const total_cost_in_egypt = total_cost * 50;
    const row = {{ date: (new Date()).toGMTString(), workflow_id, execution_id, client_id, model: azureOpenAIApiDeploymentName, input_tokens, output_tokens, total_tokens, input_cost: input_cost_val, output_cost: output_cost_val, total_cost, total_cost_in_egypt }};
    if (googleSheetTool && googleSheetTool.func) {{ await googleSheetTool.func(row); }}
  }} }}]
}});
return llm;"""

llm5_code = LLM_CODE_TEMPLATE.format(api_key=AZURE_API_KEY, api_version="2024-08-01-preview", metadata_node="Set metadata3", temperature=0.7)
nodes.append({"parameters":{"code":{"supplyData":{"code":llm5_code}},"inputs":{"input":[{"type":"ai_tool","required":True}]},"outputs":{"output":[{"type":"ai_languageModel"}]}},"id":"fdd7f2c4-bf9f-40e6-ba7b-520bbdc26402","name":"Azure OpenAI Chat Model5","type":"@n8n/n8n-nodes-langchain.code","position":[8784,5184],"typeVersion":1})

# Log Reformer Rekaz (cost tracking tool for Reformer LLM)
LOG_TOOL_PARAMS = {"method":"POST","url":"https://access.mrailabs.com/api/log-usage","sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},"sendBody":True,"bodyParameters":{"parameters":[{"name":"api_key","value":ACCESS_API_KEY},{"name":"execution_id","value":"={{ $execution.id }}"},{"name":"workflow_id","value":"={{ $workflow.id }}"},{"name":"platform_user_id","value":"={{ $('Memory + Model PreEnter2').item.json['Memory Key'] }}"},{"name":"request_type","value":"reform"},{"name":"model","value":"={{ $json.model || 'gpt-4o-mini' }}"},{"name":"input_tokens","value":"={{ $fromAI('input_tokens', ``, 'string') }}"},{"name":"output_tokens","value":"={{ $fromAI('output_tokens', ``, 'string') }}"},{"name":"input_cost","value":"={{ $fromAI('input_cost', ``, 'string') }}"},{"name":"output_cost","value":"={{ $fromAI('output_cost', ``, 'string') }}"}]},"options":{}}
nodes.append({"parameters":LOG_TOOL_PARAMS,"type":"n8n-nodes-base.httpRequestTool","typeVersion":4.3,"position":[8848,5328],"id":"62895ecc-eb6e-4ba7-8280-67953be52693","name":"Log Reformer Rekaz"})

# Set metadata4
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"ca1744cf-69e7-4a85-81d3-2fb2b936e496","name":"workflow_id","value":"={{ $workflow.id }}","type":"string"},{"id":"205c7c4d-2dfa-471f-9306-33d30e16722a","name":"execution_id","value":"={{ $execution.id }}","type":"string"},{"id":"3fa4932f-c3cc-41a8-90a4-d1b3a2d32cdd","name":"client_id","value":CLIENT_ID,"type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[9136,5008],"id":"be2c6eed-d6b8-47b5-805f-7823b157116a","name":"Set metadata4"})

# Information Extractor
nodes.append({"parameters":{"text":"={{ $('Reformer').item.json.output }}","attributes":{"attributes":[{"name":"category","description":"تصنيف السؤال من هذه القائمة فقط: Who_Are_We_And_Related_Information أو Practical_Case_Studies_and_why_us أو Terms_And_Conditions_Data_Privacy_Policy","required":True},{"name":"reformer_data","description":"كل البيانات الأخرى (query, alternates, negative_terms, hyde, language)","required":True}]},"options":{}},"type":"@n8n/n8n-nodes-langchain.informationExtractor","typeVersion":1.2,"position":[9280,5008],"id":"b2c1d404-f9cb-4dca-8d53-0b7e8c18dea6","name":"Information Extractor"})

# Azure OpenAI Chat Model7 (LLM for Information Extractor)
llm7_code = LLM_CODE_TEMPLATE.format(api_key=AZURE_API_KEY, api_version="2024-08-01-preview", metadata_node="Set metadata4", temperature=0.7)
nodes.append({"parameters":{"code":{"supplyData":{"code":llm7_code}},"inputs":{"input":[{"type":"ai_tool","required":True}]},"outputs":{"output":[{"type":"ai_languageModel"}]}},"id":"77c626f0-3baa-4364-9f48-cff5c8e67b2d","name":"Azure OpenAI Chat Model7","type":"@n8n/n8n-nodes-langchain.code","position":[9248,5184],"typeVersion":1})

# Log Reformer Rekaz4
LOG_TOOL_PARAMS4 = dict(LOG_TOOL_PARAMS)
nodes.append({"parameters":LOG_TOOL_PARAMS4,"type":"n8n-nodes-base.httpRequestTool","typeVersion":4.3,"position":[9312,5328],"id":"4b47c6d7-d993-4d59-90cd-311ba69d1980","name":"Log Reformer Rekaz4"})

# Edit Fields1
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"dd42c43a-f949-46c7-bc0c-79dc4472b3d3","name":"Pinecone_Namespace","value":"={{ $json.output.category }}","type":"string"},{"id":"24500874-b716-4abc-9376-cb8ccb0ca25b","name":"Reformer","value":"={{ $json.output }}","type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[9584,5024],"id":"1aba9fc2-d101-4930-a5dd-14862171b052","name":"Edit Fields1"})

# Pinecone Vector Store1
nodes.append({"parameters":{"mode":"load","pineconeIndex":{"__rl":True,"value":"mr-ai-website-chatbot-knowledge-base","mode":"list","cachedResultName":"mr-ai-website-chatbot-knowledge-base"},"prompt":"={{ $json.Reformer }}","topK":12,"options":{"pineconeNamespace":"={{ $json.Pinecone_Namespace }}"}},"type":"@n8n/n8n-nodes-langchain.vectorStorePinecone","typeVersion":1.3,"position":[9712,5024],"id":"3520038b-f00c-42ac-9894-aeb3e709459d","name":"Pinecone Vector Store1","credentials":{"pineconeApi":PINECONE_CREDS}})

# Embeddings Azure OpenAI
nodes.append({"parameters":{"model":"text-embedding-3-large","options":{"dimensions":3072}},"type":"@n8n/n8n-nodes-langchain.embeddingsAzureOpenAi","typeVersion":1,"position":[9712,5184],"id":"57431b9d-2a54-4ce7-a543-1c94448f3464","name":"Embeddings Azure OpenAI","credentials":{"azureOpenAiApi":AZURE_CREDS}})

# Aggregate1
nodes.append({"parameters":{"fieldsToAggregate":{"fieldToAggregate":[{"fieldToAggregate":"document.pageContent"}]},"options":{}},"type":"n8n-nodes-base.aggregate","typeVersion":1,"position":[9984,5024],"id":"1063ed24-a9ca-4e43-9d38-111900de27df","name":"Aggregate1"})

# Text3
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"2f35809b-3889-4ef7-a8d5-a4d934842631","name":"Text from user","value":"={{ $('Memory + Model PreEnter2').first().json.Input }}","type":"string"},{"id":"8a4a05e2-9c61-48cc-a767-ddf3d426f69d","name":"Text  from database","value":"={{ $json.pageContent }}","type":"array"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[10112,5024],"id":"20a92d90-7226-4df6-a141-b823e82acb9f","name":"Text3"})

# Set metadata2
nodes.append({"parameters":{"assignments":{"assignments":[{"id":"ca1744cf-69e7-4a85-81d3-2fb2b936e496","name":"workflow_id","value":"={{ $workflow.id }}","type":"string"},{"id":"205c7c4d-2dfa-471f-9306-33d30e16722a","name":"execution_id","value":"={{ $execution.id }}","type":"string"},{"id":"3fa4932f-c3cc-41a8-90a4-d1b3a2d32cdd","name":"client_id","value":CLIENT_ID,"type":"string"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[10256,5024],"id":"d40dfdc4-5264-4a0b-ba95-c26375cf77ae","name":"Set metadata2"})


# ============================================================
# SECTION 4: AI AGENTS (System prompts modified for Be Star)
# ============================================================

# Be Star Ticketing Agent (renamed from Sales Assistant Orchestrator Agent1)
BESTAR_SYSTEM_PROMPT = """أنت "عمر" مساعد ذكي لحجز تذاكر فعالية "كن نجماً - Be Star" 🌟
📋 معلومات الفعالية:
🎉 الاسم: كن نجماً - Be Star
📅 الموعد: 11 فبراير 2026
📍 المكان: سوهاج - الكوامل - قاعة قناة السويس
💰 الأسعار:
- VIP: 500 جنيه
- طلبة: 100 جنيه
💳 الدفع: فودافون كاش على الرقم 01557368364
الوقت الحالي: {{ $now.format('dd/LLL/yyyy h:mm A') }}
═══════════════════════════════════════════
📋 استراتيجية المحادثة
المرحلة 1: الترحيب (على قد السؤال!)
لما العميل يبعت تحية:
- "وعليكم السلام ورحمة الله 😊 أهلاً بيك! معاك عمر من فعالية كن نجماً. أقدر أساعدك بإيه؟"
❌ ماتعرضش تفاصيل قبل ما يسأل
---
المرحلة 2: الرد على الأسئلة
- ردّ على سؤال العميل بالظبط (2-3 جمل)
- لو عايز يحجز → وجّهه لخطوات الحجز
---
المرحلة 3: جمع بيانات الحجز (سؤال واحد/رسالة)
⚠️ لو العميل قال معلومة قبل كده، ماتسألش عليها تاني.
1. الاسم بالكامل؟
2. الإيميل؟
3. نوع التذكرة (VIP أو طلبة)؟
4. عدد التذاكر؟
---
المرحلة 4: الدفع
"تمام يا فندم! 💰 المبلغ المطلوب [المبلغ] جنيه
---
ادفع على فودافون كاش: 01557368364
---
وابعتلي صورة إيصال الدفع عشان نأكد الحجز ✅"
---
المرحلة 5: استلام إثبات الدفع
لو العميل بعت صورة:
"شكراً يا فندم! 📸 استلمنا إيصال الدفع. الأدمن هيراجعه وهيبعتلك التذكرة قريب إن شاء الله ✅"
═══════════════════════════════════════════
📦 بيانات من قاعدة البيانات:
{{ $('Text3').item.json['Text  from database'] }}
═══════════════════════════════════════════
📝 تعليمات إضافية:
{{ $if($('Access Control4').isExecuted, $('Access Control4').item.json.knowledge_base.additional_instructions, '') }}
═══════════════════════════════════════════
🎁 عروض حالياً:
{{ $if($('Access Control4').isExecuted, $('Access Control4').item.json.knowledge_base.current_offers, '') }}
═══════════════════════════════════════════
✅ قواعد:
- سؤال واحد في كل رسالة
- استخدم "---" لتقسيم الرسائل الطويلة
- اتكلم بالعامية المصرية الودودة
- استخدم الإيموجي باعتدال
- ماتستخدمش markdown أو HTML
- ماتكررش سؤال على معلومة اتقالت
- لو سأل خارج الموضوع: "بعتذر يا فندم 🙏 أنا تخصصي فقط في فعالية كن نجماً"
═══════════════════════════════════════════
التنسيق:
✅ نص عادي | إيموجي | أسطر جديدة | ---
❌ markdown | \\n | <br> | HTML tags
═══════════════════════════════════════════"""

nodes.append({"parameters":{"promptType":"define","text":"={{ $('Text3').item.json['Text from user'] }}","options":{"systemMessage":"=" + BESTAR_SYSTEM_PROMPT,"returnIntermediateSteps":False}},"type":"@n8n/n8n-nodes-langchain.agent","typeVersion":3,"position":[10624,4864],"id":"ba2c31bd-7da8-4c21-a901-7ab21dad8bc6","name":"Be Star Ticketing Agent"})

# Azure OpenAI Chat Model4 (LLM for Agent)
llm4_code = LLM_CODE_TEMPLATE.format(api_key=AZURE_API_KEY, api_version="2024-12-01-preview", metadata_node="Set metadata3", temperature=1)
nodes.append({"parameters":{"code":{"supplyData":{"code":llm4_code}},"inputs":{"input":[{"type":"ai_tool","required":True}]},"outputs":{"output":[{"type":"ai_languageModel"}]}},"id":"6fc195f2-0015-4f73-9a14-6ec16095fd64","name":"Azure OpenAI Chat Model4","type":"@n8n/n8n-nodes-langchain.code","position":[10416,5104],"typeVersion":1})

# Postgres Chat Memory1 (for Agent)
nodes.append({"parameters":{"sessionIdType":"customKey","sessionKey":"={{ $('Memory + Model PreEnter2').first().json['Memory Key'] }}","tableName":MEMORY_TABLE,"contextWindowLength":50},"type":"@n8n/n8n-nodes-langchain.memoryPostgresChat","typeVersion":1.3,"position":[10688,5232],"id":"dce43c58-58bc-4029-a49d-cf75d12c77f4","name":"Postgres Chat Memory1","credentials":{"postgres":POSTGRES_CREDS}})

# Log Reformer Rekaz3 (cost tracking tool for Agent LLM)
LOG_TOOL_PARAMS3 = dict(LOG_TOOL_PARAMS)
LOG_TOOL_PARAMS3["bodyParameters"]["parameters"][4] = {"name":"request_type","value":"respond"}
nodes.append({"parameters":LOG_TOOL_PARAMS3,"type":"n8n-nodes-base.httpRequestTool","typeVersion":4.3,"position":[10576,5232],"id":"77b114f8-8326-4ff1-993b-fd03e10da250","name":"Log Reformer Rekaz3"})

# Guardrails Supervisor (MODIFIED: Be Star instead of Mr. AI)
GUARDRAILS_PROMPT = """You are a "Compliance Filter" for كن نجماً (Be Star). 🛡️
Your specific role is to PASS the "Draft Answer" to the user EXACTLY AS IT IS, unless a "Fatal Error" is detected.

# 🚫 FATAL ERRORS (ONLY THESE REQUIRE INTERVENTION):
1. **Out of Scope**: Discussing politics, religion, cooking, medical advice, or coding unrelated to كن نجماً event.
2. **Hallucination**: Promising a specific price or feature NOT present in the provided context.
3. **Harmful/Rude**: Profanity or insults.

# 🚦 DECISION LOGIC (STRICT):
- **IF NO FATAL ERROR IS FOUND:**
  You MUST return the "Draft Answer" **WORD-FOR-WORD**.
  - ❌ Do NOT summarize.
  - ❌ Do NOT improve the style or tone.
  - ❌ Do NOT change the dialect.
  - ✅ **COPY & PASTE** the Draft Answer exactly.

- **IF A FATAL ERROR IS FOUND:**
  Only THEN, rewrite the answer to be a polite, formal refusal or correction (in Egyptian Arabic).
  (Example: "عذراً يا فندم، أنا تخصصي فقط في فعالية كن نجماً.")"""

nodes.append({"parameters":{"promptType":"define","text":"=Original Query: {{ $('Memory + Model PreEnter2').item.json.Input }}\n\nDraft Answer: {{ $json.output }}","options":{"systemMessage":"=" + GUARDRAILS_PROMPT}},"type":"@n8n/n8n-nodes-langchain.agent","typeVersion":1.6,"position":[11696,4880],"id":"5c6a7ebb-c03a-4549-ab07-7fa49cb63b9e","name":"Guardrails Supervisor"})

# Azure OpenAI Chat Model1 (LLM for Guardrails)
nodes.append({"parameters":{"model":"gpt-4.1-mini","options":{}},"type":"@n8n/n8n-nodes-langchain.lmChatAzureOpenAi","typeVersion":1,"position":[11424,5264],"id":"85498b7b-e653-4892-b997-d3f61e40b035","name":"Azure OpenAI Chat Model1","credentials":{"azureOpenAiApi":AZURE_CREDS}})

# Postgres Chat Memory (for Guardrails)
nodes.append({"parameters":{"sessionIdType":"customKey","sessionKey":"={{ $('Memory + Model PreEnter2').first().json['Memory Key'] }}","tableName":MEMORY_TABLE,"contextWindowLength":50},"type":"@n8n/n8n-nodes-langchain.memoryPostgresChat","typeVersion":1.3,"position":[11824,5296],"id":"33584155-f433-4d4f-88e6-fef9d111b5bd","name":"Postgres Chat Memory","credentials":{"postgres":POSTGRES_CREDS}})

# ============================================================
# SECTION 5: OUTPUT FLOW (WhatsApp only, Switch Answer removed)
# ============================================================

# Log Usr Messages
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/log-message","sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},"sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({\"api_key\": \""+ACCESS_API_KEY+"\", \"platform_user_id\": $('Memory + Model PreEnter2').item.json['Memory Key'], \"execution_id\": $execution.id, \"role\": \"user\", \"content\": $('Memory + Model PreEnter2').item.json['Input']}) }}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[12736,4976],"id":"432c5ea9-2f67-44b5-a6c3-8d0d8d16e747","name":"Log Usr Messages"})

# Send presence1
nodes.append({"parameters":{"resource":"chat-api","operation":"send-presence","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","remoteJid":"={{ $('Whatsapp').first().json.body.data.key.remoteJid }}","delay":3000},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[13536,5216],"id":"98dc2f51-9118-43dc-ab1c-85b4464e48d5","name":"Send presence1","retryOnFail":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Splite the messages
SPLIT_CODE = """const DELIMITER = '---';
const rawOutput = $('Guardrails Supervisor').first().json.output || '';
if (!rawOutput || rawOutput.trim().length === 0) { return [{ json: { text: '' } }]; }
const hasDelimiter = rawOutput.includes(DELIMITER);
let messages = [];
if (hasDelimiter) { messages = rawOutput.split(DELIMITER).map(msg => msg.trim()).filter(msg => msg.length > 0); }
else { messages = [rawOutput.trim()]; }
messages = messages.map(msg => msg.replace(/---/g, '').trim());
messages = messages.filter(msg => msg.length > 0);
if (messages.length === 0) { const cleanedOriginal = rawOutput.replace(/---/g, '').trim(); return [{ json: { text: cleanedOriginal || 'عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.' } }]; }
return messages.map(text => ({ json: { text } }));"""
nodes.append({"parameters":{"jsCode":SPLIT_CODE},"type":"n8n-nodes-base.code","typeVersion":2,"position":[13632,5440],"id":"a1d9b95c-6e94-4cd7-9111-2b2b4473aa6d","name":"Splite the messages"})

# Send text (first message with quote)
nodes.append({"parameters":{"resource":"messages-api","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","remoteJid":"={{ $('Whatsapp').first().json.body.data.key.remoteJid }}","messageText":"={{ $('Splite the messages').first().json.text }}","options_message":{"quoted":{"messageQuoted":{"messageId":"={{ $('Whatsapp').first().json.body.data.key.id }}"}}}},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[13808,5392],"id":"198e6f25-e508-4bf0-b96a-350de8fa45b5","name":"Send text","retryOnFail":True,"executeOnce":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Log AI Messages1
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/log-message","sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},"sendBody":True,"specifyBody":"=json","bodyParameters":{"parameters":[{}]},"jsonBody":"={{ JSON.stringify({\"api_key\": \""+ACCESS_API_KEY+"\", \"platform_user_id\": $('Memory + Model PreEnter2').first().json['Memory Key'], \"execution_id\": $execution.id, \"role\": \"assistant\", \"content\": $('Splite the messages').first().json.text}) }}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[13952,5392],"id":"461da543-db3b-4e69-b7ee-370d52acfeee","name":"Log AI Messages1"})

# Skip First One (code)
nodes.append({"parameters":{"jsCode":"const allItems = $('Splite the messages').all();\nif (allItems.length <= 1) { return []; }\nreturn allItems.slice(1);"},"type":"n8n-nodes-base.code","typeVersion":2,"position":[13808,5552],"id":"69fe3c09-ac5b-40ff-bb95-54efc0265803","name":"Skip First One"})

# Loop Over Items
nodes.append({"parameters":{"options":{}},"type":"n8n-nodes-base.splitInBatches","typeVersion":3,"position":[13968,5552],"id":"25a504b2-d07f-49aa-b437-f4a06e1f839b","name":"Loop Over Items"})

# No Operation, do nothing
nodes.append({"parameters":{},"type":"n8n-nodes-base.noOp","typeVersion":1,"position":[14176,5408],"id":"12c04e42-2767-4b85-981d-6c6bc88d9c93","name":"No Operation, do nothing"})

# Send text1 (remaining messages)
nodes.append({"parameters":{"resource":"messages-api","instanceName":"={{ $('Whatsapp').first().json.body.instance }}","remoteJid":"={{ $('Whatsapp').first().json.body.data.key.remoteJid }}","messageText":"={{ $('Loop Over Items').item.json.text }}","options_message":{}},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[14144,5568],"id":"147c0a6a-631f-4abd-be80-6482901e4fd4","name":"Send text1","retryOnFail":True,"credentials":{"evolutionApi":EVO_CREDS}})

# Log AI Messages
nodes.append({"parameters":{"method":"POST","url":"https://access.mrailabs.com/api/log-message","sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},"sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({\"api_key\": \""+ACCESS_API_KEY+"\", \"platform_user_id\": $('Memory + Model PreEnter2').item.json['Memory Key'], \"execution_id\": $execution.id, \"role\": \"assistant\", \"content\": $('Loop Over Items').item.json.text}) }}","options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.3,"position":[14336,5568],"id":"b122c0c9-bd9f-4681-b0aa-ff3e6eb1fdee","name":"Log AI Messages"})

# ============================================================
# SECTION 6: APPROVAL FLOW (NEW for Be Star)
# ============================================================

# Send PDF Ticket
nodes.append({"parameters":{"resource":"messages-api","operation":"send-media","instanceName":"Mr. AI","remoteJid":"={{ $json.phone }}@s.whatsapp.net","mediaUrl":"={{ $json.pdf_url }}","mediaType":"document","fileName":"={{ $json.code }}.pdf","caption":"🎫 تذكرتك جاهزة! نتمنى لك وقتاً ممتعاً في كن نجماً","options_message":{}},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[6176,6600],"id":"33a8d0fa-3674-4d80-b5a7-f573c5c3d4f1","name":"Send PDF Ticket","credentials":{"evolutionApi":EVO_CREDS}})

# Send Confirmation Text
nodes.append({"parameters":{"resource":"messages-api","instanceName":"Mr. AI","remoteJid":"={{ $json.phone }}@s.whatsapp.net","messageText":"✅ تم تأكيد حجزك بنجاح!\n\nاسم الحضور: {{ $json.name }}\nنوع التذكرة: {{ $json.ticket_type }}\nكود التذكرة: {{ $json.code }}\n\n📍 العنوان: سوهاج - الكوامل - قاعة قناة السويس\n📅 الموعد: 11 فبراير 2026","options_message":{}},"type":"n8n-nodes-evolution-api-english.evolutionApi","typeVersion":1,"position":[6416,6600],"id":"46d07dee-2391-4c33-827d-f6d57e0a8547","name":"Send Confirmation Text","credentials":{"evolutionApi":EVO_CREDS}})

# ============================================================
# SECTION 7: STICKY NOTES (kept relevant ones)
# ============================================================
for sn in [
    {"content":"# Inputs\n","height":912,"width":1376,"pos":[7088,4816],"id":"a948ff74","color":None},
    {"content":"# Voice\n","height":256,"width":976,"pos":[7408,5408],"id":"c17763e8","color":3},
    {"content":"## Text or Voice\n","height":208,"width":208,"pos":[7152,5440],"id":"6e7f5b10","color":7},
    {"content":"# Text\n","height":176,"width":656,"pos":[7648,4944],"id":"20fa2687","color":3},
    {"content":"# Anaysis image","height":304,"width":1264,"pos":[7168,5792],"id":"da72f62f","color":None},
    {"content":"# Anaysis stickers\n","height":240,"width":1264,"pos":[7168,6176],"id":"73960d5d","color":None},
    {"content":"# Orchestrator Agent\n","height":752,"width":768,"pos":[10384,4768],"id":"12a57df2","color":5},
    {"content":"# Rag \n","height":720,"width":1920,"pos":[8480,4768],"id":"55bc4455","color":None},
    {"content":"## Mr Ai Guard ","height":752,"width":1024,"pos":[11360,4800],"id":"58b87122","color":7},
    {"content":"# Output\n","height":784,"width":1536,"pos":[12608,4704],"id":"50162fcd","color":None},
    {"content":"## Whatsapp","height":192,"width":560,"pos":[13456,5184],"id":"c5873594","color":7},
    {"content":"## Splite the messeges","height":384,"width":924,"pos":[13568,5376],"id":"db56bba9","color":3},
    {"content":"## Approval Flow","height":240,"width":560,"pos":[5856,6528],"id":"bestar-approval-sn","color":7},
]:
    n = {"parameters":{"content":sn["content"],"height":sn["height"],"width":sn["width"]},"type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":sn["pos"],"id":sn["id"]+"-0000-0000-0000-000000000000" if len(sn["id"])<36 else sn["id"],"name":"Sticky Note"}
    if sn["color"] is not None: n["parameters"]["color"] = sn["color"]
    nodes.append(n)

# ============================================================
# CONNECTIONS
# ============================================================
C = lambda node, typ="main", idx=0: {"node":node,"type":typ,"index":idx}

connections = {
    # Trigger + Access
    "Whatsapp":{"main":[[C("User Phone ID")]]},
    "User Phone ID":{"main":[[C("Access Control4")]]},
    "Access Control4":{"main":[[C("If8")]]},
    "If8":{"main":[[C("Switch3")]]},
    # Switch → Input Processing
    "Switch3":{"main":[[C("Text4")],[C("Get media in base1")],[C("Get Image Base64")],[C("Get Stickers Base")]]},
    "Text4":{"main":[[C("Memory + Model PreEnter2")]]},
    # Audio Pipeline
    "Get media in base1":{"main":[[C("Convert to File")]]},
    "Convert to File":{"main":[[C("Convert Audio Type3")]]},
    "Convert Audio Type3":{"main":[[C("Transcribe a recording1")]]},
    "Transcribe a recording1":{"main":[[C("Cost Calculator")]]},
    "Cost Calculator":{"main":[[C("Voice")]]},
    "Voice":{"main":[[C("Memory + Model PreEnter2")]]},
    # Image Pipeline
    "Get Image Base64":{"main":[[C("Analyze Image (Mistral)2")]]},
    "Analyze Image (Mistral)2":{"main":[[C("image")]]},
    "image":{"main":[[C("Memory + Model PreEnter2")]]},
    # Stickers Pipeline
    "Get Stickers Base":{"main":[[C("Analyze Strickers (Mistral)3")]]},
    "Analyze Strickers (Mistral)3":{"main":[[C("Stickers")]]},
    "Stickers":{"main":[[C("Memory + Model PreEnter2")]]},
    # RAG Pipeline
    "Memory + Model PreEnter2":{"main":[[C("Set metadata3")]]},
    "Set metadata3":{"main":[[C("Reformer")]]},
    "Reformer":{"main":[[C("Set metadata4")]]},
    "Set metadata4":{"main":[[C("Information Extractor")]]},
    "Information Extractor":{"main":[[C("Edit Fields1")]]},
    "Edit Fields1":{"main":[[C("Pinecone Vector Store1")]]},
    "Pinecone Vector Store1":{"main":[[C("Aggregate1")]]},
    "Aggregate1":{"main":[[C("Text3")]]},
    "Text3":{"main":[[C("Set metadata2")]]},
    "Set metadata2":{"main":[[C("Be Star Ticketing Agent")]]},
    # RAG AI sub-nodes
    "Simple Memory":{"ai_memory":[[C("Reformer","ai_memory")]]},
    "Log Reformer Rekaz":{"ai_tool":[[C("Azure OpenAI Chat Model5","ai_tool")]]},
    "Azure OpenAI Chat Model5":{"ai_languageModel":[[C("Reformer","ai_languageModel")]]},
    "Log Reformer Rekaz4":{"ai_tool":[[C("Azure OpenAI Chat Model7","ai_tool")]]},
    "Azure OpenAI Chat Model7":{"ai_languageModel":[[C("Information Extractor","ai_languageModel")]]},
    "Embeddings Azure OpenAI":{"ai_embedding":[[C("Pinecone Vector Store1","ai_embedding")]]},
    # Agent AI sub-nodes
    "Azure OpenAI Chat Model4":{"ai_languageModel":[[C("Be Star Ticketing Agent","ai_languageModel")]]},
    "Log Reformer Rekaz3":{"ai_tool":[[C("Azure OpenAI Chat Model4","ai_tool")]]},
    "Postgres Chat Memory1":{"ai_memory":[[C("Be Star Ticketing Agent","ai_memory")]]},
    # Agent → Guardrails → Output
    "Be Star Ticketing Agent":{"main":[[C("Guardrails Supervisor")]]},
    "Azure OpenAI Chat Model1":{"ai_languageModel":[[C("Guardrails Supervisor","ai_languageModel")]]},
    "Postgres Chat Memory":{"ai_memory":[[C("Guardrails Supervisor","ai_memory")]]},
    "Guardrails Supervisor":{"main":[[C("Log Usr Messages")]]},
    # Output (Switch Answer removed, direct to WhatsApp)
    "Log Usr Messages":{"main":[[C("Send presence1")]]},
    "Send presence1":{"main":[[C("Splite the messages")]]},
    "Splite the messages":{"main":[[C("Skip First One"),C("Send text")]]},
    "Send text":{"main":[[C("Log AI Messages1")]]},
    "Skip First One":{"main":[[C("Loop Over Items")]]},
    "Loop Over Items":{"main":[[C("No Operation, do nothing")],[C("Send text1")]]},
    "Send text1":{"main":[[C("Log AI Messages")]]},
    "Log AI Messages":{"main":[[C("Loop Over Items")]]},
    # Approval Flow
    "Approval Webhook":{"main":[[C("Send PDF Ticket")]]},
    "Send PDF Ticket":{"main":[[C("Send Confirmation Text")]]},
}

# ============================================================
# OUTPUT
# ============================================================
workflow = {
    "nodes": nodes,
    "connections": connections,
    "pinData": {},
    "meta": {
        "templateCredsSetupCompleted": True,
        "instanceId": "8df4082ac81111d2321c538ef34013493a96dd3b14b3af10e13ce9c3849e34d3"
    }
}

output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "n8n_workflow", "be_star_ticketing_v2.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)
print(f"[OK] Workflow saved to: {output_path}")
print(f"   Total nodes: {len(nodes)}")
