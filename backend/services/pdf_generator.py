"""
PDF Ticket Generator Service - With Arabic Support (Fixed)
"""
import qrcode
from io import BytesIO
import os
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Arabic text reshaping
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False


# Colors
GOLD = HexColor("#D4AF37")
DARK_BG = HexColor("#0a0a0a")


# Try to register Arabic-compatible fonts
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

# Register Arabic fonts
try:
    pdfmetrics.registerFont(TTFont('Amiri-Regular', '/app/fonts/Amiri-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', '/app/fonts/Amiri-Bold.ttf'))
    FONT_REGULAR = 'Amiri-Regular'
    FONT_BOLD = 'Amiri-Bold'
except Exception as e:
    print(f"Error loading Arabic fonts: {e}")
    # Fallback to Helvetica
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper display in PDF"""
    if not text:
        return ""
    if not ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception as e:
        print(f"Error reshaping Arabic text: {e}")
        return text


def generate_qr_code_image(data: str) -> BytesIO:
    """Generate QR code and return as BytesIO"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#D4AF37", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def generate_ticket_pdf(
    ticket_code: str,
    ticket_type: str,
    customer_name: str,
    price: int
) -> bytes:
    """Generate ticket as PDF using ReportLab with Arabic support"""
    
    buffer = BytesIO()
    width, height = 105*mm, 175*mm  # Taller to fit QR code
    
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Background
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Gold border
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(3*mm, 3*mm, width-6*mm, height-6*mm, fill=False, stroke=True)
    
    # Header band
    c.setFillColor(GOLD)
    c.rect(3*mm, height-35*mm, width-6*mm, 32*mm, fill=True, stroke=False)
    
    # Event name - English
    c.setFillColor(DARK_BG)
    c.setFont(FONT_BOLD, 26)
    c.drawCentredString(width/2, height-16*mm, "Be Star")
    
    # Arabic subtitle
    c.setFont(FONT_REGULAR, 14)
    arabic_title = reshape_arabic("كن نجماً")
    c.drawCentredString(width/2, height-26*mm, arabic_title)
    
    # Ticket type badge
    badge_color = GOLD if ticket_type == "VIP" else HexColor("#C0C0C0")
    c.setFillColor(badge_color)
    c.roundRect(width/2-20*mm, height-46*mm, 40*mm, 9*mm, 4*mm, fill=True, stroke=False)
    
    c.setFillColor(DARK_BG)
    c.setFont(FONT_BOLD, 12)
    c.drawCentredString(width/2, height-43.5*mm, ticket_type)
    
    # Guest section
    y_pos = height - 56*mm
    
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 8)
    c.drawCentredString(width/2, y_pos, "GUEST NAME")
    
    # Customer name
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 16)
    display_name = reshape_arabic(customer_name)
    c.drawCentredString(width/2, y_pos-9*mm, display_name)
    
    y_pos -= 20*mm
    
    # Divider
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(10*mm, y_pos, width-10*mm, y_pos)
    
    y_pos -= 10*mm
    
    # Event details - Date & Time
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 7)
    c.drawString(12*mm, y_pos, "DATE")
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 10)
    event_date = os.getenv("EVENT_DATE", "11 Feb 2026")
    c.drawString(12*mm, y_pos-5*mm, event_date)
    
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 7)
    c.drawString(58*mm, y_pos, "TIME")
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 10)
    event_time = os.getenv("EVENT_TIME", "7:00 PM")
    c.drawString(58*mm, y_pos-5*mm, event_time)
    
    y_pos -= 14*mm
    
    # Venue - Two lines
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 7)
    c.drawCentredString(width/2, y_pos, "VENUE")
    
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 9)
    venue_line1 = reshape_arabic("سوهاج - الكوامل")
    venue_line2 = reshape_arabic("قاعة قناة السويس")
    c.drawCentredString(width/2, y_pos-6*mm, venue_line1)
    c.drawCentredString(width/2, y_pos-12*mm, venue_line2)
    
    y_pos -= 20*mm
    
    # QR and Ticket Code Section (Side by Side)
    qr_y_pos = y_pos - 35*mm
    
    # 1. QR Code (Left)
    from reportlab.lib.utils import ImageReader
    qr_buffer = generate_qr_code_image(ticket_code)
    qr_img = ImageReader(qr_buffer)
    qr_size = 30*mm
    # Draw QR on the left side
    c.drawImage(qr_img, 10*mm, qr_y_pos, width=qr_size, height=qr_size)
    
    # 2. Ticket Code (Right)
    # Center of the right side space
    right_center_x = width - 25*mm 
    
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 7)
    c.drawCentredString(right_center_x, qr_y_pos + 20*mm, "TICKET CODE")
    
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 18)
    c.drawCentredString(right_center_x, qr_y_pos + 12*mm, ticket_code)
    
    # Price removed as requested

    
    # Footer
    c.setFillColor(GOLD)
    c.rect(3*mm, 3*mm, width-6*mm, 12*mm, fill=True, stroke=False)
    
    c.setFillColor(DARK_BG)
    c.setFont(FONT_BOLD, 10)
    footer_text = reshape_arabic("نتمنى لك تجربة رائعة!")
    c.drawCentredString(width/2, 8*mm, footer_text)
    
    # Tear line (dashed)
    c.setStrokeColor(GOLD)
    c.setDash(3, 3)
    c.setLineWidth(1)
    c.line(0, 15*mm, width, 15*mm)
    
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generate_ticket_html(
    ticket_code: str,
    ticket_type: str,
    customer_name: str,
    price: int
) -> str:
    """Generate ticket HTML for preview"""
    return f"""
    <html>
    <head><title>Ticket {ticket_code}</title></head>
    <body style="background: #0a0a0a; color: white; font-family: Arial; text-align: center; padding: 20px;">
        <h1 style="color: #D4AF37;">Be Star - كن نجماً</h1>
        <h2>{ticket_type}</h2>
        <p><strong>Guest:</strong> {customer_name}</p>
        <p><strong>Code:</strong> {ticket_code}</p>
        <p><strong>Price:</strong> {price} EGP</p>
    </body>
    </html>
    """
