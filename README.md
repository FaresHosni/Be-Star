# 🌟 Be Star - كن نجماً

نظام حجز تذاكر إيفنت "كن نجماً" المتكامل

## 📋 معلومات الإيفنت
- **التاريخ:** 2026-02-11
- **المكان:** سوهاج - الكوامل - قاعة قناة السويس
- **تذاكر VIP:** 500 جنيه
- **تذاكر Student:** 100 جنيه

---

## 🚀 تشغيل المشروع

### 1. Backend (Python FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
السيرفر هيشتغل على: http://localhost:8000

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
الداشبورد هتفتح على: http://localhost:5173

### 3. n8n Workflow
1. افتح n8n
2. اعمل Import للـ workflow من: `n8n_workflow/be_star_ticketing.json`
3. فعّل الـ Workflow

---

## 🔐 تسجيل الدخول للداشبورد
1. افتح http://localhost:5173
2. اضغط على "إنشاء حساب الأدمن الافتراضي"
3. سجل دخول بـ:
   - **الإيميل:** hsny4756@gmail.com
   - **كلمة المرور:** admin123

---

## 📁 هيكل المشروع
```
Be Star/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Database models
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Configuration
│   ├── routes/
│   │   ├── tickets.py       # Ticket APIs
│   │   ├── auth.py          # Authentication
│   │   ├── distributors.py  # Distributors
│   │   ├── chat.py          # Chat widget
│   │   └── stats.py         # Statistics
│   └── services/
│       ├── pdf_generator.py # PDF tickets
│       └── email_service.py # Email sending
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Tickets.jsx
│   │   │   ├── Distributors.jsx
│   │   │   └── Login.jsx
│   │   └── components/
│   │       ├── Sidebar.jsx
│   │       └── ChatWidget.jsx
│   └── package.json
└── n8n_workflow/
    └── be_star_ticketing.json
```

---

## 🔗 API Endpoints

### التذاكر
- `POST /api/tickets` - إنشاء تذكرة
- `GET /api/tickets` - عرض كل التذاكر
- `GET /api/tickets/check/{phone}` - البحث بـ رقم التليفون
- `POST /api/tickets/{id}/approve` - موافقة/رفض
- `POST /api/tickets/activate` - تفعيل تذكرة

### Chat Widget (للربط مع n8n)
- `POST /api/chat/send` - إرسال رسالة
- `POST /api/chat/webhook/n8n` - استقبال رد من n8n

---

## ⚙️ Evolution API
- **URL:** http://38.242.139.159:8080
- **Instance:** Mr. AI
- **رقم الإشعارات:** +201557368364

---

© 2026 Be Star - كن نجماً | Mr AI Labs
