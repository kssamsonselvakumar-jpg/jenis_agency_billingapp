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

st.title("🧾 Invoice Billing Software")

# -------- INITIALIZE SESSION STATE --------
if "bill" not in st.session_state:
    st.session_state.bill = []

if "customers" not in st.session_state:
    st.session_state.customers = ["Customer 1", "Customer 2", "Customer 3"]

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1000

# -------- SIDEBAR --------
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Invoice settings
    invoice_no = st.session_state.invoice_counter
    st.info(f"**Invoice No:** INV{invoice_no:04d}")
    
    st.divider()
    
    # Customer Management
    st.header("👥 Customer Management")
    new_customer = st.text_input("Add New Customer")
    if st.button("➕ Save Customer"):
        if new_customer and new_customer not in st.session_state.customers:
            st.session_state.customers.append(new_customer)
            st.success("Customer saved!")
    
    st.divider()
    
    # All Customers
    st.subheader("All Customers")
    for idx, cust in enumerate(st.session_state.customers, 1):
        st.write(f"{idx}. {cust}")
    
    st.divider()
    
    # App Info
    st.info(f"""
    **App Info:**
    - Next Invoice: INV{st.session_state.invoice_counter:04d}
    - Current Items: {len(st.session_state.bill)}
    """)

# -------- CUSTOMER SECTION --------
st.subheader("👤 Customer Information")

col1, col2 = st.columns([2, 1])
with col1:
    customer = st.selectbox("Select Customer", st.session_state.customers)
    st.info(f"**Invoice No:** INV{invoice_no:04d}")

with col2:
    invoice_date = st.date_input("Invoice Date", datetime.date.today())
    payment_status = st.selectbox("Payment Status", ["Pending", "Paid"])

# -------- ADD ITEMS SECTION --------
st.subheader("🛒 Add Items")

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    item = st.text_input("Item Name", placeholder="Enter item name")
with col2:
    price = st.number_input("Price (₹)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
with col3:
    qty = st.number_input("Quantity", min_value=1, value=1, step=1)

if st.button("➕ Add Item", type="primary"):
    if not item.strip():
        st.error("Please enter item name")
    elif price <= 0:
        st.error("Price must be greater than 0")
    elif qty <= 0:
        st.error("Quantity must be greater than 0")
    else:
        total = round(price * qty, 2)
        st.session_state.bill.append([item, price, qty, total])
        st.success(f"Added: {item}")
        st.rerun()

# -------- BILL TABLE --------
if st.session_state.bill:
    st.subheader("📋 Invoice Items")
    
    # Create dataframe
    df = pd.DataFrame(st.session_state.bill, 
                     columns=["Item", "Price", "Quantity", "Total"])
    
    # Display table
    df_display = df.copy()
    df_display.index = df_display.index + 1
    st.dataframe(df_display, use_container_width=True)
    
    # Calculate grand total
    grand_total = round(df["Total"].sum(), 2)
    
    # Item management
    st.subheader("🛠️ Manage Items")
    col1, col2 = st.columns(2)
    
    with col1:
        if len(st.session_state.bill) > 0:
            item_to_remove = st.number_input("Item number to remove", 
                                           min_value=1, 
                                           max_value=len(st.session_state.bill), 
                                           value=1)
            if st.button("🗑️ Remove Item"):
                st.session_state.bill.pop(item_to_remove - 1)
                st.rerun()
    
    with col2:
        if st.button("🔄 Clear All Items"):
            st.session_state.bill = []
            st.rerun()
    
    # -------- CALCULATIONS --------
    st.divider()
    st.subheader("💰 Total Amount")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Final Amount")
        st.markdown(f"# **₹ {grand_total:,.2f}**")
        
    with col2:
        # Amount in words
        words = num2words(grand_total, lang='en_IN')
        st.markdown("### Amount in Words")
        st.info(f"**{words.title()} Rupees Only**")
        
        # Additional notes
        notes = st.text_area("📝 Additional Notes", placeholder="Special instructions...", height=100)

    # -------- PDF GENERATION --------
    st.divider()
    st.subheader("📄 Generate Invoice")
    
    def create_invoice():
        """Generate PDF invoice"""
        filename = f"INV{invoice_no:04d}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Try to register Tamil font if exists
        font_file = "Tamilri_Chenetfont_01.ttf"
        font_name = "TamilFont"
        
        try:
            if os.path.exists(font_file):
                pdfmetrics.registerFont(TTFont(font_name, font_file))
                use_tamil_font = True
            else:
                use_tamil_font = False
        except:
            use_tamil_font = False
        
        # Define styles
        if use_tamil_font:
            title_style = ParagraphStyle(
                'TitleStyle', 
                fontName=font_name, 
                fontSize=20, 
                alignment=1,
                spaceAfter=12
            )
            body_style = ParagraphStyle(
                'BodyStyle', 
                fontName='Helvetica', 
                fontSize=11,
                leading=14
            )
        else:
            title_style = styles['Title']
            body_style = styles['Normal']
        
        # Company Header
        if use_tamil_font:
            elements.append(Paragraph("ஜெனிஸ் ஏஜென்சி", title_style))
        else:
            elements.append(Paragraph("Jenis Agency", title_style))
        
        elements.append(Spacer(1, 20))
        
        # Invoice Details
        elements.append(Paragraph(f"Invoice No: INV{invoice_no:04d}", body_style))
        elements.append(Paragraph(f"Date: {invoice_date.strftime('%d-%m-%Y')}", body_style))
        elements.append(Paragraph(f"Customer: {customer}", body_style))
        elements.append(Paragraph(f"Payment Status: {payment_status}", body_style))
        elements.append(Spacer(1, 25))
        
        # Items Table
        table_data = [["S.No", "Item Description", "Qty", "Price (₹)", "Total (₹)"]]
        
        for idx, row in enumerate(st.session_state.bill, 1):
            table_data.append([
                str(idx),
                row[0],  # Item name
                str(row[2]),  # Quantity
                f"{row[1]:,.2f}",  # Price
                f"{row[3]:,.2f}"  # Total
            ])
        
        # Add total row
        table_data.append(["", "", "", "", ""])
        table_data.append(["", "", "", "Grand Total:", f"₹ {grand_total:,.2f}"])
        
        # Create table
        items_table = Table(table_data, colWidths=[30, 300, 50, 80, 90])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Body rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # S.No center
            ('ALIGN', (2, 1), (2, -2), 'CENTER'),  # Qty center
            ('ALIGN', (3, 1), (-1, -2), 'RIGHT'),  # Numbers right
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            
            # Total row
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (3, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('LINEABOVE', (3, -1), (-1, -1), 2, colors.black),
            ('TOPPADDING', (3, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (3, -1), (-1, -1), 10),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # Amount in words
        words_en = num2words(grand_total, lang='en_IN')
        elements.append(Paragraph(f"Amount in Words: {words_en.title()} Rupees Only", body_style))
        
        if notes:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Notes: {notes}", body_style))
        
        # Thank you message
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))
        
        # Signature
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("_________________________", ParagraphStyle(
            'Signature', alignment=2, fontSize=10)))
        elements.append(Paragraph("Authorized Signature", ParagraphStyle(
            'SignatureLabel', alignment=2, fontSize=9)))
        
        # Build PDF
        doc.build(elements)
        
        # Read and return PDF
        with open(filename, "rb") as f:
            pdf_bytes = f.read()
        
        os.remove(filename)
        return pdf_bytes

    # -------- DOWNLOAD BUTTONS --------
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Invoice", type="primary", use_container_width=True):
            with st.spinner("Creating PDF..."):
                try:
                    pdf_bytes = create_invoice()
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=f"INV{invoice_no:04d}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("PDF generated successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        # CSV Download
        if st.button("📊 Generate CSV", use_container_width=True):
            df_invoice = pd.DataFrame(st.session_state.bill, 
                                    columns=["Item", "Price", "Quantity", "Total"])
            
            # Add total row
            total_row = pd.DataFrame({
                "Item": ["GRAND TOTAL"],
                "Price": [""],
                "Quantity": [""],
                "Total": [grand_total]
            })
            
            df_combined = pd.concat([df_invoice, total_row], ignore_index=True)
            csv_data = df_combined.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"INV{invoice_no:04d}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # -------- NEW INVOICE BUTTON --------
    st.divider()
    if st.button("🔄 Start New Invoice", use_container_width=True):
        st.session_state.bill = []
        st.session_state.invoice_counter += 1
        st.rerun()

else:
    # Empty state
    st.info("🌟 Add items to create an invoice")
    if st.button("Start New Invoice", type="secondary"):
        st.session_state.invoice_counter += 1
        st.rerun()

# -------- FOOTER --------
st.divider()
st.caption("Jenis Agency - Professional Billing Software")
