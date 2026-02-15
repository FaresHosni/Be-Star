import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_FILE = os.path.join(DIR, "be_star_ticketing_v6.json")
BACKEND_URL = "http://38.242.139.159:3005"

def patch_workflow():
    if not os.path.exists(WORKFLOW_FILE):
        print(f"Error: {WORKFLOW_FILE} not found")
        return

    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        wf = json.load(f)

    # 1. Define the new node
    save_image_node = {
        "parameters": {
            "method": "POST",
            "url": f"{BACKEND_URL}/api/tickets/save-draft",
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
            "jsonBody": "={{ JSON.stringify({\n  user_phone: $('User Phone ID').first().json.User_phone_ID,\n  ticket_index: 0,\n  field: 'payment_proof',\n  value: 'data:image/jpeg;base64,' + $('Get Image Base64').first().json.data.base64\n}) }}",
            "options": {}
        },
        "name": "Save Image to Draft",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.1,
        "position": [
            -14300, 
            4048
        ],
        "id": "save-image-draft-001"
    }

    # 2. Add the node to the list
    # Check if it already exists to avoid duplicates
    existing_idx = next((i for i, n in enumerate(wf["nodes"]) if n["name"] == "Save Image to Draft"), -1)
    if existing_idx != -1:
        print("Node 'Save Image to Draft' already exists. Updating...")
        wf["nodes"][existing_idx] = save_image_node
    else:
        wf["nodes"].append(save_image_node)
        print("Added 'Save Image to Draft' node.")

    # 3. Update connections
    # We want: image -> Save Image to Draft -> Memory + Model PreEnter2
    
    # Connect 'image' to 'Save Image to Draft'
    if "image" in wf["connections"]:
        wf["connections"]["image"]["main"] = [[
            {
                "node": "Save Image to Draft",
                "type": "main",
                "index": 0
            }
        ]]
    
    # Connect 'Save Image to Draft' to 'Memory + Model PreEnter2'
    wf["connections"]["Save Image to Draft"] = {
        "main": [[
            {
                "node": "Memory + Model PreEnter2",
                "type": "main",
                "index": 0
            }
        ]]
    }

    # Verify positions to make it look nice (optional, but good for debugging)
    # Get 'image' position
    image_node = next((n for n in wf["nodes"] if n["name"] == "image"), None)
    memory_node = next((n for n in wf["nodes"] if n["name"] == "Memory + Model PreEnter2"), None)
    
    if image_node and memory_node:
        # Place it between image and memory
        # image: [-14560, 4220] (approx)
        # memory: [-14080, 4048]
        # Let's set it to [-14300, 4048]
        save_image_node["position"] = [
            (image_node["position"][0] + memory_node["position"][0]) // 2,
            memory_node["position"][1]
        ]

    # Save the file
    with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=True)
    
    print(f"Successfully patched {WORKFLOW_FILE}")

if __name__ == "__main__":
    patch_workflow()
