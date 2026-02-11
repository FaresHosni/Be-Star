"""
Email Service using Gmail SMTP
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional


# Email HTML Template
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background-color: #0a0a0a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: linear-gradient(145deg, #1a1a1a 0%, #0a0a0a 100%);
            border: 1px solid #D4AF37;
            border-radius: 15px;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
            color: #0a0a0a;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .content {
            padding: 30px;
        }
        .greeting {
            font-size: 20px;
            color: #D4AF37;
            margin-bottom: 20px;
        }
        .info-box {
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .info-label {
            color: #D4AF37;
        }
        .ticket-code {
            text-align: center;
            font-size: 32px;
            color: #D4AF37;
            letter-spacing: 8px;
            margin: 20px 0;
            font-weight: bold;
        }
        .footer {
            background: #1a1a1a;
            padding: 20px;
            text-align: center;
            color: #888;
            font-size: 14px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #D4AF37, #FFD700);
            color: #0a0a0a;
            padding: 15px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 كن نجماً - Be Star 🌟</h1>
        </div>
        <div class="content">
            <div class="greeting">مرحباً {{ customer_name }}! 🎉</div>
            <p>تهانينا! تم تأكيد حجز تذكرتك بنجاح.</p>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-label">نوع التذكرة</span>
                    <span>{{ ticket_type }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">التاريخ</span>
                    <span>{{ event_date }}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">المكان</span>
                    <span>{{ event_location }}</span>
                </div>
            </div>
            
            <p style="text-align: center;">كود التذكرة الخاص بك:</p>
            <div class="ticket-code">{{ ticket_code }}</div>
            
            <p>يرجى الاحتفاظ بهذا الإيميل وإظهاره عند الدخول.</p>
            <p>التذكرة مرفقة بهذا الإيميل كملف PDF.</p>
        </div>
        <div class="footer">
            <p>نتمنى لك وقتاً رائعاً! 🌟</p>
            <p>فريق كن نجماً</p>
        </div>
    </div>
</body>
</html>
"""


async def send_ticket_email(
    to_email: str,
    customer_name: str,
    ticket_code: str,
    ticket_type: str,
    pdf_bytes: Optional[bytes] = None
) -> dict:
    """Send ticket confirmation email with PDF attachment"""
    
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        return {"success": False, "error": "SMTP credentials not configured"}
    
    # Create message
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"🎟️ تذكرتك لإيفنت كن نجماً - {ticket_code}"
    
    # Create HTML body
    from jinja2 import Template
    template = Template(EMAIL_TEMPLATE)
    html_content = template.render(
        customer_name=customer_name,
        ticket_code=ticket_code,
        ticket_type=ticket_type,
        event_date=os.getenv("EVENT_DATE", "2026-02-11"),
        event_location=os.getenv("EVENT_LOCATION", "سوهاج - الكوامل - قاعة قناة السويس")
    )
    
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    # Attach PDF if provided
    if pdf_bytes:
        pdf_attachment = MIMEBase("application", "pdf")
        pdf_attachment.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_attachment)
        pdf_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename=ticket_{ticket_code}.pdf"
        )
        msg.attach(pdf_attachment)
    
    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        return {"success": True, "message": "تم إرسال الإيميل بنجاح"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_admin_notification(
    ticket_code: str,
    customer_name: str,
    customer_phone: str,
    ticket_type: str,
    price: int
) -> dict:
    """Send notification to admin about new ticket"""
    
    admin_email = os.getenv("ADMIN_EMAIL")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not admin_email or not smtp_user:
        return {"success": False, "error": "Admin email not configured"}
    
    html = f"""
    <html dir="rtl">
    <body style="font-family: Arial; direction: rtl;">
        <h2 style="color: #D4AF37;">🎟️ طلب حجز تذكرة جديد</h2>
        <p><strong>الاسم:</strong> {customer_name}</p>
        <p><strong>الهاتف:</strong> {customer_phone}</p>
        <p><strong>نوع التذكرة:</strong> {ticket_type}</p>
        <p><strong>السعر:</strong> {price} جنيه</p>
        <p><strong>الكود:</strong> {ticket_code}</p>
        <hr>
        <p>يرجى مراجعة إثبات الدفع والموافقة من لوحة التحكم.</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = admin_email
    msg["Subject"] = f"🎟️ طلب حجز جديد - {customer_name}"
    msg.attach(MIMEText(html, "html", "utf-8"))
    
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
