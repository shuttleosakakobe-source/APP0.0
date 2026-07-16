import streamlit as st
import requests
import datetime

st.markdown("### 📋 帳票作成")

# 作成タイプを選択
report_type = st.radio("作成するカードを選択", ["新規営業情報", "ケアサービス紹介"], horizontal=True)

with st.form("report_form"):
    # 共通項目
    report_date = st.date_input("作成日", datetime.date.today())
    reporter = st.text_input("作成者")
    
    # シャトルコード入力
    shuttle_code = st.text_input("シャトルコード（入力すると加盟店・顧客名が自動入力されます）")
    
    # ケアサービス紹介の時だけ「区分」を表示
    service_type = None
    if report_type == "ケアサービス紹介":
        service_type = st.radio("区分", ["SM", "TMX", "その他"])
    
    content = st.text_area("詳細")
    
    if st.form_submit_button("送信してPDFを作成"):
        # GASへ送信するデータ
        payload = {
            "report_type": report_type,
            "report_date": str(report_date),
            "reporter": reporter,
            "shuttle_code": shuttle_code,
            "content": content,
            "service_type": service_type
        }
        
        # あなたのGASデプロイURL
        gas_url = "https://script.google.com/macros/s/AKfycbx20iER9ujWECjZ9Xkrwt-KmzzruGv7Y03ApJe4_wY73kULrynX49Q1s5_Li5aOEcod/exec"
        
        try:
            with st.spinner('PDFを作成中...'):
                res = requests.post(gas_url, json=payload)
                result = res.json()
                
                # エラーが返ってきたら表示
                if "error" in result:
                    st.error(f"作成失敗: {result['error']}")
                else:
                    st.success("🎉 PDF作成完了！")
                    st.markdown(f"### [🖨️ PDFを開く]({result['pdf_url']})")
                    
        except Exception as e:
            st.error(f"通信エラー: {str(e)}")
