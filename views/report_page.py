import streamlit as st
import requests
import datetime

st.markdown("### 📋 営業情報カード 入力")

with st.form("new_report_form"):
    report_date = st.date_input("作成日", datetime.date.today())
    branch_name = st.text_input("加盟店名")
    customer_name = st.text_input("お客様名")
    address = st.text_input("住所")
    content = st.text_area("詳細")
    
    if st.form_submit_button("送信してPDFを作成"):
        payload = {
            "report_date": str(report_date),
            "reporter": st.session_state.get("user_name", "不明"),
            "branch_name": branch_name,
            "customer_name": customer_name,
            "address": address,
            "content": content
        }
        
        gas_url = "https://script.google.com/macros/s/AKfycbxgSp8E5AC11SJTYBkrcdfqXwyCMfeN_s7TlU6G3NePlOXo6oje9dffxLgBP_sgYfXG/exec"
        
        try:
            with st.spinner('作成中...'):
                res = requests.post(gas_url, json=payload)
                # ここでレスポンスの中身を表示してデバッグ
                if res.status_code == 200:
                    result = res.json()
                    if "error" in result:
                        st.error(f"GAS内のエラー: {result['error']}")
                    else:
                        st.success("🎉 作成完了！")
                        st.markdown(f"### [🖨️ PDFを開く]({result['pdf_url']})")
                else:
                    st.error(f"通信エラー: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"実行エラー: {str(e)}")
