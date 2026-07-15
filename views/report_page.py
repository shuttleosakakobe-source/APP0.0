import streamlit as st
import html
import urllib.request
import io
import json
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# 安全なテキスト処理
def sanitize_for_paragraph(text):
    if not text: return ""
    return html.escape(str(text)).replace("\n", " <br> ")

# PDF生成ロジック
def generate_pdf(data_row):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, 
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='HeiseiKakuGo-W5', fontSize=18, alignment=1, spaceAfter=15)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', fontSize=11, leading=16)
    
    story = []
    story.append(Paragraph(f"シャトル{data_row.get('branch', '神戸中央店')} 情報カード", title_style))
    
    info_data = [
        [
            Paragraph(f"<b>作成日:</b> {sanitize_for_paragraph(data_row.get('report_date', ''))}", normal_style),
            Paragraph(f"<b>作成者:</b> {sanitize_for_paragraph(data_row.get('reporter', ''))} 印", normal_style),
            Paragraph("<b>チーフ印:</b> ", normal_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[200, 160, 160])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke), ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 8), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"<b>【 情報の種類 】</b>", normal_style))
    story.append(Spacer(1, 5))
    type_box = Table([[Paragraph(f"<b>{sanitize_for_paragraph(data_row.get('report_type', ''))}</b>", normal_style)]], colWidths=[520])
    type_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightyellow), ('BOX', (0,0), (-1,-1), 1, colors.orange), ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(type_box)
    story.append(Spacer(1, 15))
    
    main_data = [
        ["お客様名", Paragraph(sanitize_for_paragraph(data_row.get('customer_name', '')), normal_style)],
        ["顧客コード /\nシャトルコード", Paragraph(sanitize_for_paragraph(data_row.get('customer_code', '')), normal_style)],
        ["住所・地図情報", Paragraph(sanitize_for_paragraph(data_row.get('address', '')), normal_style)],
        ["具体的な報告・\n提案内容", Paragraph(sanitize_for_paragraph(data_row.get('content', '')), normal_style)]
    ]
    t_main = Table(main_data, colWidths=[120, 400])
    t_main.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'HeiseiKakuGo-W5'), ('FONTSIZE', (0,0), (0,-1), 11),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), ('BOX', (0,0), (-1,-1), 1.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 12), ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_main)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>◇ 支店・加盟店様 返信コメント欄 ◇</b>", normal_style))
    story.append(Spacer(1, 5))
    reply_box = Table([["\n\n\n\n"], [Paragraph("<b>返信日:</b>   月   日    <b>返信者名:</b>            (印)", normal_style)]], colWidths=[520])
    reply_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black), ('LINEBELOW', (0,0), (0,0), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    story.append(reply_box)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- 画面描画 ---
if not st.session_state.get("login_status", False):
    st.switch_page("app.py")

user_name = st.session_state.user_name
user_branch = st.session_state.user_branch

st.markdown("<style>.block-container { max-width: 500px; }</style>", unsafe_allow_html=True)

# 🔙 メニューに戻るボタン
if st.button("⬅️ メニュー画面に戻る", use_container_width=True):
    st.switch_page("views/staff_page.py")

st.markdown("### 📋 ３店共通情報カード 入力フォーム")

# 送信成功後の画面切り替え表示
if st.session_state.get('last_submitted_data'):
    st.success("🎉 報告書の送信が完了しました！")
    
    pdf_buf = generate_pdf(st.session_state.last_submitted_data)
    st.download_button(
        label=f"🖨️ 送信した「{st.session_state.last_submitted_data['customer_name']}」の報告書を印刷・保存",
        data=pdf_buf,
        file_name=f"情報カード_{st.session_state.last_submitted_data['customer_name']}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
    
    if st.button("✍️ 続けて別の報告書を作成する", use_container_width=True):
        st.session_state.last_submitted_data = None
        st.rerun()
else:
    with st.form("report_card_form", clear_on_submit=True):
        st.info(f"**作成者:** {user_name}  ({user_branch})")
        report_date = st.date_input("作成日", datetime.date.today())
        report_type = st.radio("情報の種類", ["A. 業務情報", "B. 新規顧客営業情報 (返信不要)", "C. 既存顧客解約減少防止情報 (返信不要)"])
        
        customer_name = st.text_input("お客様名（店舗名など）", placeholder="例：〇〇うどん 東神戸店")
        customer_code = st.text_input("顧客コード / シャトルコード（任意）", placeholder="分かれば入力")
        address = st.text_area("住所・地図情報", placeholder="住所や目印になる情報")
        content = st.text_area("具体的な報告・提案内容", placeholder="詳しい内容をご記入ください")
        
        submitted = st.form_submit_button("📮 報告書を送信する", use_container_width=True)
        
        if submitted:
            if not customer_name:
                st.error("「お客様名」を入力してください。")
            elif not content:
                st.error("「具体的な報告・提案内容」を入力してください。")
            else:
                payload = {
                    "report_date": str(report_date), "reporter": user_name, "branch": user_branch,
                    "report_type": report_type, "customer_name": customer_name,
                    "customer_code": customer_code, "address": address, "content": content
                }
                gas_url = "https://script.google.com/macros/s/AKfycbz3QF-WcjncAsN7gusA2Rlqry6hC9avTFGBrNz1qEaKhnd3z47OLOiD2qRIqjzY0dDL/exec"
                try:
                    req = urllib.request.Request(gas_url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        if res_data.get("status") == "success":
                            st.toast("送信完了！")
                            st.session_state.last_submitted_data = payload
                            st.rerun()
                        else:
                            st.error(f"送信エラー: {res_data.get('message')}")
                except Exception as e:
                    st.error(f"接続失敗。電波の良い場所でお試しください。({e})")
