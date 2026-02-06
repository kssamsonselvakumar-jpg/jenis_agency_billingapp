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
from PIL import Image
import io
import base64

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

if "invoice_history" not in st.session_state:
    st.session_state.invoice_history = []

# -------- SIDEBAR --------
with st.sidebar:
    st.header("⚙️ அமைப்புகள்")
    
    # Font status
    if os.path.exists(FONT_FILE):
        st.success("✓ தமிழ்ரி சென்னை எழுத்துரு ஏற்றப்பட்டது")
    else:
        st.error(f"✗ '{FONT_FILE}' எழுத்துரு கிடைக்கவில்லை")
    
    st.divider()
    
    # Export Settings
    st.header("📤 ஏற்றுமதி அமைப்புகள்")
    default_filename = st.text_input("இயல்புநிலை கோப்புப் பெயர்", 
                                     f"INV{st.session_state.invoice_counter:04d}")
    
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

# -------- REST OF YOUR CODE (Customer, Items, Calculations remain SAME) --------
# [Keep all your existing code for customer section, item addition, calculations here]
# I'm showing only the PDF generation and download section changes

# -------- PDF GENERATION FUNCTION (UPDATED) --------
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
        tamil_title = ParagraphStyle(
            'TamilTitle', 
            fontName=FONT_NAME, 
            fontSize=24,
            alignment=1,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50'),
            leading=26
        )
        tamil_body = ParagraphStyle(
            'TamilBody', 
            fontName=FONT_NAME, 
            fontSize=13,
            leading=18,
            textColor=colors.black
        )
    else:
        tamil_title = ParagraphStyle(
            'TamilTitle',
            fontName='Helvetica-Bold',
            fontSize=24,
            alignment=1,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50')
        )
        tamil_body = styles['Normal']
    
    # Company Header
    elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", tamil_title))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("வரவுச்சீட்டு", tamil_body))
    elements.append(Spacer(1, 25))
    
    # Invoice Details
    elements.append(Paragraph(f"<b>வரவுச்சீட்டு எண்:</b> INV{invoice_no:04d}", tamil_body))
    elements.append(Paragraph(f"<b>தேதி:</b> {invoice_date.strftime('%d-%m-%Y')}", tamil_body))
    elements.append(Paragraph(f"<b>வாடிக்கையாளர்:</b> {customer}", tamil_body))
    elements.append(Paragraph(f"<b>பணம் செலுத்தும் நிலை:</b> {payment_status}", tamil_body))
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
    table_data.append(["", "", "", "", "<b>செலுத்த வேண்டிய தொகை:</b>", f"<b>{final_total:,.2f}</b>"])
    
    # Create items table
    items_table = Table(table_data, colWidths=[30, 200, 50, 50, 80, 90])
    
    # Apply table styles
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME if tamil_font_available else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        ('FONTNAME', (0, 1), (1, -6), FONT_NAME if tamil_font_available else 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -6), 11),
        ('ALIGN', (0, 1), (0, -6), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -6), 'RIGHT'),
        ('GRID', (0, 0), (-1, -6), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
        
        ('FONTNAME', (4, -5), (-1, -2), 'Helvetica'),
        ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (4, -1), (-1, -1), colors.HexColor('#e8f4fc')),
        ('LINEABOVE', (4, -5), (-1, -5), 1, colors.black),
        ('LINEABOVE', (4, -1), (-1, -1), 2, colors.HexColor('#1a5276')),
    ])
    
    items_table.setStyle(table_style)
    elements.append(items_table)
    elements.append(Spacer(1, 25))
    
    # Amount in words
    words_en = num2words(final_total, lang='en_IN')
    elements.append(Paragraph(f"<b>தொகை வார்த்தைகளில்:</b> {words_en.title()} ரூபாய் மட்டும்", tamil_body))
    
    if notes:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"<b>குறிப்புகள்:</b> {notes}", tamil_body))
    
    # Thank you message
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("வணிகத்திற்கு நன்றி!", ParagraphStyle(
        'ThankYou',
        fontName=FONT_NAME if tamil_font_available else 'Helvetica-Bold',
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#27ae60')
    )))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", ParagraphStyle(
        'Footer',
        fontName=FONT_NAME if tamil_font_available else 'Helvetica',
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )))
    
    # Build PDF
    doc.build(elements)
    
    # Read the PDF file and encode it
    with open(filename, "rb") as f:
        pdf_bytes = f.read()
    
    # Clean up the temporary file
    os.remove(filename)
    
    return pdf_bytes

# -------- NEW: CREATE HTML FOR IMAGE EXPORT --------
def create_invoice_html():
    """Create HTML representation of invoice for image export"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family: 'TamilriChennai';
                src: url('data:font/ttf;base64,{base64.b64encode(open(FONT_FILE, 'rb').read()).decode() if os.path.exists(FONT_FILE) else ''}');
            }}
            body {{
                font-family: {'TamilriChennai' if os.path.exists(FONT_FILE) else 'Arial, sans-serif'};
                width: 210mm;
                margin: 0 auto;
                padding: 20px;
                background: white;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .company-name {{
                font-size: 28px;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .invoice-title {{
                font-size: 18px;
                color: #34495e;
            }}
            .details {{
                margin-bottom: 20px;
                line-height: 1.6;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background-color: #1a5276;
                color: white;
                padding: 10px;
                text-align: center;
            }}
            td {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            .summary {{
                margin-top: 20px;
                border-top: 2px solid #1a5276;
                padding-top: 10px;
            }}
            .total {{
                background-color: #e8f4fc;
                font-weight: bold;
                padding: 10px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company-name">ஜெனிஸ் ஏஜென்சி</div>
            <div class="invoice-title">வரவுச்சீட்டு</div>
        </div>
        
        <div class="details">
            <div><strong>வரவுச்சீட்டு எண்:</strong> INV{invoice_no:04d}</div>
            <div><strong>தேதி:</strong> {invoice_date.strftime('%d-%m-%Y')}</div>
            <div><strong>வாடிக்கையாளர்:</strong> {customer}</div>
            <div><strong>பணம் செலுத்தும் நிலை:</strong> {payment_status}</div>
        </div>
        
        <table>
            <tr>
                <th>எண்</th>
                <th>பொருளின் விபரம்</th>
                <th>அலகு</th>
                <th>அளவு</th>
                <th>விலை ₹</th>
                <th>மொத்தம் ₹</th>
            </tr>
    """
    
    # Add items
    for idx, row in enumerate(st.session_state.bill, 1):
        html_content += f"""
            <tr>
                <td style="text-align: center;">{idx}</td>
                <td>{row[0]}</td>
                <td>{row[3]}</td>
                <td style="text-align: right;">{row[2]}</td>
                <td style="text-align: right;">{row[1]:,.2f}</td>
                <td style="text-align: right;">{row[4]:,.2f}</td>
            </tr>
        """
    
    # Add summary
    html_content += f"""
            <tr class="summary">
                <td colspan="5" style="text-align: right; border: none;"><strong>மொத்த தொகை:</strong></td>
                <td style="text-align: right; border: none;">{grand_total:,.2f}</td>
            </tr>
    """
    
    if discount_amount > 0:
        html_content += f"""
            <tr>
                <td colspan="5" style="text-align: right; border: none;"><strong>தள்ளுபடி:</strong></td>
                <td style="text-align: right; border: none;">-{discount_amount:,.2f}</td>
            </tr>
        """
    
    if tax_amount > 0:
        html_content += f"""
            <tr>
                <td colspan="5" style="text-align: right; border: none;"><strong>வரி ({tax_percent}%):</strong></td>
                <td style="text-align: right; border: none;">{tax_amount:,.2f}</td>
            </tr>
        """
    
    if shipping > 0:
        html_content += f"""
            <tr>
                <td colspan="5" style="text-align: right; border: none;"><strong>கப்பல் கட்டணம்:</strong></td>
                <td style="text-align: right; border: none;">{shipping:,.2f}</td>
            </tr>
        """
    
    html_content += f"""
            <tr class="total">
                <td colspan="5" style="text-align: right; border: none;"><strong>செலுத்த வேண்டிய தொகை:</strong></td>
                <td style="text-align: right; border: none;">{final_total:,.2f}</td>
            </tr>
        </table>
        
        <div class="details">
            <div><strong>தொகை வார்த்தைகளில்:</strong> {num2words(final_total, lang='en_IN').title()} ரூபாய் மட்டும்</div>
    """
    
    if notes:
        html_content += f"""
            <div><strong>குறிப்புகள்:</strong> {notes}</div>
        """
    
    html_content += """
        </div>
        
        <div class="footer">
            <div>வணிகத்திற்கு நன்றி!</div>
            <div>ஜெனிஸ் ஏஜென்சி</div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# -------- DOWNLOAD SECTION (UPDATED) --------
st.divider()
st.subheader("📤 வரவுச்சீட்டை பதிவிறக்கம் செய்க")

if st.session_state.bill:
    # Get base filename from sidebar or use default
    base_filename = st.sidebar.text_input("கோப்புப் பெயர்", f"INV{invoice_no:04d}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 PDF வடிவம்")
        st.write("அச்சிடுவதற்கு ஏற்றது")
        if st.button("PDF உருவாக்கு", key="pdf_gen"):
            pdf_bytes = create_invoice()
            st.download_button(
                label="📥 PDF பதிவிறக்கம்",
                data=pdf_bytes,
                file_name=f"{base_filename}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    with col2:
        st.markdown("### 🖼️ PNG படம்")
        st.write("மின்னஞ்சல்/WhatsApp பகிர்வு")
        if st.button("PNG உருவாக்கு", key="png_gen"):
            # Create HTML and convert to image (simplified version)
            html_content = create_invoice_html()
            
            # For now, provide HTML file that can be converted to image
            st.download_button(
                label="📥 HTML பதிவிறக்கம் (PNG-க்கு)",
                data=html_content,
                file_name=f"{base_filename}.html",
                mime="text/html",
                use_container_width=True
            )
            st.info("HTML கோப்பை உங்கள் browser-ல் திறந்து Print → Save as PNG செய்யவும்")
    
    with col3:
        st.markdown("### 📊 CSV தரவு")
        st.write("Excel-ல் பயன்படுத்த")
        if st.button("CSV உருவாக்கு", key="csv_gen"):
            # Create DataFrame
            df_invoice = pd.DataFrame(st.session_state.bill, 
                                    columns=["பொருள்", "விலை", "அளவு", "அலகு", "மொத்தம்"])
            
            # Add summary rows
            summary_data = {
                "பொருள்": ["மொத்த தொகை", "தள்ளுபடி", f"வரி ({tax_percent}%)", "கப்பல் கட்டணம்", "செலுத்த வேண்டிய தொகை"],
                "விலை": ["", "", "", "", ""],
                "அளவு": ["", "", "", "", ""],
                "அலகு": ["", "", "", "", ""],
                "மொத்தம்": [grand_total, -discount_amount, tax_amount, shipping, final_total]
            }
            df_summary = pd.DataFrame(summary_data)
            df_combined = pd.concat([df_invoice, df_summary], ignore_index=True)
            
            csv_data = df_combined.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 CSV பதிவிறக்கம்",
                data=csv_data,
                file_name=f"{base_filename}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # -------- MULTIPLE FORMATS IN ONE SECTION --------
    st.divider()
    st.subheader("🎯 அனைத்து வடிவங்களும்")
    
    # Create all formats at once
    if st.button("🔄 அனைத்து வடிவங்களையும் உருவாக்கு", type="primary"):
        with st.spinner("கோப்புகள் உருவாக்கப்படுகின்றன..."):
            # 1. Generate PDF
            pdf_bytes = create_invoice()
            
            # 2. Generate CSV
            df_invoice = pd.DataFrame(st.session_state.bill, 
                                    columns=["பொருள்", "விலை", "அளவு", "அலகு", "மொத்தம்"])
            summary_data = {
                "பொருள்": ["மொத்த தொகை", "தள்ளுபடி", f"வரி ({tax_percent}%)", "கப்பல் கட்டணம்", "செலுத்த வேண்டிய தொகை"],
                "விலை": ["", "", "", "", ""],
                "அளவு": ["", "", "", "", ""],
                "அலகு": ["", "", "", "", ""],
                "மொத்தம்": [grand_total, -discount_amount, tax_amount, shipping, final_total]
            }
            df_summary = pd.DataFrame(summary_data)
            df_combined = pd.concat([df_invoice, df_summary], ignore_index=True)
            csv_data = df_combined.to_csv(index=False, encoding='utf-8-sig')
            
            # 3. Generate HTML (for image)
            html_content = create_invoice_html()
            
            # 4. Generate TXT (simple text version)
            txt_content = f"""
ஜெனிஸ் ஏஜென்சி - வரவுச்சீட்டு
வரவுச்சீட்டு எண்: INV{invoice_no:04d}
தேதி: {invoice_date.strftime('%d-%m-%Y')}
வாடிக்கையாளர்: {customer}
பணம் செலுத்தும் நிலை: {payment_status}

பொருட்கள்:
"""
            for idx, row in enumerate(st.session_state.bill, 1):
                txt_content += f"{idx}. {row[0]} - {row[2]} {row[3]} @ ₹{row[1]:,.2f} = ₹{row[4]:,.2f}\n"
            
            txt_content += f"""
சுருக்கம்:
மொத்த தொகை: ₹{grand_total:,.2f}
தள்ளுபடி: ₹{discount_amount:,.2f}
வரி ({tax_percent}%): ₹{tax_amount:,.2f}
கப்பல் கட்டணம்: ₹{shipping:,.2f}
-------------------------
செலுத்த வேண்டிய தொகை: ₹{final_total:,.2f}

தொகை வார்த்தைகளில்: {num2words(final_total, lang='en_IN').title()} ரூபாய் மட்டும்

வணிகத்திற்கு நன்றி!
ஜெனிஸ் ஏஜென்சி
"""
            
            # Display download buttons in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    label="📥 PDF",
                    data=pdf_bytes,
                    file_name=f"{base_filename}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                st.download_button(
                    label="📥 CSV",
                    data=csv_data,
                    file_name=f"{base_filename}.csv",
                    mime="text/csv"
                )
            
            with col3:
                st.download_button(
                    label="📥 HTML",
                    data=html_content,
                    file_name=f"{base_filename}.html",
                    mime="text/html"
                )
            
            with col4:
                st.download_button(
                    label="📥 TXT",
                    data=txt_content,
                    file_name=f"{base_filename}.txt",
                    mime="text/plain"
                )
            
            st.success("✅ அனைத்து கோப்புகளும் தயார்!")

# -------- INVOICE PREVIEW --------
st.divider()
st.subheader("👁️ வரவுச்சீட்டு முன்னோட்டம்")

if st.session_state.bill:
    # Simple text preview
    st.text(f"""
ஜெனிஸ் ஏஜென்சி
வரவுச்சீட்டு எண்: INV{invoice_no:04d}
தேதி: {invoice_date.strftime('%d-%m-%Y')}
வாடிக்கையாளர்: {customer}

பொருட்கள்: {len(st.session_state.bill)}
மொத்த தொகை: ₹{final_total:,.2f}
    """)
    
    # Preview table
    df_preview = pd.DataFrame(st.session_state.bill, 
                            columns=["பொருள்", "விலை (₹)", "அளவு", "அலகு", "மொத்தம் (₹)"])
    st.dataframe(df_preview, use_container_width=True)
    
    st.info(f"**செலுத்த வேண்டிய தொகை: ₹{final_total:,.2f}**")

# -------- REST OF YOUR EXISTING CODE --------
# [Keep all your existing code for new invoice button, history, etc.]

# Add this CSS for better styling
st.markdown("""
<style>
    .stDownloadButton button {
        width: 100%;
        margin: 5px 0;
    }
    .format-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background: #f9f9f9;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)
