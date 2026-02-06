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
# Using Tamilri_Chenetfont_01.ttf
FONT_FILE = "Tamilri_Chenetfont_01.ttf"
FONT_NAME = "TamilriChennai"

# -------- INITIALIZE SESSION STATE --------
if "bill" not in st.session_state:
    st.session_state.bill = []

if "customers" not in st.session_state:
    st.session_state.customers = ["ஸ்ரீ குரு பகவான் அருள்"]

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1000

if "invoice_history" not in st.session_state:
    st.session_state.invoice_history = []

# -------- SIDEBAR --------
with st.sidebar:
    st.header("⚙️ அமைப்புகள்")
    
    # Font status
    if os.path.exists(FONT_FILE):
        st.success("✓ தமிழ்ரி சென்னை எழுத்துரு ஏற்றப்பட்டது")
        st.text("தமிழ்ரி சென்னை எழுத்துரு")
        st.text("ஜெனிஸ் ஏஜென்சி")
        st.text("வரவுச்சீட்டு எண்")
    else:
        st.error(f"✗ '{FONT_FILE}' எழுத்துரு கிடைக்கவில்லை")
        st.info("தமிழ்ரி சென்னை எழுத்துரு அதே folder-ல் வைக்கவும்")
    
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
    - மொத்த வரவுச்சீட்டுகள்: {len(st.session_state.invoice_history)}
    - தற்போதைய பொருட்கள்: {len(st.session_state.bill)}
    """)

# -------- CUSTOMER SECTION --------
st.subheader("👤 வாடிக்கையாளர் தகவல்")

col1, col2 = st.columns([2, 1])
with col1:
    # Customer search and select
    search_term = st.text_input("🔍 வாடிக்கையாளரை தேடு", "")
    if search_term:
        filtered_customers = [c for c in st.session_state.customers 
                             if search_term.lower() in c.lower()]
        customer = st.selectbox("வாடிக்கையாளரை தேர்ந்தெடு", filtered_customers, 
                               index=0 if filtered_customers else None)
    else:
        customer = st.selectbox("வாடிக்கையாளரை தேர்ந்தெடு", st.session_state.customers)
        
    # Invoice number
    invoice_no = st.session_state.invoice_counter
    st.info(f"**வரவுச்சீட்டு எண்:** INV{invoice_no:04d}")

with col2:
    invoice_date = st.date_input("வரவுச்சீட்டு தேதி", datetime.date.today())
    payment_status = st.selectbox("பணம் செலுத்தும் நிலை", 
                                 ["நிலுவை", "செலுத்தப்பட்டது", "பகுதி செலுத்தம்"])

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
    unit = st.selectbox("அலகு", ["எண்ணிக்கை", "கிலோ", "லிட்டர்", "மீட்டர்", "பெட்டி", "துண்டு"])

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
        discount_percent = st.number_input("தள்ளுபடி (%)", 
                                         min_value=0.0, 
                                         max_value=100.0, 
                                         value=0.0, 
                                         step=0.5)
    with col2:
        discount_fixed = st.number_input("தள்ளுபடி (₹)", 
                                       min_value=0.0, 
                                       max_value=grand_total, 
                                       value=0.0, 
                                       step=10.0)
    with col3:
        tax_percent = st.number_input("வரி (%)", 
                                    min_value=0.0, 
                                    value=0.0, 
                                    step=0.5)
    with col4:
        shipping = st.number_input("கப்பல் கட்டணம் (₹)", 
                                 min_value=0.0, 
                                 value=0.0, 
                                 step=10.0)
    
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
        notes = st.text_area("📝 கூடுதல் குறிப்புகள்", 
                           placeholder="சிறப்பு அறிவுறுத்தல்கள்...",
                           height=100)
    
    # -------- PDF GENERATION --------
    st.divider()
    st.subheader("📄 வரவுச்சீட்டு உருவாக்கு")
    
    def create_invoice():
        """Generate PDF invoice with Tamilri Chennai font"""
        filename = f"INV{invoice_no:04d}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Register Tamilri Chennai font
        tamil_font_available = False
        try:
            if os.path.exists(FONT_FILE):
                pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
                tamil_font_available = True
        except Exception as e:
            st.warning(f"எழுத்துரு பிழை: {str(e)}. இயல்புநிலை எழுத்துரு பயன்படுத்தப்படுகிறது.")
        
        # Define styles with Tamilri Chennai font
        if tamil_font_available:
            # Title style - Larger for Tamilri Chennai
            tamil_title = ParagraphStyle(
                'TamilTitle', 
                fontName=FONT_NAME, 
                fontSize=24,  # Slightly larger for this font
                alignment=1,  # Center
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50'),
                leading=26
            )
            
            # Subtitle style
            tamil_subtitle = ParagraphStyle(
                'TamilSubtitle',
                fontName=FONT_NAME,
                fontSize=14,
                alignment=1,
                spaceAfter=20,
                textColor=colors.HexColor('#34495e'),
                leading=18
            )
            
            # Body style
            tamil_body = ParagraphStyle(
                'TamilBody', 
                fontName=FONT_NAME, 
                fontSize=13,  # Adjusted for this font
                leading=18,
                textColor=colors.black
            )
            
            # Small text style
            tamil_small = ParagraphStyle(
                'TamilSmall',
                fontName=FONT_NAME,
                fontSize=11,
                leading=15,
                textColor=colors.darkgrey
            )
            
            # Table header style
            tamil_table_header = ParagraphStyle(
                'TamilTableHeader',
                fontName=FONT_NAME,
                fontSize=12,
                textColor=colors.white,
                alignment=1,
                leading=16
            )
        else:
            # Fallback styles
            tamil_title = ParagraphStyle(
                'TamilTitle',
                fontName='Helvetica-Bold',
                fontSize=24,
                alignment=1,
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50')
            )
            tamil_subtitle = styles['Heading2']
            tamil_body = styles['Normal']
            tamil_small = styles['Normal']
            tamil_table_header = styles['Normal']
        
        # Company Header (Center aligned with Tamilri Chennai)
        elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", tamil_title))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("வரவுச்சீட்டு", tamil_subtitle))
        elements.append(Spacer(1, 25))
        
        # Invoice Details in a clean layout
        elements.append(Paragraph(f"<b>வரவுச்சீட்டு எண்:</b> INV{invoice_no:04d}", tamil_body))
        elements.append(Paragraph(f"<b>தேதி:</b> {invoice_date.strftime('%d-%m-%Y')}", tamil_body))
        elements.append(Paragraph(f"<b>வாடிக்கையாளர்:</b> {customer}", tamil_body))
        elements.append(Paragraph(f"<b>பணம் செலுத்தும் நிலை:</b> {payment_status}", tamil_body))
        elements.append(Spacer(1, 25))
        
        # Horizontal line
        elements.append(Spacer(1, 1))
        elements.append(Table([[""]], colWidths=[500], style=[
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(Spacer(1, 25))
        
        # Items Table Header
        table_data = [
            ["எண்", "பொருளின் விபரம்", "அலகு", "அளவு", "விலை ₹", "மொத்தம் ₹"]
        ]
        
        # Add items
        for idx, row in enumerate(st.session_state.bill, 1):
            table_data.append([
                str(idx),
                row[0],  # Item name
                row[3],  # Unit
                str(row[2]),  # Quantity
                f"{row[1]:,.2f}",  # Price
                f"{row[4]:,.2f}"  # Total
            ])
        
        # Add empty row before summary
        table_data.append(["", "", "", "", "", ""])
        
        # Add summary rows
        table_data.append(["", "", "", "", "மொத்த தொகை:", f"{grand_total:,.2f}"])
        if discount_amount > 0:
            table_data.append(["", "", "", "", "தள்ளுபடி:", f"-{discount_amount:,.2f}"])
        if tax_amount > 0:
            table_data.append(["", "", "", "", f"வரி ({tax_percent}%):", f"{tax_amount:,.2f}"])
        if shipping > 0:
            table_data.append(["", "", "", "", "கப்பல் கட்டணம்:", f"{shipping:,.2f}"])
        table_data.append(["", "", "", "", "<b>செலுத்த வேண்டிய தொகை:</b>", f"<b>{final_total:,.2f}</b>"])
        
        # Create items table
        items_table = Table(table_data, colWidths=[30, 200, 50, 50, 80, 90])
        
        # Apply table styles optimized for Tamilri Chennai
        table_style = TableStyle([
            # Header row - Dark blue background
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME if tamil_font_available else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Item rows - Tamilri Chennai for Tamil text
            ('FONTNAME', (0, 1), (1, -6), FONT_NAME if tamil_font_available else 'Helvetica'),
            ('FONTNAME', (2, 1), (2, -6), FONT_NAME if tamil_font_available else 'Helvetica'),
            ('FONTNAME', (3, 1), (-1, -6), 'Helvetica'),  # Numbers in English font
            ('FONTSIZE', (0, 1), (-1, -6), 11),
            ('ALIGN', (0, 1), (0, -6), 'CENTER'),  # Serial number
            ('ALIGN', (3, 1), (-1, -6), 'RIGHT'),  # Numbers right aligned
            ('ALIGN', (1, 1), (1, -6), 'LEFT'),    # Item names left aligned
            ('VALIGN', (0, 1), (-1, -6), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -6), 0.5, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -6), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Summary rows
            ('FONTNAME', (4, -5), (-1, -2), 'Helvetica'),
            ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (4, -1), (-1, -1), colors.HexColor('#e8f4fc')),
            ('LINEABOVE', (4, -5), (-1, -5), 1, colors.black),
            ('LINEABOVE', (4, -1), (-1, -1), 2, colors.HexColor('#1a5276')),
            ('TOPPADDING', (4, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (4, -1), (-1, -1), 10),
        ])
        
        items_table.setStyle(table_style)
        elements.append(items_table)
        elements.append(Spacer(1, 25))
        
        # Amount in words
        words_en = num2words(final_total, lang='en_IN')
        elements.append(Paragraph(f"<b>தொகை வார்த்தைகளில்:</b> {words_en.title()} ரூபாய் மட்டும்", 
                                tamil_body))
        
        # Notes if any
        if notes:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(f"<b>குறிப்புகள்:</b> {notes}", tamil_small))
        
        # Terms and conditions
        elements.append(Spacer(1, 30))
        terms = Paragraph(
            "<b>விதிமுறைகள்:</b> 1. பணம் 15 நாட்களுக்குள் செலுத்தப்பட வேண்டும். 2. தாமதப்படுத்தினால் மாதத்திற்கு 1.5% தாமத கட்டணம்.",
            tamil_small
        )
        elements.append(terms)
        
        # Thank you message and signature
        elements.append(Spacer(1, 40))
        
        # Signature area
        signature_table = Table([
            ["", "அங்கீகரிக்கப்பட்ட கையொப்பம்"],
            ["", "________________________"]
        ], colWidths=[300, 200])
        
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME if tamil_font_available else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", ParagraphStyle(
            'CompanyFooter',
            fontName=FONT_NAME if tamil_font_available else 'Helvetica-Bold',
            fontSize=12,
            alignment=1,
            textColor=colors.HexColor('#1a5276')
        )))
        
        # Font used information
        elements.append(Spacer(1, 15))
        if tamil_font_available:
            elements.append(Paragraph("தமிழ்ரி சென்னை எழுத்துரு", ParagraphStyle(
                'FontInfo',
                fontName=FONT_NAME,
                fontSize=8,
                alignment=1,
                textColor=colors.grey
            )))
        
        # Build PDF
        doc.build(elements)
        return filename
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 புதிய வரவுச்சீட்டு", use_container_width=True):
            st.session_state.bill = []
            st.session_state.invoice_counter += 1
            st.rerun()
    
    with col2:
        if st.button("💾 PDF உருவாக்கு", type="primary", use_container_width=True):
            pdf = create_invoice()
            with open(pdf, "rb") as f:
                st.download_button(
                    label="📥 வரவுச்சீட்டை பதிவிறக்கு",
                    data=f,
                    file_name=f"INV{invoice_no:04d}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Save to history
            invoice_data = {
                "வரவுச்சீட்டு எண்": f"INV{invoice_no:04d}",
                "தேதி": invoice_date.strftime("%d-%m-%Y"),
                "வாடிக்கையாளர்": customer,
                "பொருட்கள்": len(st.session_state.bill),
                "தொகை": final_total,
                "நிலை": payment_status
            }
            st.session_state.invoice_history.append(invoice_data)
            
            # Clear current bill and increment counter
            st.session_state.bill = []
            st.session_state.invoice_counter += 1
            st.success(f"வரவுச்சீட்டு INV{invoice_no:04d} உருவாக்கப்பட்டது!")
            st.rerun()
    
    with col3:
        if st.session_state.invoice_history:
            with st.expander("📜 வரவுச்சீட்டு வரலாறு"):
                hist_df = pd.DataFrame(st.session_state.invoice_history[-10:])
                st.dataframe(hist_df, use_container_width=True)
                if st.button("வரலாற்றை அழி"):
                    st.session_state.invoice_history = []
                    st.rerun()

else:
    # Empty state
    st.info("🌟 வரவுச்சீட்டு உருவாக்க பொருட்களை சேர்க்கவும்")
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("புதிய வரவுச்சீட்டை தொடங்கு", type="secondary"):
            st.session_state.invoice_counter += 1
            st.rerun()

# -------- FOOTER --------
st.divider()
st.caption("ஜெனிஸ் ஏஜென்சி - தொழில்முறை பில்லிங் மென்பொருள் | எழுத்துரு: தமிழ்ரி சென்னை")