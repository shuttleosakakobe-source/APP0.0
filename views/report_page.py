import streamlit as st
import requests
import datetime

# ページ設定
st.markdown("### 📋 新規営業情報カード 入力")

with st.form("new_report_form"):
    report_date = st.date_input("作成日", datetime.date.today())
    branch_name = st.text_input("加盟店名")
    customer_name = st.text_input("お客様名")
    address = st.text_input("住所")
    content = st.text_area("詳細")
    
    if st.form_submit_button("送信してPDFを作成"):
        # スプレッドシートに送信するデータ
        payload = {
            "report_date": str(report_date),
            "reporter": st.session_state.get("user_name", "不明"),
            "branch_name": branch_name,
            "customer_name": customer_name,
            "address": address,
            "content": content
        }
        
        # ご提示いただいたGASのURLへ送信
        gas_url = "https://script.google.com/macros/s/AKfycby9VBvs7I313uzYi3nq023TREcFvRxEVMA2yOdIMSPHPNu8jYpYCs7e64GU7jT5m26Z/exec"
        
        try:
            with st.spinner('PDFを作成中...'):
                res = requests.post(gas_url, json=payload, timeout=30)
                result = res.json()
                
                st.success("🎉 PDF作成完了！")
                st.markdown(f"### [🖨️ 作成されたPDFを開く]({result['pdf_url']})")
        except Exception as e:
            st.error(f"作成失敗: {e}")
