import streamlit as st
import io
from PIL import Image
import fitz  # PyMuPDF

# Patterns to redact from PDF
REDACTION_PATTERNS = [
    "WISE (Shanghai Wise Supply Chain Managements Co., Ltd)",
    "Att: Jack Wang",
    "419 Gongyue Road",
    "Baoshan Ditrict",
    "Shanghai, China",
    "GST # 101750818RT0001",
    "Account NO#01661-001-1062879",
    "Swift address = BOFMCAM2",
    "Bank of Montreal",
    "1299 Greene Avenue",
    "Westmount, Quebec H3Z 2A6",
    "If you have any questions concerning this invoice please call: 514-676-1113"
]

def redact_pdf(input_pdf_bytes):
    """Find and redact text using precise white boxes."""
    doc = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    
    for page in doc:
        for pattern in REDACTION_PATTERNS:
            text_instances = page.search_for(pattern)
            for rect in text_instances:
                annot = page.add_redact_annot(rect)
                annot.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))
                annot.update()
        page.apply_redactions()
    
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()

def pdf_to_image(pdf_bytes):
    """Convert PDF first page to image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img

def main():
    st.set_page_config(page_title="❤️ 罗爸爸的爱之 - 发票涂改 ❤️", layout="centered")
    st.title("❤️ 罗爸爸的爱之 - 发票涂改 ❤️")
    
    uploaded_file = st.file_uploader("上传PDF发票", type=["pdf"])
    
    if uploaded_file:
        pdf_bytes = uploaded_file.read()

        # Preview original
        st.subheader("原始发票")
        try:
            img = pdf_to_image(pdf_bytes)
            st.image(img, use_container_width=True)
        except Exception as e:
            st.warning(f"无法预览原始PDF: {e}")

        if st.button("涂改"):
            with st.spinner("正在涂改..."):
                try:
                    redacted_pdf = redact_pdf(pdf_bytes)
                    
                    st.subheader("涂改后的发票")
                    try:
                        img = pdf_to_image(redacted_pdf)
                        st.image(img, use_container_width=True)
                    except Exception:
                        st.warning("涂改后的发票无法预览，但可下载。")
                    
                    st.download_button(
                        "下载涂改后的PDF",
                        redacted_pdf,
                        "redacted_invoice.pdf",
                        "application/pdf"
                    )
                except Exception as e:
                    st.error(f"涂改失败: {e}")

if __name__ == "__main__":
    main()
