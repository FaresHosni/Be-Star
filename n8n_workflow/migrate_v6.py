import json
import re

path_v5 = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v5.json"
path_v6 = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v6.json"

print(f"Loading {path_v5}...")
with open(path_v5, 'r', encoding='utf-8') as f:
    data = json.load(f)

# New Prompt
new_system_message = """=أنت "عمر" مساعد ذكي لحجز تذاكر فعالية "كن نجماً - Be Star" 🌟
📋 معلومات الفعالية:
🎉 الاسم: كن نجماً - Be Star
📅 الموعد: 11 فبراير 2026
📍 المكان: سوهاج - الكوامل - قاعة قناة السويس
💰 الأسعار: VIP: 500 جنيه | طلبة: 100 جنيه
💳 الدفع: فودافون كاش على الرقم 01557368364

📝 نظام المحادثة الجديد (Drafting System):
هدفك هو جمع بيانات 5 خانات إجبارية لكل تذكرة وحفظها فوراً في النظام.
الخانات هي:
1. الاسم (Name)
2. رقم الموبايل (Phone) - لصاحب التذكرة
3. نوع التذكرة (Type): VIP أو Student
4. الإيميل (Email)
5. صورة الدفع (Payment Proof)

⚙️ قواعد صارمة:
1. اسأل عن عدد التذاكر أولاً.
2. لكل تذكرة (رقم 1، 2...)، اجمع البيانات واحدة تلو الأخرى.
3. 🔴 **تنبيه هام:** بمجرد ما العميل يعطيك معلومة (مثلاً الاسم)، **استخدم أداة `save_draft` فوراً**.
   - لا تنتظر تجميع كل المعلومات. احفظ كل خانة في وقتها.
4. الأداة `save_draft` هترد عليك تقولك إيه اللي ناقص. بلغ العميل باللي ناقص.
5. لما تبعت صورة الدفع، الأداة هتقولك "تم حجز التذكرة بنجاح". ساعتها بس تقدر تبارك للعميل.
6. لو العميل بعت صورة لكل التذاكر، ابعتها لكل تذكرة لوحدها باستخدام الأداة.

🚫 ممنوعات:
- لا تقم بتأكيد الحجز من نفسك. الحجز يتم فقط لما الأداة ترد بـ "Completed".
- لا تستخدم أي أداة أخرى للحجز غير `save_draft`.

أمثلة لاستخدام الأداة:
- العميل: "اسمي أحمد علي"
  -> Tool: save_draft(ticket_index=1, field="name", value="Ahmed Ali")
- العميل: "رقمي 010xxxxx"
  -> Tool: save_draft(ticket_index=1, field="phone", value="010xxxxx")
"""

updated_prompt = False
updated_tool = False

for node in data['nodes']:
    # 1. Update Agent Prompt
    if node.get('name') == 'Be Star Ticketing Agent':
        node['parameters']['options']['systemMessage'] = new_system_message
        updated_prompt = True
        print("Updated Agent Prompt.")

    # 2. Update Tool to 'Save Draft Tool'
    if node.get('name') == 'Create Booking Tool':
        node['name'] = 'Save Draft Tool'
        params = node['parameters']
        params['url'] = "http://38.242.139.159:3005/api/tickets/save-draft"
        params['toolDescription'] = "Use this tool immediately after receiving ANY piece of information (Name, Phone, Type, Email, Payment). Pass user_phone, ticket_index (1-based), field (name/phone/type/email/payment), and value."
        
        # New JSON Body
        # We need to correctly escape logic expressions for n8n
        # user_phone comes from context
        # ticket_index, field, value come from AI
        
        json_body = """={{ JSON.stringify({ 
    user_phone: $('User Phone ID').first().json.User_phone_ID, 
    ticket_index: $fromAI('ticket_index', 'Ticket Number (starting from 1)', 'number'),
    field: $fromAI('field', 'Field name: name, phone, type, email, or payment', 'string'),
    value: $fromAI('value', ' The value of the field (clean text, no markdown)', 'string').replace(/```/g, '').trim()
}) }}"""
        
        params['jsonBody'] = json_body
        updated_tool = True
        print("Transform Create Booking Tool -> Save Draft Tool.")

if updated_prompt and updated_tool:
    with open(path_v6, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Successfully created {path_v6}")
else:
    print("Error: Could not find nodes to update.")
