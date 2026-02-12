import json
import sys
import re

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
            
            # Current JSON Body is a string with expressions
            # We want to replace the 'value' logic.
            # The structure is usually:
            # "jsonBody": "={\n  \"ticket_index\": ...,\n  \"field\": ...,\n  \"value\": $fromAI(...\n}"
            
            # Instead of parsing the string, we'll replace the full jsonBody expression with the robust one.
            
            # Robust Expression:
            # If AI value contains "وصف الصورة" AND Image Node Executed -> Use Image Base64.
            # Else -> Use AI value.
            
            new_expression = """={{
{
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
            print("✅ Updated 'value' expression to intercept image descriptions.")
            break

    if tool_found:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated workflow to {path}")
    else:
        print("❌ Error: Node 'Save Draft Tool' not found.")

except Exception as e:
    print(f"❌ Error: {e}")
