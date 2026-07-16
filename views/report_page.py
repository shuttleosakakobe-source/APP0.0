import streamlit as st
import requests
import io
import json
import datetime
import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# PDF生成関数
# PDF生成関数の該当部分を以下に差し替えてください
def generate_pdf(data_row, map_image_path=None):
    # 日本語フォントの読み込みをより確実にします
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    
    buffer = io.BytesIO()
    # マージンやサイズを標準化
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # 完全に日本語が通るようにスタイルを定義
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontName='HeiseiKakuGo-W5', 
        fontSize=18, alignment=1, spaceAfter=20
    )
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', 
        fontSize=12, leading=18
    )
    
    story = []
    story.append(Paragraph("シャトル神戸中央店 新規営業情報カード", title_style))
    story.append(Paragraph(f"作成日: {data_row.get('report_date')} 作成者: {data_row.get('reporter')} 様", normal_style))
    story.append(Spacer(1, 20))
    
    # 表データ
    data = [
        ["加盟店", data_row.get('branch_name', '')],
        ["お客様名", f"{data_row.get('customer_name', '')} 様"],
        ["住所", data_row.get('address', '')],
        ["詳細", data_row.get('content', '')],
    ]
    
    # 表の列幅とスタイルを詳細に設定
    table = Table(data, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'HeiseiKakuGo-W5'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(table)
    
    if map_image_path and os.path.exists(map_image_path):
        story.append(Spacer(1, 20))
        story.append(Paragraph("地図・資料:", normal_style))
        story.append(RLImage(map_image_path, width=300, height=200))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

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
            
            # 正しいURLに更新済み
            gas_url = "https://script.google.com/macros/s/AKfycbwsWHCg5wd7L5RpsE41DCXDzhqJzULx9-7_nC59PLjd58fApK_Zva40lpFZDvzHObik/exec"
            
            try:
                res = requests.post(gas_url, json=payload, timeout=20)
                if res.status_code == 200:
                    st.session_state.submitted_data = payload
                    st.rerun() 
                else:
                    st.error(f"送信失敗: サーバーからの応答コード {res.status_code}")
            except Exception as e:
                st.error(f"通信エラー: {str(e)}")
else:
    st.success("🎉 送信完了！")
    pdf_buf = generate_pdf(st.session_state.submitted_data, map_image_path="temp_map.png")
    st.download_button("🖨️ 報告書を印刷・保存", data=pdf_buf, file_name="情報カード.pdf", mime="application/pdf")
    
    if st.button("✍️ 続けて作成する"):
        del st.session_state.submitted_data
        if os.path.exists("temp_map.png"): os.remove("temp_map.png")
        st.rerun()
