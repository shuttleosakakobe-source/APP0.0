import streamlit as st
import requests
import datetime

# サイドバーに戻るボタンを配置（スタッフメニューページへ戻る）
if st.sidebar.button("⬅️ メインメニューに戻る"):
    st.switch_page("views/staff_page.py")

st.markdown("### 📋 帳票作成センター")

# 検索結果保持用
if "search_data" not in st.session_state:
    st.session_state.search_data = {}

def fetch_data():
    code = st.session_state.shuttle_input
    if code:
        gas_url = "https://script.google.com/macros/s/AKfycby9VBvs7I313uzYi3nq023TREcFvRxEVMA2yOdIMSPHPNu8jYpYCs7e64GU7jT5m26Z/exec"
        res = requests.get(gas_url, params={"code": code})
        st.session_state.search_data = res.json()

card_type = st.selectbox("作成するカードを選択", ["新規営業", "ケアサービス紹介"])

# ログインユーザー名（※Session State等から取得する場合は書き換えてください）
reporter_name = st.session_state.get("user_name", "山田太郎")

with st.form("main_form"):
    report_date = st.date_input("作成日", datetime.date.today())
    reporter = st.text_input("作成者名", value=reporter_name)

    if card_type == "新規営業":
        branch_name = st.text_input("加盟店名")
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        content = st.text_area("詳細")
        image_url = st.text_input("画像URL")

    elif card_type == "ケアサービス紹介":
        col1, col2 = st.columns([3, 1])
        with col1:
            shuttle_code = st.text_input("シャトルコード", key="shuttle_input")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("検索", on_click=fetch_data)
        
        branch_name = st.text_input("加盟店名", value=st.session_state.search_data.get("branch", ""))
        dealer_code = st.text_input("加盟店コード", value=st.session_state.search_data.get("dealer_code", ""))
        customer_name = st.text_input("お客様名", value=st.session_state.search_data.get("customer", ""))
        address = st.text_input("住所")
        phone = st.text_input("電話番号")
        contact_person = st.text_input("ご担当者様")
        service_type = st.multiselect("区分", ["SM(家庭用)", "SM(業務用)", "TMX", "MM", "その他"])
        content = st.text_area("内容")
        maker = st.text_input("エアコンメーカー")
        has_cleaning_function = st.selectbox("お掃除機能", ["有", "無"])
        year = st.text_input("年式")

    if st.form_submit_button("送信してPDFを作成"):
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
        
        gas_url = "https://script.google.com/macros/s/AKfycby9VBvs7I313uzYi3nq023TREcFvRxEVMA2yOdIMSPHPNu8jYpYCs7e64GU7jT5m26Z/exec"
        res = requests.post(gas_url, json=payload)
        st.success("🎉 PDF作成完了！")
        st.markdown(f"### [🖨️ PDFを開く]({res.json()['pdf_url']})")
