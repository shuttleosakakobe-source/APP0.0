import streamlit as st
import requests
import datetime

st.markdown("### 📋 帳票作成センター")
card_type = st.selectbox("作成するカードを選択してください", ["新規営業", "ケアサービス紹介"])

with st.form("main_form"):
    report_date = st.date_input("作成日", datetime.date.today())
    reporter = st.text_input("作成者名")
    
    # フォームごとにフィールドを出し分け
    if card_type == "新規営業":
        branch_name = st.text_input("加盟店名")
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        content = st.text_area("詳細（改行可）")
        image_url = st.text_input("画像URL")
    
    elif card_type == "ケアサービス紹介":
        branch_name = st.text_input("加盟店名")
        shuttle_code = st.text_input("シャトルコード")
        dealer_code = st.text_input("加盟店コード")
        customer_name = st.text_input("お客様名")
        address = st.text_input("住所")
        phone = st.text_input("電話番号")
        contact_person = st.text_input("ご担当者様")
        service_type = st.multiselect("区分", ["SM(家庭用)", "SM(業務用)", "TMX", "MM", "その他"])
        content = st.text_area("内容")
        maker = st.text_input("エアコンメーカー")
        has_cleaning_function = st.selectbox("お掃除機能", ["有", "無"])
        year = st.text_input("年式")

    if st.form_submit_button("送信してPDFを作成"):
        # 共通payloadの作成
        payload = {
            "card_type": card_type,
            "report_date": str(report_date),
            "reporter": reporter,
            "branch_name": branch_name,
            "customer_name": customer_name,
            "address": address,
            "content": content
        }
        
        # ケアサービス専用データの追加
        if card_type == "ケアサービス紹介":
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
        elif card_type == "新規営業":
            payload.update({"image_url": image_url})

        # GASへの送信
        gas_url = "https://script.google.com/macros/s/AKfycbwA0W0H_utpATDAbZAD_QViERsvm8lNPozMzqafoopqjkRYOLw4u2c-WRSy9tGQgDWy/exec" # あなたのURL
        res = requests.post(gas_url, json=payload)
        st.success("🎉 作成完了！")
        st.markdown(f"### [🖨️ PDFを開く]({res.json()['pdf_url']})")
