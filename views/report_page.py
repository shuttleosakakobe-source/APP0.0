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

# ... (sanitize_for_paragraph関数はそのまま)

def generate_pdf(data_row, map_image_path=None):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', fontSize=11, leading=16)
    
    story = []
    # タイトル・作成情報など (既存の内容)
    # ...
    
    # 既存のテーブル要素の後ろに地図を追加
    if map_image_path:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>地図等:</b>", normal_style))
        img = RLImage(map_image_path, width=300, height=200)
        story.append(img)
    
    # ... (返信欄など)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- フォーム部分の修正 ---
# st.form内に以下を追加
uploaded_file = st.file_uploader("地図等の画像をアップロード", type=['png', 'jpg', 'jpeg'])

# 送信処理内での画像処理
img_path = None
if uploaded_file:
    img_path = "temp_map.png"
    Image.open(uploaded_file).save(img_path)

# PDF生成呼び出し
pdf_buf = generate_pdf(payload, map_image_path=img_path)
