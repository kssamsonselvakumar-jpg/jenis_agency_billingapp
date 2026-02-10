import streamlit as st
import pandas as pd
import os
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from num2words import num2words
import datetime

st.set_page_config(page_title="Jenis Agency - Tax Invoice", page_icon="🧾", layout="wide")

COMPANY_NAME = "ஜெனிஸ் ஏஜென்சி"
COMPANY_ADDRESS = "பாலக்காடு ரோடு வாழையார்"
COMPANY_PHONE = "9003223305"
COMPANY_EMAIL = "ramakrishnankarivilai@gmail.com"
COMPANY_STATE = "32-Kerala"

# ✅ USE UNICODE TAMIL FONT
FONT_FILE = "NotoSansTamil-Regular.ttf"
FONT_NAME = "NotoTamil"

if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1

if "customers" not in st.session_state:
    st.session_state.customers = {
        "ஸ்ரீ குரு பகவான் அருள்": {"contact": "9894536686", "address": ""}
    }

with st.sidebar:
    st.header("⚙️ Invoice Settings")
    invoice_no = st.session_state.invoice_counter
    st.info(f"**Invoice No:** {invoice_no}")
    st.divider()

    st.header("👥 Customer Management")
    col1, col2 = st.columns(2)
    with col1:
        new_customer_name = st.text_input("Customer Name")
    with col2:
        new_customer_phone = st.text_input("Phone")

    if st.button("➕ Save Customer"):
        if new_customer_name:
            st.session_state.customers[new_customer_name] = {
                "contact": new_customer_phone,
                "address": ""
            }
            st.success("Customer saved!")

    st.divider()
    customer_list = list(st.session_state.customers.keys())
    selected_customer = st.selectbox("Choose Customer", customer_list)
    customer_info = st.session_state.customers[selected_customer]
    st.write(f"**Phone:** {customer_info['contact']}")

st.title("🧾 ஜெனிஸ் ஏஜென்சி - Tax Invoice")

# ================= PDF FUNCTION =================
def generate_invoice_pdf():

    filename = "invoice.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []

    # ✅ Register Tamil font
    use_tamil_font = False
    if os.path.exists(FONT_FILE):
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
            use_tamil_font = True
        except:
            pass

    base_font = FONT_NAME if use_tamil_font else "Helvetica"
    bold_font = FONT_NAME if use_tamil_font else "Helvetica-Bold"

    # ================= HEADER =================
    title_style = ParagraphStyle('Title', fontName=bold_font, fontSize=16, spaceAfter=10)
    elements.append(Paragraph("Tax Invoice", title_style))

    company_style = ParagraphStyle('Company', fontName=base_font, fontSize=12)
    elements.append(Paragraph(COMPANY_NAME, company_style))

    address_style = ParagraphStyle('Address', fontName=base_font, fontSize=9)
    elements.append(Paragraph(COMPANY_ADDRESS, address_style))
    elements.append(Paragraph(f"Phone: {COMPANY_PHONE}   Email: {COMPANY_EMAIL}   State: {COMPANY_STATE}", address_style))
    elements.append(Spacer(1, 15))

    # ================= CUSTOMER =================
    bill_style = ParagraphStyle('BillTo', fontName=bold_font, fontSize=10)
    elements.append(Paragraph("Bill To:", bill_style))
    elements.append(Paragraph(selected_customer, ParagraphStyle('Cust', fontName=base_font, fontSize=10)))
    elements.append(Paragraph(f"Contact No: {customer_info['contact']}", address_style))
    elements.append(Spacer(1, 10))

    # ================= ITEMS =================
    table_data = [["#", "Item Name", "HSN", "Qty", "Price (₹)", "Amount (₹)"]]

    total_qty = 0
    total_amt = 0
    for i, item in enumerate(st.session_state.invoice_items, 1):
        total_qty += item["quantity"]
        total_amt += item["total"]
        table_data.append([
            i,
            item["item_name"],
            item["hsn_code"],
            item["quantity"],
            f"₹ {item['unit_price']:,.2f}",
            f"₹ {item['total']:,.2f}"
        ])

    table_data.append(["Total", "", "", total_qty, "", f"₹ {total_amt:,.2f}"])

    table = Table(table_data, colWidths=[25, 170, 55, 40, 75, 75])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTNAME', (0, 1), (-1, -1), base_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f2f2f2')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))

    # ================= SUMMARY =================
    summary = [
        ["Total", ":", f"₹ {total_amt:,.2f}"],
        ["In Words", ":", f"{num2words(total_amt, lang='en_IN').title()} Rupees only"]
    ]
    summary_table = Table(summary, colWidths=[100, 20, 200])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), base_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(f"For {COMPANY_NAME}", ParagraphStyle('Sign', fontName=bold_font, alignment=2)))

    doc.build(elements)

    with open(filename, "rb") as f:
        data = f.read()
    os.remove(filename)
    return data

# ================= BUTTON =================
if st.session_state.invoice_items:
    if st.button("🖨️ Generate PDF Invoice"):
        pdf = generate_invoice_pdf()
        st.download_button("📥 Download PDF", pdf, "invoice.pdf", "application/pdf")
