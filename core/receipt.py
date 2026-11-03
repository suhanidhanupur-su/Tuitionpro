import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_receipt_pdf(payment):
    """
    Generates a professional fee payment receipt as a PDF byte stream.
    Uses standard ReportLab fonts and vectors for crisp printing.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Primary colors
    brand_primary = colors.HexColor('#4F46E5')     # Indigo
    brand_dark    = colors.HexColor('#1E1B4B')     # Deep navy
    text_dark     = colors.HexColor('#1F2937')     # Gray 800
    text_muted    = colors.HexColor('#6B7280')     # Gray 500
    bg_light      = colors.HexColor('#F8FAFC')     # Slate 50
    border_color  = colors.HexColor('#E2E8F0')     # Slate 200
    accent_green  = colors.HexColor('#15803D')     # Green 700

    student = payment.student
    batch = student.batch

    # ── Top Header Banner ───────────────────────────────────────────
    p.setFillColor(brand_dark)
    p.rect(0, height - 110, width, 110, fill=True, stroke=False)

    # Institute Title
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 22)
    p.drawString(45, height - 48, 'TUITIONPRO ACADEMY')

    p.setFont('Helvetica', 10)
    p.setFillColor(colors.HexColor('#C7D2FE'))
    p.drawString(45, height - 68, 'Premier Coaching & Tuition Management')
    p.drawString(45, height - 84, 'Email: support@tuitionpro.local | Phone: +91 98765 43210')

    # Receipt Pill / Badge
    p.setFillColor(brand_primary)
    p.roundRect(width - 180, height - 75, 135, 34, 6, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 12)
    p.drawCentredString(width - 180 + (135 / 2), height - 54, 'FEE RECEIPT')

    # ── Receipt Meta Bar (Receipt No & Date) ─────────────────────────
    bar_y = height - 150
    p.setFillColor(bg_light)
    p.rect(45, bar_y, width - 90, 32, fill=True, stroke=True)
    p.setStrokeColor(border_color)

    p.setFillColor(text_dark)
    p.setFont('Helvetica-Bold', 10)
    p.drawString(58, bar_y + 11, 'Receipt No:')
    p.setFont('Helvetica', 10)
    p.drawString(125, bar_y + 11, payment.receipt_no)

    p.setFont('Helvetica-Bold', 10)
    p.drawString(width - 240, bar_y + 11, 'Payment Date:')
    p.setFont('Helvetica', 10)
    p.drawString(width - 155, bar_y + 11, payment.date.strftime('%d-%b-%Y'))

    # ── Student Information Box ────────────────────────────────────
    student_box_y = height - 265
    p.setFillColor(colors.white)
    p.setStrokeColor(border_color)
    p.roundRect(45, student_box_y, width - 90, 100, 6, fill=True, stroke=True)

    # Box title header
    p.setFillColor(colors.HexColor('#EEF2FF'))
    p.roundRect(45, student_box_y + 76, width - 90, 24, 6, fill=True, stroke=False)
    p.rect(45, student_box_y + 76, width - 90, 12, fill=True, stroke=False)
    p.setFillColor(brand_primary)
    p.setFont('Helvetica-Bold', 10)
    p.drawString(58, student_box_y + 83, 'STUDENT & ENROLLMENT DETAILS')

    # Row 1: Name & Phone
    p.setFont('Helvetica-Bold', 9)
    p.setFillColor(text_muted)
    p.drawString(58, student_box_y + 54, 'Student Name:')
    p.setFillColor(text_dark)
    p.setFont('Helvetica-Bold', 11)
    p.drawString(145, student_box_y + 54, student.name)

    p.setFont('Helvetica-Bold', 9)
    p.setFillColor(text_muted)
    p.drawString(width / 2 + 10, student_box_y + 54, 'Contact Phone:')
    p.setFillColor(text_dark)
    p.setFont('Helvetica', 10)
    p.drawString(width / 2 + 95, student_box_y + 54, student.phone or 'N/A')

    # Row 2: Batch & Subject
    p.setFont('Helvetica-Bold', 9)
    p.setFillColor(text_muted)
    p.drawString(58, student_box_y + 32, 'Assigned Batch:')
    p.setFillColor(text_dark)
    p.setFont('Helvetica', 10)
    batch_name = f"{batch.name} ({batch.subject})" if batch else "No Batch Assigned"
    p.drawString(145, student_box_y + 32, batch_name)

    p.setFont('Helvetica-Bold', 9)
    p.setFillColor(text_muted)
    p.drawString(width / 2 + 10, student_box_y + 32, 'Monthly Fee:')
    p.setFillColor(text_dark)
    p.setFont('Helvetica', 10)
    monthly_str = f"Rs. {batch.monthly_fee:,.2f}" if (batch and batch.monthly_fee) else "N/A"
    p.drawString(width / 2 + 95, student_box_y + 32, monthly_str)

    # Row 3: Email
    p.setFont('Helvetica-Bold', 9)
    p.setFillColor(text_muted)
    p.drawString(58, student_box_y + 12, 'Email Address:')
    p.setFillColor(text_dark)
    p.setFont('Helvetica', 9)
    p.drawString(145, student_box_y + 12, student.email or 'N/A')

    # ── Payment Details Section ────────────────────────────────────
    table_y = student_box_y - 145
    p.setStrokeColor(border_color)
    p.setFillColor(colors.white)
    p.roundRect(45, table_y, width - 90, 130, 6, fill=True, stroke=True)

    # Table Header Bar
    p.setFillColor(colors.HexColor('#1E293B'))
    p.roundRect(45, table_y + 106, width - 90, 24, 6, fill=True, stroke=False)
    p.rect(45, table_y + 106, width - 90, 12, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 9)
    p.drawString(58, table_y + 113, 'PARTICULARS')
    p.drawString(270, table_y + 113, 'PAYMENT MODE')
    p.drawString(410, table_y + 113, 'REFERENCE')
    p.drawRightString(width - 58, table_y + 113, 'AMOUNT (Rs.)')

    # Row 1: Values
    p.setFillColor(text_dark)
    p.setFont('Helvetica-Bold', 10)
    desc = payment.remarks if payment.remarks else "Tuition & Coaching Fee"
    p.drawString(58, table_y + 75, desc[:35])

    p.setFont('Helvetica', 10)
    p.drawString(270, table_y + 75, payment.get_mode_display())
    p.drawString(410, table_y + 75, (payment.reference or '—')[:16])

    p.setFont('Helvetica-Bold', 12)
    p.setFillColor(brand_primary)
    p.drawRightString(width - 58, table_y + 75, f"Rs. {payment.amount:,.2f}")

    # Divider line inside table
    p.setStrokeColor(border_color)
    p.line(45, table_y + 48, width - 45, table_y + 48)

    # Total Amount Row
    p.setFillColor(bg_light)
    p.rect(46, table_y + 1, width - 92, 46, fill=True, stroke=False)
    p.setFillColor(text_dark)
    p.setFont('Helvetica-Bold', 11)
    p.drawString(58, table_y + 20, 'Total Amount Received:')

    p.setFont('Helvetica-Bold', 14)
    p.setFillColor(accent_green)
    p.drawRightString(width - 58, table_y + 18, f"Rs. {payment.amount:,.2f}")

    # ── Fee Account Summary Box ────────────────────────────────────
    summary_y = table_y - 105
    p.setStrokeColor(border_color)
    p.setFillColor(colors.white)
    p.roundRect(45, summary_y, width - 90, 90, 6, fill=True, stroke=True)

    p.setFillColor(colors.HexColor('#F1F5F9'))
    p.roundRect(45, summary_y + 68, width - 90, 22, 6, fill=True, stroke=False)
    p.rect(45, summary_y + 68, width - 90, 10, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#475569'))
    p.setFont('Helvetica-Bold', 9)
    p.drawString(58, summary_y + 74, 'STUDENT FEE LEDGER STATEMENT')

    # Metrics
    exp_fee  = student.total_fee_expected
    tot_paid = student.total_paid
    pending  = student.pending_balance

    col1_x = 58
    col2_x = 220
    col3_x = 380

    p.setFont('Helvetica', 8)
    p.setFillColor(text_muted)
    p.drawString(col1_x, summary_y + 44, 'Total Expected Fee:')
    p.drawString(col2_x, summary_y + 44, 'Total Paid Till Date:')
    p.drawString(col3_x, summary_y + 44, 'Current Balance Status:')

    p.setFont('Helvetica-Bold', 11)
    p.setFillColor(text_dark)
    p.drawString(col1_x, summary_y + 24, f"Rs. {exp_fee:,.2f}")

    p.setFillColor(accent_green)
    p.drawString(col2_x, summary_y + 24, f"Rs. {tot_paid:,.2f}")

    if pending > 0:
        p.setFillColor(colors.HexColor('#DC2626'))  # Red
        balance_text = f"Rs. {pending:,.2f} Due"
    elif pending < 0:
        p.setFillColor(brand_primary)
        balance_text = f"Rs. {abs(pending):,.2f} Advance"
    else:
        p.setFillColor(accent_green)
        balance_text = "Fully Cleared"
    p.drawString(col3_x, summary_y + 24, balance_text)

    # ── Signatures & Footer ─────────────────────────────────────────
    sign_y = summary_y - 85

    # Authorized Signatory box
    p.setStrokeColor(colors.HexColor('#94A3B8'))
    p.line(width - 210, sign_y + 35, width - 58, sign_y + 35)
    p.setFillColor(text_dark)
    p.setFont('Helvetica-Bold', 9)
    p.drawCentredString(width - 134, sign_y + 20, 'Authorized Signatory')
    p.setFont('Helvetica', 8)
    p.setFillColor(text_muted)
    p.drawCentredString(width - 134, sign_y + 8, 'TuitionPro Academy')

    # Terms note
    p.setFont('Helvetica-Oblique', 8)
    p.setFillColor(text_muted)
    p.drawString(45, sign_y + 28, '* Note: Fees once paid are non-refundable.')
    p.drawString(45, sign_y + 14, '* This is a computer-generated fee receipt.')

    # Bottom border line
    p.setStrokeColor(brand_primary)
    p.setLineWidth(2)
    p.line(45, 30, width - 45, 30)

    p.setFont('Helvetica', 8)
    p.setFillColor(text_muted)
    p.drawString(45, 18, 'TuitionPro Management System')
    p.drawRightString(width - 45, 18, f"Generated on {payment.created_at.strftime('%d-%b-%Y %I:%M %p') if payment.created_at else 'N/A'}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.getvalue()
