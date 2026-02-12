import json
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

path = r"d:\ME\Mr.ai\Be Star\n8n_workflow\be_star_ticketing_v6.json"

print(f"Loading {path}...")
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update 'Memory + Model PreEnter2' to inject phone into Input
    pre_enter_found = False
    for node in data['nodes']:
        if node.get('name') == 'Memory + Model PreEnter2':
            pre_enter_found = True
            print("Found 'Memory + Model PreEnter2'. Updating Input expression...")
            
            # We want to prepend [User Phone: 01xxxx] to the existing logic.
            # Existing logic is complex nested $if.
            # We wrap it.
            
            # Context: $('User Phone ID').item.json.User_phone_ID
            # We use .first() to be safe.
            
            # Original Value was:
            # "={{ $if($('Text4').isExecuted, ... ) }}"
            
            # We construct:
            # "={{ '[رقم العميل: ' + $('User Phone ID').first().json.User_phone_ID + '] ' + ($if( ... )) }}"
            
            # Let's locate the 'Input' assignment
            for assignment in node['parameters']['assignments']['assignments']:
                if assignment['name'] == 'Input':
                    original_val = assignment['value']
                    # Strip "={{ " and " }}" if present, or just wrap it?
                    # n8n expressions start with ={{.
                    if original_val.startswith("={{") and original_val.endswith("}}"):
                        inner = original_val[3:-2].strip()
                        new_val = "={{ '[رقم العميل: ' + $('User Phone ID').first().json.User_phone_ID + '] ' + (" + inner + ") }}"
                    else:
                        # Fallback if structure is different
                        new_val = "={{ '[رقم العميل: ' + $('User Phone ID').first().json.User_phone_ID + '] ' + " + original_val + " }}"
                    
                    assignment['value'] = new_val
                    print("✅ Injected User Phone into Input field.")
                    break
            break

    # 2. Update Agent Prompt to use this info
    agent_found = False
    new_prompt = """=أنت "عمر" مساعد ذكي لحجز تذاكر فعالية "كن نجماً - Be Star" 🌟
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
2. رقم الموبايل (Phone):
   - ستجد "رقم العميل" الحالي في بداية كلامه (بين قوسين []).
   - اسأله: "تحب أسجل بنفس رقم الواتساب ده (واذكر الرقم) ولا رقم تاني؟".
   - لو قال "نفسه" أو "تمام"، استخدم هذا الرقم.
   - لو قال رقم تاني، خده منه.
3. نوع التذكرة (Type): VIP أو Student
4. الإيميل (Email)
5. صورة الدفع (Payment Proof)

⚙️ قواعد صارمة:
1. اسأل عن عدد التذاكر أولاً.
2. لكل تذكرة (رقم 1، 2...)، اجمع البيانات واحدة تلو الأخرى.
3. 🔴 **تنبيه هام:** بمجرد ما العميل يعطيك معلومة، **استخدم أداة `save_draft` فوراً**.
4. الأداة `save_draft` هترد عليك تقولك إيه اللي ناقص. بلغ العميل باللي ناقص.
5. لما تبعت صورة الدفع، الأداة هتقولك "تم حجز التذكرة بنجاح". ساعتها بس تقدر تبارك للعميل.
6. لو العميل بعت صورة لكل التذاكر، ابعتها لكل تذكرة لوحدها باستخدام الأداة.

📸 **قواعد خاصة بالصور (هام جداً):**
- إذا وصلك نص يبدأ بـ "العميل بعت صورة" أو "وصف الصورة"، فهذا هو إثبات الدفع.
- **يجب** استدعاء الأداة فوراً: `save_draft(..., field="payment", value="وصف الصورة...")`.
- ⛔ **تحذير:** لا ترد أبداً برسائل مثل "تم الاستلام" أو "جاري المراجعة" من عندك.
- **تجاهل** أي معلومات قديمة عن "مراجعة خلال 6 ساعات". نظام المسودة هو المصدر الوحيد للحقيقة. الحجز يتم لحظياً عبر الأداة.

🚫 ممنوعات:
- لا تقم بتأكيد الحجز من نفسك. الحجز يتم فقط لما الأداة ترد بـ "Completed".
- لا تستخدم أي أداة أخرى للحجز غير `save_draft`.
"""

    for node in data['nodes']:
        if node.get('name') == 'Be Star Ticketing Agent':
            node['parameters']['options']['systemMessage'] = new_prompt
            agent_found = True
            print("✅ Updated Agent Prompt with Phone Question logic.")
            break

    if pre_enter_found and agent_found:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved enhanced workflow to {path}")
    else:
        print(f"❌ Error: PreEnter Found: {pre_enter_found}, Agent Found: {agent_found}")

except Exception as e:
    print(f"❌ Error: {e}")
