import streamlit as st
import requests
import datetime
import os
import urllib.request
import csv
import io

# サイドバーに戻るボタンを配置（スタッフメニューページへ戻る）
if st.sidebar.button("⬅️ メインメニューに戻る"):
    st.switch_page("views/staff_page.py")

# ヘッダー非表示・余白調整のスタイル設定
st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. ログインチェック
# ----------------------------------------------------
if not st.session_state.get("login_status", False):
    st.warning("ログインが必要です。ログイン画面に移動します。")
    st.switch_page("views/login.py")

st.markdown("### 📋 帳票作成センター")
user_name = st.session_state.get("user_name", "担当者")
user_branch = st.session_state.get("user_branch", "店舗")

# 検索結果保持用
if "search_data" not in st.session_state:
    st.session_state.search_data = {}

# ----------------------------------------------------
# 2. データ取得用の補助関数（スプレッドシートから読み込み）
# ----------------------------------------------------
def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        return None

def fetch_data():
    """シャトルコードでスプレッドシートを検索し、一致する行のデータを取得"""
    code = st.session_state.get("shuttle_input", "").strip()
    if code:
        sheet_id = "1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM"
        gid = "127347205"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        rows = load_sheet_data(csv_url)
        found = False
        
        if rows:
            for row in rows:
                if len(row) >= 5:
                    sheet_shuttle_code = row[1].strip()
                    if sheet_shuttle_code == code:
                        raw_branch = row[0].strip()  # A列：加盟店名
                        
                        # 全角「Ｄ－」「Ｄ-」半角「D-」「Dー」など表記揺れも含めて徹底除去
                        cleaned_branch = raw_branch.replace("Ｄ－", "").replace("Ｄ-", "").replace("D-", "").replace("Dー", "").strip()
                        
                        st.session_state.search_data = {
                            "branch": cleaned_branch,            # A列（D-除去後）
                            "customer": row[2].strip(),          # C列：お客様名
                            "dealer_code": row[4].strip()        # E列：加盟店コード
                        }
                        found = True
                        break
        
        if not found:
            st.session_state.search_data = {}
            st.warning(f"シャトルコード「{code}」に該当するデータが見つかりませんでした。")

# ----------------------------------------------------
# 3. 画面レイアウト
# ----------------------------------------------------
st.title("📝 ３店共通情報カード（報告）")
st.write(f"担当者: **{user_name}** ({user_branch})")

card_type = st.selectbox("作成するカードを選択", ["新規営業", "ケアサービス紹介"])

st.markdown("---")

# 基本情報（共通）
report_date = st.date_input("作成日", datetime.date.today())
reporter = st.text_input("作成者名", value=user_name)

st.markdown("---")

# --- A. 新規営業の場合 ---
if card_type == "新規営業":
    with st.form(key="form_singi"):
        st.subheader("💼 新規営業 カード入力")
        branch_name = st.text_input("加盟店名", value=user_branch)
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        content = st.text_area("詳細")
        image_url = st.text_input("画像URL")
        
        submit_pdf = st.form_submit_button("🖨️ 送信してPDFを作成", type="primary", use_container_width=True)

    # 送信時のデータ準備（ダミー）
    shuttle_code = ""
    dealer_code = ""
    phone = ""
    contact_person = ""
    service_type = []
    maker = ""
    has_cleaning_function = "無"
    year = ""

# --- B. ケアサービス紹介の場合 ---
else:
    st.subheader("🏥 ケアサービス紹介 カード入力")
    
    # 🔍 シャトルコード入力＆検索エリア（横並び配置）
    with st.form(key="search_form"):
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            shuttle_code = st.text_input("シャトルコード", key="shuttle_input", placeholder="コードを入力してください")
        with col_search2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # 位置あわせ用余白
            search_submitted = st.form_submit_button("🔍 検索", on_click=fetch_data, use_container_width=True)

    # 📝 詳細入力フォーム
    with st.form(key="form_care"):
        branch_name = st.text_input("加盟店名", value=st.session_state.search_data.get("branch", user_branch))
        dealer_code = st.text_input("加盟店コード", value=st.session_state.search_data.get("dealer_code", ""))
        customer_name = st.text_input("お客様名", value=st.session_state.search_data.get("customer", ""))
        
        address = st.text_input("住所")
        phone = st.text_input("電話番号")
        contact_person = st.text_input("ご担当者様")
        service_type = st.multiselect("区分", ["SM(家庭用)", "SM(業務用)", "TMX", "MM", "その他"])
        content = st.text_area("内容")
        maker = st.text_input("エアコンメーカー")
        has_cleaning_function = st.selectbox("お掃除機能", ["無", "有"])
        year = st.text_input("年式")
        
        image_url = ""
        
        submit_pdf = st.form_submit_button("🖨️ 送信してPDFを作成", type="primary", use_container_width=True)

# ----------------------------------------------------
# 4. PDF送信処理
# ----------------------------------------------------
if submit_pdf:
    if not customer_name:
        st.warning("お客様名を入力してください。")
    else:
        with st.spinner("PDFを作成中..."):
            payload = {
                "card_type": card_type,
                "report_date": str(report_date),
                "reporter": reporter,
                "branch_name": branch_name,
                "customer_name": customer_name,
                "address": address,
                "content": content
            }
            if card_type == "新規営業":
                payload.update({"image_url": image_url})
            elif card_type == "ケアサービス紹介":
                payload.update({
                    "shuttle_code": shuttle_code,
                    "dealer_code": dealer_code,
                    "phone": phone,
                    "contact_person": contact_person,
                    "service_type": ", ".join(service_type),
                    "maker": maker,
                    "has_cleaning_function": has_cleaning_function,
                    "year": year
                })
            
            try:
                gas_url = "https://script.google.com/macros/s/AKfycby9VBvs7I313uzYi3nq023TREcFvRxEVMA2yOdIMSPHPNu8jYpYCs7e64GU7jT5m26Z/exec"
                res = requests.post(gas_url, json=payload, timeout=15)
                res_data = res.json()
                
                if "pdf_url" in res_data:
                    st.success("🎉 PDF作成完了！")
                    st.markdown(f"### [🖨️ PDFを開く]({res_data['pdf_url']})")
                else:
                    st.error("PDFの生成に失敗しました。レスポンスを確認してください。")
            except Exception as e:
                st.error(f"送信中にエラーが発生しました: {e}")

st.markdown("---")

# 戻るボタン
if st.button("⬅️ メニュー画面に戻る", use_container_width=True):
    st.switch_page("views/staff_page.py")
