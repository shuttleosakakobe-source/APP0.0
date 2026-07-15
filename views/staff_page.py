import streamlit as st
import os
import base64
import html
import urllib.request
import csv
import io
import json
import datetime
# PDF生成用のライブラリをインポート
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# 共通データ読み込み関数
def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        return None

# --- 神戸中央店用の各種データ取得関数 ---
@st.cache_data(ttl=60)
def get_kobe_campaign_info():
    sheet_id = "1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM"
    gid = "121045239"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    rows = load_sheet_data(url)
    campaign_name = "キャンペーン入力"
    form_url = "#"
    
    if rows:
        if len(rows) >= 2 and len(rows[1]) >= 5:
            val_e2 = rows[1][4].strip()
            if val_e2:
                campaign_name = val_e2

        for row in rows:
            if len(row) >= 2 and row[0].strip() == "神戸中央店":
                form_url = row[1].strip()
                break
                
    return campaign_name, form_url

@st.cache_data(ttl=60)
def get_kobe_user_maintenance_url(user_name):
    sheet_id = "1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM"
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    rows = load_sheet_data(url)
    if rows and len(rows) >= 2:
        header = [col.strip() for col in rows[0]]
        try:
            name_idx = header.index("担当者名")
        except ValueError:
            name_idx = 1
            
        for row in rows[1:]:
            if len(row) > name_idx:
                sheet_name_val = row[name_idx].strip()
                if user_name in sheet_name_val or sheet_name_val in user_name:
                    if len(row) >= 5:
                        return row[4].strip()
    return "#"

# 画像をBase64変換
def _get_base64_img(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_img_html(file_name, emoji, width="100%"):
    data = _get_base64_img(file_name)
    if data:
        img_code = f'data:image/png;base64,{data}'
        return f'<img src="{img_code}" style="width:{width}; aspect-ratio:1/1; object-fit:contain; border-radius:15px; display: block; margin: 0 auto;">'
    return f'<div style="width:{width}; aspect-ratio:1/1; background:#f0f2f6; border-radius:15px; display:flex; align-items:center; justify-content:center; font-size:40px; margin: 0 auto;">{emoji}</div>'

# HTML特殊文字のエスケープおよび安全な改行変換関数
def sanitize_for_paragraph(text):
    if not text:
        return ""
    escaped = html.escape(str(text))
    # パパーサーエラー防止のため <br> の前後に確実にスペースを確保
    return escaped.replace("\n", " <br> ")

# 💡 PDF自動生成ロジック (A4サイズ・日本語フォント対応)
def generate_pdf(data_row):
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, 
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='HeiseiKakuGo-W5', fontSize=18, alignment=1, spaceAfter=15
    )
    normal_style = ParagraphStyle(
        'NormalStyle', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', fontSize=11, leading=16
    )
    
    story = []
    
    # 1. タイトル
    story.append(Paragraph(f"シャトル{data_row.get('branch', '神戸中央店')} 情報カード", title_style))
    
    # 2. 基本情報テーブル
    info_data = [
        [
            Paragraph(f"<b>作成日:</b> {sanitize_for_paragraph(data_row.get('report_date', ''))}", normal_style),
            Paragraph(f"<b>作成者:</b> {sanitize_for_paragraph(data_row.get('reporter', ''))} 印", normal_style),
            Paragraph("<b>チーフ印:</b> ", normal_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[200, 160, 160])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))
    
    # 3. 情報の種類
    story.append(Paragraph(f"<b>【 情報の種類 】</b>", normal_style))
    story.append(Spacer(1, 5))
    type_box = Table([[Paragraph(f"<b>{sanitize_for_paragraph(data_row.get('report_type', ''))}</b>", normal_style)]], colWidths=[520])
    type_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightyellow),
        ('BOX', (0,0), (-1,-1), 1, colors.orange),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(type_box)
    story.append(Spacer(1, 15))
    
    # 4. メイン内容 (💡 エラー回避のため、左側ラベル列はParagraphを使わないプレーンなテキストに変更)
    main_data = [
        ["お客様名", Paragraph(sanitize_for_paragraph(data_row.get('customer_name', '')), normal_style)],
        ["顧客コード /\nシャトルコード", Paragraph(sanitize_for_paragraph(data_row.get('customer_code', '')), normal_style)],
        ["住所・地図情報", Paragraph(sanitize_for_paragraph(data_row.get('address', '')), normal_style)],
        ["具体的な報告・\n提案内容", Paragraph(sanitize_for_paragraph(data_row.get('content', '')), normal_style)]
    ]
    t_main = Table(main_data, colWidths=[120, 400])
    t_main.setStyle(TableStyle([
        # 左側ラベル列のフォント設定と太字指定
        ('FONTNAME', (0,0), (0,-1), 'HeiseiKakuGo-W5'),
        ('FONTSIZE', (0,0), (0,-1), 11),
        ('TEXTCOLOR', (0,0), (0,-1), colors.black),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_main)
    story.append(Spacer(1, 20))
    
    # 5. 返信コメント欄
    story.append(Paragraph("<b>◇ 支店・加盟店様 返信コメント欄 ◇</b>", normal_style))
    story.append(Spacer(1, 5))
    
    # 空行の枠を確保 (ここもプレーンテキストで安全を確保)
    reply_box = Table([
        ["\n\n\n\n"],
        [Paragraph("<b>返信日:</b>   月   日    <b>返信者名:</b>            (印)", normal_style)]
    ], colWidths=[520])
    reply_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('LINEBELOW', (0,0), (0,0), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM')
    ]))
    story.append(reply_box)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- 画面表示処理 ---
if not st.session_state.get("login_status", False):
    st.warning("ログインしてください。")
    st.switch_page("app.py")
else:
    user_name = st.session_state.user_name
    user_branch = st.session_state.user_branch

    # セッション状態の初期化
    if 'show_report_form' not in st.session_state:
        st.session_state.show_report_form = False
    if 'last_submitted_data' not in st.session_state:
        st.session_state.last_submitted_data = None

    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem !important; max-width: 500px; }
        .button-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 15px 0; }
        .btn-item { text-align: center; text-decoration: none; display: block; color: black !important; }
        .btn-text { font-size: 12px; font-weight: bold; line-height: 1.2; text-align: center; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.write(f"👤 **{user_name} さん** ({user_branch})")
    
    if os.path.exists("1.png"): 
        st.image("1.png", use_container_width=True)

    # 🏢 拠点分岐 (神戸中央店)
    if user_branch == "神戸中央店":
        st.write("### 🏢 メニュー（神戸中央店）")

        maint_input_url = "https://docs.google.com/forms/d/e/1FAIpQLSc4E3L_UJkVxMMSTOYgcw3SJyoBixHoJfhe0WC-x1wbK6lsHw/viewform"
        maint_confirm_url = get_kobe_user_maintenance_url(user_name)
        campaign_name, campaign_url = get_kobe_campaign_info()

        b1 = get_img_html("3.png", "📄")
        b2 = get_img_html("4.png", "📋")
        b4 = get_img_html("5.png", "🧽")

        grid_html = f'''
            <div class="button-grid">
                <a class="btn-item" href="{maint_input_url}" target="_blank">
                    {b1}<p class="btn-text" style="margin-top:6px;">メンテナンス<br>入力</p>
                </a>
                <a class="btn-item" href="{maint_confirm_url}" target="_blank">
                    {b2}<p class="btn-text" style="margin-top:6px;">メンテナンス<br>確認</p>
                </a>
                <a class="btn-item" href="{campaign_url}" target="_blank">
                    {b4}<p class="btn-text" style="margin-top:6px;">{campaign_name}</p>
                </a>
            </div>
        '''
        st.markdown(grid_html, unsafe_allow_html=True)

        # ✍️ 「情報カード報告書」の表示切り替えボタン
        st.write("---")
        
        btn_type = "primary"
        if st.session_state.show_report_form:
            btn_type = "secondary"

        if st.button("📝 ３店共通情報カード（報告）を作成する", use_container_width=True, type=btn_type):
            st.session_state.show_report_form = not st.session_state.show_report_form
            # フォームを開くときは直前の印刷ボタンを隠す
            if st.session_state.show_report_form:
                st.session_state.last_submitted_data = None
            st.rerun()

        # 💡 送信直後の印刷用ダウンロードボタンの表示位置
        if st.session_state.last_submitted_data and not st.session_state.show_report_form:
            st.info("🎉 報告書の送信が完了しています。必要に応じて以下から印刷・保存してください。")
            pdf_buf = generate_pdf(st.session_state.last_submitted_data)
            st.download_button(
                label=f"🖨️ 送信した「{st.session_state.last_submitted_data['customer_name']}」の報告書を印刷する",
                data=pdf_buf,
                file_name=f"情報カード_{st.session_state.last_submitted_data['customer_name']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.write("---")

        # --- 📝 情報カード入力フォーム ---
        if st.session_state.show_report_form:
            st.markdown("### 📋 ３店共通情報カード（プラスα）入力")
            
            with st.form("report_card_form", clear_on_submit=True):
                st.info(f"**作成者:** {user_name}  /  **拠点:** {user_branch}")
                report_date = st.date_input("作成日", datetime.date.today())
                
                report_type = st.radio(
                    "情報の種類",
                    [
                        "A. 業務情報",
                        "B. 新規顧客営業情報 (返信不要)",
                        "C. 既存顧客解約減少防止情報 (返信不要)"
                    ]
                )
                
                customer_name = st.text_input("お客様名（店舗名など）", placeholder="例：〇〇うどん 東神戸店")
                customer_code = st.text_input("顧客コード / シャトルコード（任意）", placeholder="分かれば入力してください")
                address = st.text_area("住所・地図情報", placeholder="新店の場所や住所、目印になる情報をご記入ください")
                content = st.text_area("具体的な報告・提案内容", placeholder="例：新店が〇月〇日にオープン予定です。一度営業してみてはいかがでしょうか。")
                
                submitted = st.form_submit_button("📮 報告書を送信する", use_container_width=True)
                
                if submitted:
                    if not customer_name:
                        st.error("「お客様名」は必須入力項目です。")
                    elif not content:
                        st.error("「具体的な報告・提案内容」は必須入力項目です。")
                    else:
                        payload = {
                            "report_date": str(report_date),
                            "reporter": user_name,
                            "branch": user_branch,
                            "report_type": report_type,
                            "customer_name": customer_name,
                            "customer_code": customer_code,
                            "address": address,
                            "content": content
                        }
                        
                        gas_url = "https://script.google.com/macros/s/AKfycbz3QF-WcjncAsN7gusA2Rlqry6hC9avTFGBrNz1qEaKhnd3z47OLOiD2qRIqjzY0dDL/exec"
                        
                        try:
                            headers = {"Content-Type": "application/json"}
                            req = urllib.request.Request(
                                gas_url, 
                                data=json.dumps(payload).encode("utf-8"), 
                                headers=headers, 
                                method="POST"
                            )
                            with urllib.request.urlopen(req, timeout=10) as response:
                                res_data = json.loads(response.read().decode("utf-8"))
                                if res_data.get("status") == "success":
                                    st.toast("スプレッドシートへの記録が完了しました！")
                                    # データをセッションに保存して印刷ボタンを出すトリガーにする
                                    st.session_state.last_submitted_data = payload
                                    st.session_state.show_report_form = False
                                    st.rerun()
                                else:
                                    st.error(f"送信エラーが発生しました: {res_data.get('message')}")
                        except Exception as e:
                            st.error(f"接続に失敗しました。時間をおいて再度お試しください。({e})")
    else:
        st.info(f"{user_branch}用の画面は現在準備中です。")

    # ログアウトボタン
    st.write("---")
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.login_status = False
        st.switch_page("app.py")
