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
import json

# Set page config
st.set_page_config(
    page_title="Jenis Agency - Tax Invoice",
    page_icon="🧾",
    layout="wide"
)

# ========== CONFIGURATION ==========
COMPANY_NAME = "ஜெனிஸ் ஏஜென்சி"
COMPANY_ADDRESS = "பாலக்காடு ரோடு வாழையார்"
COMPANY_PHONE = "9003223305"
COMPANY_EMAIL = "ramakrishnankarivilai@gmail.com"
COMPANY_STATE = "32-Kerala"
WEBSITE = "www.vyaparapp.in"

# ========== FONT SETUP ==========
FONT_FILE = "Tamilri_Chenetfont_01.ttf"
FONT_NAME = "TamilFont"

# ========== INITIALIZE SESSION STATE ==========
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1

if "customers" not in st.session_state:
    st.session_state.customers = {
        "ஸ்ரீ குரு பகவான் அருள்": {
            "contact": "9894536686",
            "address": ""
        }
    }

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("⚙️ Invoice Settings")
    
    # Invoice number
    invoice_no = st.session_state.invoice_counter
    st.info(f"**Invoice No:** {invoice_no}")
    
    st.divider()
    
    # Customer Management
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
    
    # Select Customer
    st.subheader("Select Customer")
    customer_list = list(st.session_state.customers.keys())
    selected_customer = st.selectbox("Choose Customer", customer_list)
    
    # Display customer info
    if selected_customer:
        customer_info = st.session_state.customers[selected_customer]
        st.write(f"**Phone:** {customer_info['contact']}")
    
    st.divider()
    
    # HSN/SAC Settings
    st.subheader("HSN/SAC Code")
    default_hsn = st.text_input("Default HSN/SAC", "174350")
    
    st.divider()
    
    st.info(f"""
    **Invoice Info:**
    - Invoice No: {invoice_no}
    - Date: {datetime.date.today().strftime('%d-%m-%Y')}
    - Items: {len(st.session_state.invoice_items)}
    """)

# ========== MAIN INTERFACE ==========
st.title("🧾 ஜெனிஸ் ஏஜென்சி - Tax Invoice")

# ========== ADD ITEMS SECTION ==========
st.subheader("🛒 Add Invoice Items")

col1, col2, col3, col4 = st.columns(4)
with col1:
    item_name = st.text_input("Item Name", placeholder="Enter item description")
with col2:
    hsn_code = st.text_input("HSN/SAC Code", value=default_hsn)
with col3:
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
with col4:
    unit_price = st.number_input("Price/Unit (₹)", min_value=0.0, value=0.0, step=1.0, format="%.2f")

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("➕ Add Item", type="primary", use_container_width=True):
        if not item_name.strip():
            st.error("Please enter item name")
        elif unit_price <= 0:
            st.error("Price must be greater than 0")
        else:
            total_amount = round(quantity * unit_price, 2)
            st.session_state.invoice_items.append({
                "item_name": item_name,
                "hsn_code": hsn_code,
                "quantity": quantity,
                "unit_price": unit_price,
                "total": total_amount
            })
            st.success(f"Added: {item_name}")
            st.rerun()

# ========== INVOICE ITEMS TABLE ==========
if st.session_state.invoice_items:
    st.subheader("📋 Invoice Items")
    
    # Create display table
    display_data = []
    for idx, item in enumerate(st.session_state.invoice_items, 1):
        display_data.append([
            idx,
            item["item_name"],
            item["hsn_code"],
            item["quantity"],
            f"₹ {item['unit_price']:,.2f}",
            f"₹ {item['total']:,.2f}"
        ])
    
    # Calculate totals
    total_quantity = sum(item["quantity"] for item in st.session_state.invoice_items)
    total_amount = sum(item["total"] for item in st.session_state.invoice_items)
    received_amount = total_amount  # Default full payment
    balance_amount = 0.0
    
    # Display table
    df = pd.DataFrame(display_data, columns=["#", "Item Name", "HSN/SAC", "Quantity", "Price/Unit (₹)", "Amount(₹)"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # ========== SUMMARY SECTION ==========
    st.subheader("💰 Invoice Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Total Quantity:** {total_quantity}")
        st.write(f"**Sub Total:** ₹ {total_amount:,.2f}")
        st.write(f"**Total:** ₹ {total_amount:,.2f}")
        
        # Received amount input
        received_input = st.number_input("Received Amount (₹)", 
                                        min_value=0.0, 
                                        max_value=total_amount,
                                        value=total_amount,
                                        step=100.0)
        
        if received_input != total_amount:
            balance_amount = total_amount - received_input
            st.warning(f"**Balance:** ₹ {balance_amount:,.2f}")
        else:
            st.success("**Balance:** ₹ 0.00")
    
    with col2:
        # Amount in words
        words = num2words(total_amount, lang='en_IN')
        st.info(f"**Amount in Words:**\n{words.title()} Rupees only")
        
        # Payment method
        payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "UPI", "Cheque"])
        
        # Notes
        notes = st.text_area("Additional Notes", height=80)

# ========== PDF GENERATION FUNCTION ==========
def generate_invoice_pdf():
    """Generate PDF invoice exactly like the sample"""
    filename = f"INV_{invoice_no}_{datetime.date.today().strftime('%d-%m-%Y')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=30, bottomMargin=30)
    
    elements = []
    
    # Register font
    try:
        if os.path.exists(FONT_FILE):
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
            use_tamil_font = True
        else:
            use_tamil_font = False
    except:
        use_tamil_font = False
    
    # ========== COMPANY HEADER ==========
    # Title: Tax Invoice
    title_style = ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=0,  # Left align
        textColor=colors.black,
        spaceAfter=10
    )
    elements.append(Paragraph("Tax Invoice", title_style))
    
    # Company name in Tamil
    if use_tamil_font:
        company_style = ParagraphStyle(
            'Company',
            fontName=FONT_NAME,
            fontSize=12,
            alignment=0,
            textColor=colors.black
        )
        elements.append(Paragraph(COMPANY_NAME, company_style))
    else:
        elements.append(Paragraph(COMPANY_NAME, ParagraphStyle('Company', fontSize=12)))
    
    # Company address
    address_style = ParagraphStyle(
        'Address',
        fontName='Helvetica',
        fontSize=9,
        alignment=0,
        textColor=colors.black,
        spaceAfter=3
    )
    elements.append(Paragraph(COMPANY_ADDRESS, address_style))
    
    # Contact info in one line
    contact_text = f"Phone: {COMPANY_PHONE} &nbsp;&nbsp;&nbsp; Email: {COMPANY_EMAIL} &nbsp;&nbsp;&nbsp; State: {COMPANY_STATE}"
    elements.append(Paragraph(contact_text, address_style))
    
    elements.append(Spacer(1, 15))
    
    # ========== CUSTOMER SECTION ==========
    # Bill To header
    bill_to_style = ParagraphStyle(
        'BillTo',
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=0,
        textColor=colors.black,
        spaceAfter=5
    )
    elements.append(Paragraph("Bill To:", bill_to_style))
    
    # Customer name
    if use_tamil_font and selected_customer:
        customer_style = ParagraphStyle(
            'Customer',
            fontName=FONT_NAME,
            fontSize=10,
            alignment=0,
            textColor=colors.black
        )
        elements.append(Paragraph(selected_customer, customer_style))
    else:
        elements.append(Paragraph(selected_customer, ParagraphStyle('Customer', fontSize=10)))
    
    # Customer contact
    customer_info = st.session_state.customers.get(selected_customer, {})
    contact_no = customer_info.get('contact', '')
    if contact_no:
        elements.append(Paragraph(f"Contact No: {contact_no}", address_style))
    
    elements.append(Spacer(1, 10))
    
    # ========== INVOICE DETAILS ==========
    # Create table for invoice details
    inv_details_data = [
        ["Invoice Details:", "", "", "", ""],
        ["No:", str(invoice_no), "", "Date:", datetime.date.today().strftime('%d-%m-%Y')]
    ]
    
    inv_details_table = Table(inv_details_data, colWidths=[60, 80, 20, 40, 80])
    inv_details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(inv_details_table)
    elements.append(Spacer(1, 15))
    
    # ========== ITEMS TABLE ==========
    # Table header
    table_data = [
        ["#", "Item Name", "HSN/ SAC", "Quantity", "Price/ Unit (₹)", "Amount(₹)"]
    ]
    
    # Add items
    for idx, item in enumerate(st.session_state.invoice_items, 1):
        table_data.append([
            str(idx),
            item["item_name"],
            item["hsn_code"],
            str(item["quantity"]),
            f"₹ {item['unit_price']:,.2f}",
            f"₹ {item['total']:,.2f}"
        ])
    
    # Add empty row and totals
    table_data.append(["", "", "", "", "", ""])
    table_data.append(["Total", "", "", str(total_quantity), "", f"₹ {total_amount:,.2f}"])
    
    # Calculate column widths based on A4 page
    col_widths = [20, 180, 60, 50, 80, 80]
    
    items_table = Table(table_data, colWidths=col_widths)
    
    # Table styling
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        
        # Body rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # S.No
        ('ALIGN', (3, 1), (3, -2), 'CENTER'),  # Quantity
        ('ALIGN', (4, 1), (-1, -2), 'RIGHT'),  # Prices
        ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
        ('GRID', (0, 1), (-1, -2), 1, colors.black),
        ('PADDING', (0, 1), (-1, -2), 4),
        
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 9),
        ('ALIGN', (3, -1), (3, -1), 'CENTER'),
        ('ALIGN', (5, -1), (5, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f2f2f2')),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 10))
    
    # ========== SUMMARY SECTION ==========
    # Create summary table
    summary_data = [
        ["Sub Total", ":", f"₹ {total_amount:,.2f}"],
        ["Total", ":", f"₹ {total_amount:,.2f}"],
        ["", "", ""],
        ["Invoice Amount In Words :", "", f"{num2words(total_amount, lang='en_IN').title()} Rupees only"],
        ["Received", ":", f"₹ {received_input:,.2f}"],
        ["Balance", ":", f"₹ {balance_amount:,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 10, 120])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 2), 'Helvetica'),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 15))
    
    # ========== TERMS AND CONDITIONS ==========
    terms_style = ParagraphStyle(
        'Terms',
        fontName='Helvetica',
        fontSize=9,
        alignment=0,
        textColor=colors.black,
        spaceAfter=5
    )
    elements.append(Paragraph("Terms And Conditions:", terms_style))
    elements.append(Paragraph("Thank you for doing business with us.", terms_style))
    
    # Website
    website_style = ParagraphStyle(
        'Website',
        fontName='Helvetica',
        fontSize=8,
        alignment=0,
        textColor=colors.blue,
        spaceAfter=20
    )
    elements.append(Paragraph(WEBSITE, website_style))
    
    # ========== SIGNATURE SECTION ==========
    elements.append(Spacer(1, 50))
    
    # For [Company Name]: line
    if use_tamil_font:
        for_style = ParagraphStyle(
            'For',
            fontName=FONT_NAME,
            fontSize=9,
            alignment=2,  # Right align
            textColor=colors.black
        )
        elements.append(Paragraph(f"For {COMPANY_NAME}:", for_style))
    else:
        elements.append(Paragraph(f"For {COMPANY_NAME}:", ParagraphStyle('For', fontSize=9, alignment=2)))
    
    # Authorized Signatory
    elements.append(Paragraph("Authorized Signatory", ParagraphStyle(
        'Signature',
        fontName='Helvetica',
        fontSize=9,
        alignment=2,
        textColor=colors.black,
        spaceBefore=30
    )))
    
    # ========== GENERATE PDF ==========
    doc.build(elements)
    
    # Read and return PDF bytes
    with open(filename, "rb") as f:
        pdf_bytes = f.read()
    
    # Clean up
    os.remove(filename)
    
    return pdf_bytes

# ========== ACTION BUTTONS ==========
if st.session_state.invoice_items:
    st.divider()
    st.subheader("📄 Generate Invoice")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🖨️ Generate PDF Invoice", type="primary", use_container_width=True):
            with st.spinner("Creating PDF invoice..."):
                try:
                    pdf_bytes = generate_invoice_pdf()
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=f"Tax_Invoice_{invoice_no}_{datetime.date.today().strftime('%d-%m-%Y')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("Invoice generated successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        # Save and New Invoice
        if st.button("💾 Save & New Invoice", use_container_width=True):
            st.session_state.invoice_items = []
            st.session_state.invoice_counter += 1
            st.rerun()
    
    with col3:
        # Clear current invoice
        if st.button("🗑️ Clear Invoice", use_container_width=True):
            st.session_state.invoice_items = []
            st.rerun()

else:
    # Empty state
    st.info("🌟 Add items to create a tax invoice")
    if st.button("Start New Invoice"):
        st.rerun()

# ========== STYLING ==========
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .stDataFrame {
        font-size: 14px;
    }
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMetric"]) {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)
