import json
import os

# Define credentials and settings
EVOLUTION_INSTANCE_NAME = "f9908d1b-29f5-441b-a843-dd5021dc0370"
EVOLUTION_API_KEY = "B1CEB4BA7A4D-4316-AC23-B1E79C49F557"
EVOLUTION_BASE_URL = "http://38.242.139.159:8080"
CREDENTIAL_ID = "evolutionApi-bestar-cred"
CREDENTIAL_NAME = "Be Star WhatsApp"

input_file = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v2.json"
output_file = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v3.json"

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update nodes
for node in data['nodes']:
    # Update Evolution API nodes
    if node['type'] == 'n8n-nodes-evolution-api-english.evolutionApi':
        # Update credentials
        if 'credentials' in node:
            if 'evolutionApi' in node['credentials']:
                node['credentials']['evolutionApi'] = {
                    "id": CREDENTIAL_ID,
                    "name": CREDENTIAL_NAME
                }
        
        # Update instanceName parameter if it exists and is static string (not expression)
        if 'parameters' in node:
            if 'instanceName' in node['parameters'] and not str(node['parameters']['instanceName']).startswith('='):
                 node['parameters']['instanceName'] = EVOLUTION_INSTANCE_NAME

print(f"Updated workflow saved to: {output_file}")
print("Note: You will still need to create the credential in n8n with these details:")
print(f"  - Name: {CREDENTIAL_NAME}")
print(f"  - Base URL: {EVOLUTION_BASE_URL}")
print(f"  - API Key: {EVOLUTION_API_KEY}")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
