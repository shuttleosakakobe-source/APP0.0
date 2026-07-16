import streamlit as st
import html
import urllib.request
import io
import json
import datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# PDF生成ロジック
def generate_pdf(data_row, map_image_path=None):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='HeiseiKakuGo-W5', fontSize=18, alignment=1, spaceAfter=20)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', fontSize=11, leading=16)
    
    story = []
    story.append(Paragraph("シャトル神戸中央店 新規営業情報カード", title_style))
    
    story.append(Paragraph(f"作成日: {data_row.get('report_date')}  作成者: {data_row.get('reporter')} 様", normal_style))
    story.append(Spacer(1, 10))
    
    # メインテーブル（加盟店を追加）
    data = [
        ["加盟店", data_row.get('branch_name', '')],
        ["お客様名", f"{data_row.get('customer_name', '')} 様"],
        ["住所", data_row.get('address', '')],
        ["詳細", data_row.get('content', '')],
    ]
    table = Table(data, colWidths=[80, 420])
    table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('FONTNAME', (0,0), (0,-1), 'HeiseiKakuGo-W5'),
    ]))
    story.append(table)
    
    # 地図画像
    if map_image_path:
        story.append(Spacer(1, 15))
        story.append(Paragraph("<b>地図等:</b>", normal_style))
        img = RLImage(map_image_path, width=300, height=200)
        story.append(img)
        
    # 返信欄
    story.append(Spacer(1, 25))
    story.append(Paragraph("【返信欄】", normal_style))
    reply_box = Table([["\n\n\n\n"], ["責任者印"]], colWidths=[500], rowHeights=[60, 20])
    reply_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,1), (0,1), 'MIDDLE'),
        ('ALIGN', (0,1), (0,1), 'RIGHT'), ('PADDING', (0,0), (-1,-1), 5), ('FONTNAME', (0,1), (0,1), 'HeiseiKakuGo-W5'),
    ]))
    story.append(reply_box)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- 画面描画 ---
if not st.session_state.get("login_status", False): st.switch_page("app.py")

if st.button("⬅️ メニュー画面に戻る", use_container_width=True): st.switch_page("views/staff_page.py")

st.markdown("### 📋 新規営業情報カード 入力")

if st.session_state.get('last_submitted_data'):
    st.success("🎉 送信完了！")
    pdf_buf = generate_pdf(st.session_state.last_submitted_data, map_image_path="temp_map.png" if os.path.exists("temp_map.png") else None)
    st.download_button("🖨️ 報告書を印刷・保存", data=pdf_buf, file_name="情報カード.pdf", mime="application/pdf", use_container_width=True)
    if st.button("✍️ 続けて作成する", use_container_width=True):
        st.session_state.last_submitted_data = None
        if os.path.exists("temp_map.png"): os.remove("temp_map.png")
        st.rerun()
else:
    with st.form("new_report_form", clear_on_submit=True):
        report_date = st.date_input("作成日", datetime.date.today())
        branch_name = st.text_input("加盟店名")
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        content = st.text_area("詳細")
        uploaded_file = st.file_uploader("地図等の画像をアップロード", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("📮 報告書を送信する", use_container_width=True):
            if uploaded_file: Image.open(uploaded_file).save("temp_map.png")
            
            payload = {
                "report_date": str(report_date), "reporter": st.session_state.user_name,
                "branch_name": branch_name, "customer_name": customer_name,
                "address": address, "content": content
            }
            # ※ここに正しいGASのURLを貼り付けてください
            gas_url = "https://script.google.com/macros/s/（ここにあなたのURL）/exec"
            
            try:
               req = urllib.request.Request(gas_url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=10) as response:
                    st.session_state.last_submitted_data = payload
                    st.rerun()
            except Exception as e:
                st.error(f"送信エラー: {e}")
