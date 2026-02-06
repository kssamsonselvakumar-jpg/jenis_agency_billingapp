import streamlit as st
import pandas as pd
import os
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from num2words import num2words
import datetime

# Set page config
st.set_page_config(
    page_title="Invoice Billing Software",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 ஜெனிஸ் ஏஜென்சி - Invoice Billing Software")

# -------- FONT SETUP --------
FONT_FILE = "Tamilri_Chenetfont_01.ttf"
FONT_NAME = "TamilriChennai"

# -------- INITIALIZE SESSION STATE --------
if "bill" not in st.session_state:
    st.session_state.bill = []

if "customers" not in st.session_state:
    st.session_state.customers = ["ஸ்ரீ குரு பகவான் அருள்"]

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1000

# -------- SIDEBAR --------
with st.sidebar:
    st.header("⚙️ அமைப்புகள்")
    
    # Font status
    if os.path.exists(FONT_FILE):
        st.success("✓ தமிழ்ரி சென்னை எழுத்துரு")
    else:
        st.warning(f"✗ '{FONT_FILE}' எழுத்துரு கிடைக்கவில்லை")
    
    st.divider()
    
    # Download settings
    st.header("📤 பதிவிறக்கம்")
    default_filename = st.text_input("கோப்புப் பெயர்", f"INV{st.session_state.invoice_counter:04d}")
    
    st.divider()
    
    # Customer Management
    st.header("👥 வாடிக்கையாளர் மேலாண்மை")
    new_customer = st.text_input("புதிய வாடிக்கையாளர்")
    if st.button("➕ வாடிக்கையாளர் சேமி"):
        if new_customer and new_customer not in st.session_state.customers:
            st.session_state.customers.append(new_customer)
            st.success("வாடிக்கையாளர் சேமிக்கப்பட்டார்!")
    
    st.divider()
    
    # All Customers
    st.subheader("அனைத்து வாடிக்கையாளர்கள்")
    for idx, cust in enumerate(st.session_state.customers, 1):
        st.write(f"{idx}. {cust}")
    
    st.divider()
    
    # App Info
    st.info(f"""
    **தகவல்:**
    - அடுத்த வரவுச்சீட்டு: INV{st.session_state.invoice_counter:04d}
    - தற்போதைய பொருட்கள்: {len(st.session_state.bill)}
    """)

# -------- CUSTOMER SECTION --------
st.subheader("👤 வாடிக்கையாளர் தகவல்")

col1, col2 = st.columns([2, 1])
with col1:
    # Customer selection
    customer = st.selectbox("வாடிக்கையாளரை தேர்ந்தெடு", st.session_state.customers)
    invoice_no = st.session_state.invoice_counter
    st.info(f"**வரவுச்சீட்டு எண்:** INV{invoice_no:04d}")

with col2:
    invoice_date = st.date_input("வரவுச்சீட்டு தேதி", datetime.date.today())
    payment_status = st.selectbox("பணம் செலுத்தும் நிலை", ["நிலுவை", "செலுத்தப்பட்டது"])

# -------- ADD ITEMS SECTION --------
st.subheader("🛒 பொருட்களை சேர்")

col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col1:
    item = st.text_input("பொருளின் பெயர்", placeholder="பொருளின் பெயரை உள்ளிடுக")
with col2:
    price = st.number_input("விலை (₹)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
with col3:
    qty = st.number_input("அளவு", min_value=1, value=1, step=1)
with col4:
    unit = st.selectbox("அலகு", ["எண்ணிக்கை", "கிலோ", "லிட்டர்", "மீட்டர்", "பெட்டி"])

if st.button("➕ பொருளை சேர்", type="primary"):
    if not item.strip():
        st.error("பொருளின் பெயரை உள்ளிடவும்")
    elif price <= 0:
        st.error("விலை 0-ஐ விட அதிகமாக இருக்க வேண்டும்")
    elif qty <= 0:
        st.error("அளவு 0-ஐ விட அதிகமாக இருக்க வேண்டும்")
    else:
        total = round(price * qty, 2)
        st.session_state.bill.append([item, price, qty, unit, total])
        st.success(f"சேர்க்கப்பட்டது: {item}")
        st.rerun()

# -------- BILL TABLE --------
if st.session_state.bill:
    st.subheader("📋 வரவுச்சீட்டு பொருட்கள்")
    
    # Create dataframe
    df = pd.DataFrame(st.session_state.bill, 
                     columns=["பொருள்", "விலை", "அளவு", "அலகு", "மொத்தம்"])
    
    # Display table
    df_display = df.copy()
    df_display.index = df_display.index + 1
    st.dataframe(df_display, use_container_width=True)
    
    # Calculate totals
    grand_total = round(df["மொத்தம்"].sum(), 2)
    
    # Item management
    st.subheader("🛠️ பொருட்களை நிர்வகி")
    col1, col2 = st.columns(2)
    
    with col1:
        if len(st.session_state.bill) > 0:
            item_to_remove = st.number_input("நீக்க வேண்டிய பொருள் எண்", 
                                           min_value=1, 
                                           max_value=len(st.session_state.bill), 
                                           value=1)
            if st.button("🗑️ பொருளை நீக்கு"):
                st.session_state.bill.pop(item_to_remove - 1)
                st.rerun()
    
    with col2:
        if st.button("🔄 அனைத்து பொருட்களையும் அழி"):
            st.session_state.bill = []
            st.rerun()
    
    # -------- CALCULATIONS --------
    st.subheader("💰 கணக்கீடுகள்")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        discount_percent = st.number_input("தள்ளுபடி (%)", min_value=0.0, max_value=100.0, value=0.0)
    with col2:
        discount_fixed = st.number_input("தள்ளுபடி (₹)", min_value=0.0, max_value=grand_total, value=0.0)
    with col3:
        tax_percent = st.number_input("வரி (%)", min_value=0.0, value=0.0)
    with col4:
        shipping = st.number_input("கப்பல் கட்டணம் (₹)", min_value=0.0, value=0.0)
    
    # Calculate final amounts
    discount_amount = round((grand_total * discount_percent / 100) + discount_fixed, 2)
    taxable_amount = round(grand_total - discount_amount, 2)
    tax_amount = round((taxable_amount * tax_percent / 100), 2)
    final_total = round(taxable_amount + tax_amount + shipping, 2)
    
    # Display summary
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 சுருக்கம்")
        st.write(f"**மொத்த தொகை:** ₹ {grand_total:,.2f}")
        if discount_amount > 0:
            st.write(f"**தள்ளுபடி:** ₹ {discount_amount:,.2f}")
        if tax_amount > 0:
            st.write(f"**வரி ({tax_percent}%):** ₹ {tax_amount:,.2f}")
        if shipping > 0:
            st.write(f"**கப்பல் கட்டணம்:** ₹ {shipping:,.2f}")
        st.markdown(f"## **இறுதி தொகை: ₹ {final_total:,.2f}**")
        
    with col2:
        # Amount in words
        words = num2words(final_total, lang='en_IN')
        st.markdown("### 🔤 தொகை வார்த்தைகளில்")
        st.info(f"**{words.title()} ரூபாய் மட்டும்**")
        
        # Additional notes
        notes = st.text_area("📝 கூடுதல் குறிப்புகள்", placeholder="சிறப்பு அறிவுறுத்தல்கள்...")

    # -------- PDF GENERATION FUNCTION --------
    def create_invoice():
        """Generate PDF invoice"""
        filename = f"INV{invoice_no:04d}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Register font
        tamil_font_available = False
        try:
            if os.path.exists(FONT_FILE):
                pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
                tamil_font_available = True
        except:
            pass
        
        # Define styles
        if tamil_font_available:
            tamil_title = ParagraphStyle(
                'TamilTitle', 
                fontName=FONT_NAME, 
                fontSize=24,
                alignment=1,
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50')
            )
            tamil_body = ParagraphStyle(
                'TamilBody', 
                fontName=FONT_NAME, 
                fontSize=13,
                leading=18
            )
        else:
            tamil_title = styles['Title']
            tamil_body = styles['Normal']
        
        # Company Header
        elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", tamil_title))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("வரவுச்சீட்டு", tamil_body))
        elements.append(Spacer(1, 25))
        
        # Invoice Details
        elements.append(Paragraph(f"வரவுச்சீட்டு எண்: INV{invoice_no:04d}", tamil_body))
        elements.append(Paragraph(f"தேதி: {invoice_date.strftime('%d-%m-%Y')}", tamil_body))
        elements.append(Paragraph(f"வாடிக்கையாளர்: {customer}", tamil_body))
        elements.append(Paragraph(f"பணம் செலுத்தும் நிலை: {payment_status}", tamil_body))
        elements.append(Spacer(1, 25))
        
        # Items Table
        table_data = [["எண்", "பொருளின் விபரம்", "அலகு", "அளவு", "விலை ₹", "மொத்தம் ₹"]]
        
        for idx, row in enumerate(st.session_state.bill, 1):
            table_data.append([
                str(idx),
                row[0],
                row[3],
                str(row[2]),
                f"{row[1]:,.2f}",
                f"{row[4]:,.2f}"
            ])
        
        # Add summary rows
        table_data.append(["", "", "", "", "", ""])
        table_data.append(["", "", "", "", "மொத்த தொகை:", f"{grand_total:,.2f}"])
        if discount_amount > 0:
            table_data.append(["", "", "", "", "தள்ளுபடி:", f"-{discount_amount:,.2f}"])
        if tax_amount > 0:
            table_data.append(["", "", "", "", f"வரி ({tax_percent}%):", f"{tax_amount:,.2f}"])
        if shipping > 0:
            table_data.append(["", "", "", "", "கப்பல் கட்டணம்:", f"{shipping:,.2f}"])
        table_data.append(["", "", "", "", "செலுத்த வேண்டிய தொகை:", f"{final_total:,.2f}"])
        
        # Create table
        items_table = Table(table_data, colWidths=[30, 200, 50, 50, 80, 90])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME if tamil_font_available else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -6), 0.5, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (4, -1), (-1, -1), 2, colors.HexColor('#1a5276')),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 25))
        
        # Amount in words
        words_en = num2words(final_total, lang='en_IN')
        elements.append(Paragraph(f"தொகை வார்த்தைகளில்: {words_en.title()} ரூபாய் மட்டும்", tamil_body))
        
        if notes:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(f"குறிப்புகள்: {notes}", tamil_body))
        
        # Thank you
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("வணிகத்திற்கு நன்றி!", tamil_body))
        elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", tamil_body))
        
        # Build PDF
        doc.build(elements)
        
        # Read and return PDF
        with open(filename, "rb") as f:
            pdf_bytes = f.read()
        
        os.remove(filename)
        return pdf_bytes

    # -------- DOWNLOAD SECTION --------
    st.divider()
    st.subheader("📤 வரவுச்சீட்டை பதிவிறக்கம் செய்க")
    
    # Get filename from sidebar
    base_filename = default_filename if default_filename else f"INV{invoice_no:04d}"
    
    # PDF Download
    if st.button("📄 PDF உருவாக்கு மற்றும் பதிவிறக்கம்"):
        with st.spinner("PDF உருவாக்கப்படுகிறது..."):
            try:
                pdf_bytes = create_invoice()
                st.download_button(
                    label="📥 PDF பதிவிறக்கம்",
                    data=pdf_bytes,
                    file_name=f"{base_filename}.pdf",
                    mime="application/pdf",
                    key="pdf_download"
                )
                st.success("PDF தயார்!")
            except Exception as e:
                st.error(f"பிழை: {str(e)}")
    
    # CSV Download
    if st.button("📊 CSV உருவாக்கு"):
        df_invoice = pd.DataFrame(st.session_state.bill, 
                                columns=["பொருள்", "விலை", "அளவு", "அலகு", "மொத்தம்"])
        
        # Add summary
        summary_df = pd.DataFrame({
            "பொருள்": ["மொத்த தொகை", "தள்ளுபடி", f"வரி ({tax_percent}%)", "கப்பல்", "செலுத்த வேண்டிய தொகை"],
            "விலை": [grand_total, -discount_amount, tax_amount, shipping, final_total],
            "அளவு": ["", "", "", "", ""],
            "அலகு": ["", "", "", "", ""],
            "மொத்தம்": ["", "", "", "", ""]
        })
        
        df_combined = pd.concat([df_invoice, summary_df], ignore_index=True)
        csv_data = df_combined.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 CSV பதிவிறக்கம்",
            data=csv_data,
            file_name=f"{base_filename}.csv",
            mime="text/csv",
            key="csv_download"
        )
    
    # -------- NEW INVOICE BUTTON --------
    st.divider()
    if st.button("🔄 புதிய வரவுச்சீட்டு தொடங்கு"):
        st.session_state.bill = []
        st.session_state.invoice_counter += 1
        st.rerun()

else:
    # Empty state
    st.info("🌟 வரவுச்சீட்டு உருவாக்க பொருட்களை சேர்க்கவும்")
    if st.button("புதிய வரவுச்சீட்டை தொடங்கு"):
        st.session_state.invoice_counter += 1
        st.rerun()

# -------- FOOTER --------
st.divider()
st.caption("ஜெனிஸ் ஏஜென்சி - தொழில்முறை பில்லிங் மென்பொருள்")
