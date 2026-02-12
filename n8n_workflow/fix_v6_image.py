import json
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

path = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v6.json"

print(f"Loading {path}...")
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tool_found = False
    for node in data['nodes']:
        if node.get('name') == 'Save Draft Tool':
            tool_found = True
            print("Found Save Draft Tool. Updating jsonBody expression...")
            
            # Robust Expression with user_phone and image handling
            new_expression = """={{
{
  "user_phone": $('User Phone ID').first().json.User_phone_ID,
  "ticket_index": $fromAI("ticket_index", "1"),
  "field": $fromAI("field", "name"),
  "value": (
    ($fromAI("value", "") || "").includes("وصف الصورة") || 
    ($fromAI("value", "") || "").includes("User sent image") ||
    ($fromAI("value", "") || "").includes("العميل بعت صورة")
  ) && $('Get Image Base64') && $('Get Image Base64').first() ? "data:image/jpeg;base64," + $('Get Image Base64').first().json.data.base64 : $fromAI("value", "").replace(/```/g, "").trim()
}
}}"""
            
            node['parameters']['jsonBody'] = new_expression
            print("✅ Updated 'jsonBody' with 'user_phone' and image logic.")
            break

    if tool_found:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated workflow to {path}")
    else:
        print("❌ Error: Node 'Save Draft Tool' not found.")

except Exception as e:
    print(f"❌ Error: {e}")
