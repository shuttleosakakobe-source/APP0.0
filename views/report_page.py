import streamlit as st
import requests
import datetime

# 検索結果を保持するセッション状態の初期化
if "search_result" not in st.session_state:
    st.session_state.search_result = {"branch": "", "customer": "", "dealer_code": ""}

# GASからデータを取得する関数
def fetch_data():
    code = st.session_state.shuttle_input
    if code:
        # 自分のGASのURL
        gas_url = "https://script.google.com/macros/s/AKfycbyQDKM41vyLCq_glmqlcqzSElFq0QjD07aOn3oyXCDNy5Jpjtr-SNDQ1Lyuo2RcuYbW/exec"
        try:
            # doGetを呼び出し（paramsでcodeを送る）
            res = requests.get(gas_url, params={"code": code})
            data = res.json()
            if "error" not in data:
                st.session_state.search_result = data
            else:
                st.warning("該当するシャトルコードが見つかりませんでした")
                st.session_state.search_result = {"branch": "なし", "customer": "なし", "dealer_code": "なし"}
        except Exception as e:
            st.error(f"検索エラー: {e}")

st.markdown("### 📋 帳票作成")

# フォームタイプ選択
report_type = st.radio("作成するカードを選択", ["新規営業情報", "ケアサービス紹介"], horizontal=True)

# シャトルコード入力（入力変更時に fetch_data が走る）
st.text_input("シャトルコード", key="shuttle_input", on_change=fetch_data)

# 検索結果のリアルタイム表示
col1, col2, col3 = st.columns(3)
col1.metric("加盟店名", st.session_state.search_result["branch"])
col2.metric("お客様名", st.session_state.search_result["customer"])
col3.metric("加盟店コード", st.session_state.search_result["dealer_code"])

with st.form("report_form"):
    report_date = st.date_input("作成日", datetime.date.today())
    reporter = st.text_input("作成者")
    
    if report_type == "ケアサービス紹介":
        service_type = st.radio("区分", ["SM", "TMX", "その他"])
    else:
        service_type = None
    
    content = st.text_area("詳細")
    
    if st.form_submit_button("送信してPDFを作成"):
        payload = {
            "report_type": report_type,
            "report_date": str(report_date),
            "reporter": reporter,
            "shuttle_code": st.session_state.shuttle_input,
            "content": content,
            "service_type": service_type
        }
        
        # GASのURL（doPostへ送信）
        gas_url = "https://script.google.com/macros/s/AKfycbyQDKM41vyLCq_glmqlcqzSElFq0QjD07aOn3oyXCDNy5Jpjtr-SNDQ1Lyuo2RcuYbW/exec"
        
        with st.spinner('作成中...'):
            try:
                res = requests.post(gas_url, json=payload)
                result = res.json()
                if "error" in result:
                    st.error(f"作成失敗: {result['error']}")
                else:
                    st.success("🎉 PDF作成完了！")
                    st.markdown(f"### [🖨️ PDFを開く]({result['pdf_url']})")
            except Exception as e:
                st.error(f"送信エラー: {str(e)}")
