import streamlit as st
import requests
import io
import os
import datetime  # ★ここを追加してください
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- PDF生成ロジック (既存PDFへの書き込み) ---
def generate_pdf(data_row, map_image_path=None):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    # フォント登録
    pdfmetrics.registerFont(TTFont('Japanese', 'ipaexg.ttf'))
    can.setFont("Japanese", 10)
    
    # 座標指定 (x, y) ※template.pdfに合わせて調整してください
    can.drawString(150, 695, str(data_row.get('report_date', '')))
    can.drawString(350, 695, str(data_row.get('reporter', '')))
    can.drawString(150, 665, str(data_row.get('branch_name', '')))
    can.drawString(150, 640, str(data_row.get('customer_name', '')))
    can.drawString(150, 615, str(data_row.get('address', '')))
    can.drawString(150, 590, str(data_row.get('content', '')))
    
    if map_image_path and os.path.exists(map_image_path):
        can.drawImage(map_image_path, 150, 400, width=150, height=100)
    
    can.save()
    packet.seek(0)
    
    # PDF合成
    template_pdf = PdfReader(open("template.pdf", "rb"))
    overlay_pdf = PdfReader(packet)
    writer = PdfWriter()
    
    page = template_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)
    
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer

# --- 画面表示 ---
if not st.session_state.get("login_status", False):
    st.switch_page("views/login.py")

if st.button("⬅️ メニュー画面に戻る"):
    st.switch_page("views/staff_page.py")

st.markdown("### 📋 新規営業情報カード 入力")

if "submitted_data" not in st.session_state:
    with st.form("new_report_form"):
        report_date = st.date_input("作成日", datetime.date.today())
        branch_name = st.text_input("加盟店名")
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        content = st.text_area("詳細")
        uploaded_file = st.file_uploader("地図画像", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("📮 送信する"):
            if uploaded_file:
                Image.open(uploaded_file).convert("RGB").save("temp_map.png")
            
            payload = {
                "report_date": str(report_date), "reporter": st.session_state.get("user_name", "不明"),
                "branch_name": branch_name, "customer_name": customer_name,
                "address": address, "content": content
            }
            
            gas_url = "https://script.google.com/macros/s/AKfycbwsWHCg5wd7L5RpsE41DCXDzhqJzULx9-7_nC59PLjd58fApK_Zva40lpFZDvzHObik/exec"
            
            try:
                res = requests.post(gas_url, json=payload, timeout=20)
                if res.status_code == 200:
                    st.session_state.submitted_data = payload
                    st.rerun()
                else:
                    st.error("送信失敗")
            except Exception as e:
                st.error(f"エラー: {e}")
else:
    st.success("🎉 送信完了！")
    pdf_buf = generate_pdf(st.session_state.submitted_data, map_image_path="temp_map.png")
    st.download_button("🖨️ 報告書を印刷", data=pdf_buf, file_name="情報カード.pdf", mime="application/pdf")
    
    if st.button("✍️ 続けて作成する"):
        del st.session_state.submitted_data
        if os.path.exists("temp_map.png"): os.remove("temp_map.png")
        st.rerun()
