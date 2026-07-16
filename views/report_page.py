import streamlit as st
import html
import requests  # urllibから変更
import io
import json
import datetime
import os
from PIL import Image
# ... (他のインポートはそのまま)

# --- 修正後の送信部分 ---
        if st.form_submit_button("📮 報告書を送信する", use_container_width=True):
            if uploaded_file:
                Image.open(uploaded_file).convert("RGB").save("temp_map.png")
            
            payload = {
                "report_date": str(report_date), 
                "reporter": st.session_state.user_name,
                "branch_name": branch_name, 
                "customer_name": customer_name,
                "address": address, 
                "content": content
            }
            
            gas_url = "https://script.google.com/macros/s/（ここにあなたのURL）/exec"
            
            try:
                # requestsを使えば文字コードの問題は自動で解決されます
                response = requests.post(gas_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    st.session_state.last_submitted_data = payload
                    st.rerun()
                else:
                    st.error(f"送信失敗: ステータスコード {response.status_code}")
            except Exception as e:
                st.error(f"送信エラー: {e}")
