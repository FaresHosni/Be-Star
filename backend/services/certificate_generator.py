"""
Premium Certificate PDF Generator — Be Star
Generates elegant gold & black certificates using ReportLab with Arabic support.
"""
import os
from io import BytesIO
from reportlab.lib.colors import HexColor, white, Color
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math

# Arabic text reshaping
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# Colors
GOLD = HexColor("#D4AF37")
GOLD_LIGHT = HexColor("#F5E6A3")
GOLD_DARK = HexColor("#B8941F")
DARK_BG = HexColor("#0a0a0a")
DARK_CARD = HexColor("#141414")
CREAM = HexColor("#FFF8E7")

# Fonts
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

try:
    pdfmetrics.registerFont(TTFont('Amiri-Regular', '/app/fonts/Amiri-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', '/app/fonts/Amiri-Bold.ttf'))
    FONT_REGULAR = 'Amiri-Regular'
    FONT_BOLD = 'Amiri-Bold'
except Exception as e:
    print(f"Certificate: Error loading Arabic fonts: {e}")


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper display in PDF"""
    if not text:
        return ""
    if not ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def _draw_star(c, cx, cy, outer_r, inner_r, points=5, fill_color=GOLD):
    """Draw a star shape"""
    c.setFillColor(fill_color)
    p = c.beginPath()
    for i in range(points * 2):
        angle = math.pi / 2 + (i * math.pi / points)
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=True, stroke=False)


def _draw_laurel_branch(c, cx, cy, side="left", scale=1.0):
    """Draw a decorative laurel branch using leaves"""
    c.setFillColor(GOLD)
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(0.5)
    
    direction = 1 if side == "left" else -1
    
    # Stem
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5 * scale)
    p = c.beginPath()
    p.moveTo(cx, cy - 25 * mm * scale)
    p.curveTo(
        cx + direction * 5 * mm * scale, cy - 10 * mm * scale,
        cx + direction * 3 * mm * scale, cy + 5 * mm * scale,
        cx, cy + 25 * mm * scale
    )
    c.drawPath(p, stroke=True, fill=False)
    
    # Leaves along the stem
    for i in range(6):
        t = i / 5.0
        stem_y = cy - 25 * mm * scale + t * 50 * mm * scale
        
        leaf_size = (3.5 - abs(t - 0.5) * 2) * mm * scale
        
        c.saveState()
        c.setFillColor(GOLD)
        c.translate(cx + direction * (2 + t * 3) * mm * scale, stem_y)
        c.rotate(direction * (30 - i * 8))
        c.ellipse(
            -leaf_size * 0.4, -leaf_size,
            leaf_size * 0.4, leaf_size,
            fill=True, stroke=False
        )
        c.restoreState()


def _draw_ornamental_border(c, width, height, margin=5*mm):
    """Draw an ornamental double border with corner decorations"""
    # Outer border
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=False, stroke=True)
    
    # Inner border
    inner_m = margin + 3 * mm
    c.setLineWidth(0.8)
    c.rect(inner_m, inner_m, width - 2 * inner_m, height - 2 * inner_m, fill=False, stroke=True)
    
    # Corner decorations — small diamond shapes
    corner_size = 4 * mm
    corners = [
        (margin + 1.5 * mm, margin + 1.5 * mm),
        (width - margin - 1.5 * mm, margin + 1.5 * mm),
        (margin + 1.5 * mm, height - margin - 1.5 * mm),
        (width - margin - 1.5 * mm, height - margin - 1.5 * mm),
    ]
    for cx, cy in corners:
        c.setFillColor(GOLD)
        p = c.beginPath()
        p.moveTo(cx, cy + corner_size)
        p.lineTo(cx + corner_size, cy)
        p.lineTo(cx, cy - corner_size)
        p.lineTo(cx - corner_size, cy)
        p.close()
        c.drawPath(p, fill=True, stroke=False)


def generate_certificate_pdf(
    guest_name: str,
    total_points: int,
    rank: int,
    total_participants: int,
    event_name: str = None
) -> bytes:
    """
    Generate a premium certificate PDF.
    
    Returns: PDF as bytes
    """
    buffer = BytesIO()
    
    # A4 Landscape
    width, height = 297 * mm, 210 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # ━━━━━━━━━━━ BACKGROUND ━━━━━━━━━━━
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Subtle radial gradient effect (concentric rectangles)
    for i in range(20):
        alpha = 0.02 - i * 0.001
        if alpha <= 0:
            break
        c.setFillColor(Color(0.83, 0.69, 0.22, alpha))
        inset = i * 8 * mm
        c.rect(inset, inset, width - 2 * inset, height - 2 * inset, fill=True, stroke=False)
    
    # ━━━━━━━━━━━ ORNAMENTAL BORDER ━━━━━━━━━━━
    _draw_ornamental_border(c, width, height)
    
    # ━━━━━━━━━━━ TOP HEADER BAND ━━━━━━━━━━━
    header_h = 28 * mm
    header_y = height - 12 * mm - header_h
    
    # Gold gradient band
    c.setFillColor(GOLD)
    c.rect(15 * mm, header_y, width - 30 * mm, header_h, fill=True, stroke=False)
    
    # Darker gold stripe at top of band
    c.setFillColor(GOLD_DARK)
    c.rect(15 * mm, header_y + header_h - 2 * mm, width - 30 * mm, 2 * mm, fill=True, stroke=False)
    
    # Event name
    c.setFillColor(DARK_BG)
    c.setFont(FONT_BOLD, 28)
    c.drawCentredString(width / 2, header_y + 14 * mm, "Be Star")
    
    # Arabic subtitle
    c.setFont(FONT_REGULAR, 14)
    arabic_event = reshape_arabic(event_name or "كن نجماً")
    c.drawCentredString(width / 2, header_y + 5 * mm, arabic_event)
    
    # ━━━━━━━━━━━ STARS DECORATION ━━━━━━━━━━━
    # Three stars above the title
    star_y = header_y - 12 * mm
    _draw_star(c, width / 2, star_y, 5 * mm, 2 * mm)
    _draw_star(c, width / 2 - 18 * mm, star_y, 3 * mm, 1.2 * mm)
    _draw_star(c, width / 2 + 18 * mm, star_y, 3 * mm, 1.2 * mm)
    
    # ━━━━━━━━━━━ CERTIFICATE TITLE ━━━━━━━━━━━
    title_y = star_y - 18 * mm
    c.setFillColor(GOLD_LIGHT)
    c.setFont(FONT_BOLD, 36)
    cert_title = reshape_arabic("شهادة تقدير")
    c.drawCentredString(width / 2, title_y, cert_title)
    
    # Decorative line under title
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    line_w = 60 * mm
    c.line(width / 2 - line_w, title_y - 5 * mm, width / 2 + line_w, title_y - 5 * mm)
    
    # Small dots at line ends
    c.setFillColor(GOLD)
    c.circle(width / 2 - line_w, title_y - 5 * mm, 1.5 * mm, fill=True, stroke=False)
    c.circle(width / 2 + line_w, title_y - 5 * mm, 1.5 * mm, fill=True, stroke=False)
    
    # ━━━━━━━━━━━ LAUREL BRANCHES ━━━━━━━━━━━
    laurel_y = title_y - 25 * mm
    _draw_laurel_branch(c, width / 2 - 55 * mm, laurel_y, side="left", scale=0.8)
    _draw_laurel_branch(c, width / 2 + 55 * mm, laurel_y, side="right", scale=0.8)
    
    # ━━━━━━━━━━━ PRESENTED TO ━━━━━━━━━━━
    presented_y = title_y - 18 * mm
    c.setFillColor(GOLD)
    c.setFont(FONT_REGULAR, 13)
    presented_text = reshape_arabic("تُمنح هذه الشهادة إلى")
    c.drawCentredString(width / 2, presented_y, presented_text)
    
    # ━━━━━━━━━━━ GUEST NAME (HERO) ━━━━━━━━━━━
    name_y = presented_y - 18 * mm
    c.setFillColor(white)
    c.setFont(FONT_BOLD, 32)
    display_name = reshape_arabic(guest_name)
    c.drawCentredString(width / 2, name_y, display_name)
    
    # Underline for name
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.setDash(1, 1)
    name_line_w = 50 * mm
    c.line(width / 2 - name_line_w, name_y - 5 * mm, width / 2 + name_line_w, name_y - 5 * mm)
    c.setDash()  # Reset dash
    
    # ━━━━━━━━━━━ ACHIEVEMENT TEXT ━━━━━━━━━━━
    achieve_y = name_y - 20 * mm
    c.setFillColor(GOLD_LIGHT)
    c.setFont(FONT_REGULAR, 14)
    
    achieve_line1 = reshape_arabic(f"تقديراً لتميزه في مسابقة كن نجماً")
    c.drawCentredString(width / 2, achieve_y, achieve_line1)
    
    # Score highlight box
    score_y = achieve_y - 18 * mm
    box_w = 140 * mm
    box_h = 16 * mm
    c.setFillColor(Color(0.83, 0.69, 0.22, 0.1))
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.roundRect(width / 2 - box_w / 2, score_y - 4 * mm, box_w, box_h, 3 * mm, fill=True, stroke=True)
    
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 16)
    score_text = reshape_arabic(f"حصل على {total_points} نقطة  —  المركز {rank} من {total_participants}")
    c.drawCentredString(width / 2, score_y + 2 * mm, score_text)
    
    # ━━━━━━━━━━━ RANK BADGE (Right Side) ━━━━━━━━━━━
    badge_x = width - 42 * mm
    badge_y = score_y + 15 * mm
    badge_r = 13 * mm
    
    # Outer circle
    c.setFillColor(GOLD)
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(2)
    c.circle(badge_x, badge_y, badge_r, fill=True, stroke=True)
    
    # Inner circle
    c.setFillColor(DARK_BG)
    c.circle(badge_x, badge_y, badge_r - 2.5 * mm, fill=True, stroke=False)
    
    # Rank number
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 24)
    c.drawCentredString(badge_x, badge_y + 2 * mm, f"#{rank}")
    
    # Label
    c.setFont(FONT_REGULAR, 7)
    rank_label = reshape_arabic("المركز")
    c.drawCentredString(badge_x, badge_y - 7 * mm, rank_label)
    
    # ━━━━━━━━━━━ VERIFIED SEAL (Left Side) ━━━━━━━━━━━
    seal_x = 42 * mm
    seal_y = score_y + 15 * mm
    seal_r = 13 * mm
    
    # Outer circle
    c.setFillColor(GOLD)
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(2)
    c.circle(seal_x, seal_y, seal_r, fill=True, stroke=True)
    
    # Inner circle
    c.setFillColor(DARK_BG)
    c.circle(seal_x, seal_y, seal_r - 2.5 * mm, fill=True, stroke=False)
    
    # Checkmark
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.5)
    p = c.beginPath()
    p.moveTo(seal_x - 5 * mm, seal_y)
    p.lineTo(seal_x - 1.5 * mm, seal_y - 4 * mm)
    p.lineTo(seal_x + 5 * mm, seal_y + 5 * mm)
    c.drawPath(p, stroke=True, fill=False)
    
    # Label
    c.setFillColor(GOLD)
    c.setFont(FONT_BOLD, 7)
    c.drawCentredString(seal_x, seal_y - 9 * mm, "VERIFIED")
    
    # ━━━━━━━━━━━ FOOTER BAND ━━━━━━━━━━━
    footer_h = 18 * mm
    c.setFillColor(GOLD)
    c.rect(15 * mm, 12 * mm, width - 30 * mm, footer_h, fill=True, stroke=False)
    
    # Darker stripe at bottom
    c.setFillColor(GOLD_DARK)
    c.rect(15 * mm, 12 * mm, width - 30 * mm, 2 * mm, fill=True, stroke=False)
    
    c.setFillColor(DARK_BG)
    c.setFont(FONT_BOLD, 13)
    footer_text = reshape_arabic("نتمنى لك المزيد من التميز والنجاح")
    c.drawCentredString(width / 2, 19 * mm, footer_text)
    
    # Event info in footer
    c.setFont(FONT_REGULAR, 8)
    event_date = os.getenv("EVENT_DATE", "11 Feb 2026")
    event_location = reshape_arabic("سوهاج - الكوامل - قاعة قناة السويس")
    c.drawString(20 * mm, 14 * mm, f"{event_date}")
    c.drawRightString(width - 20 * mm, 14 * mm, event_location)
    
    # ━━━━━━━━━━━ FINALIZE ━━━━━━━━━━━
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
