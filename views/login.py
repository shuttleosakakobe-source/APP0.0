import streamlit as st
import os
import urllib.request
import csv
import io

def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        return None

st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

if os.path.exists("1.png"): 
    st.image("1.png", use_container_width=True)
    
st.write("### 🔑 ログイン")
u_email = st.text_input("メールアドレス").strip()
u_pass = st.text_input("パスワード", type="password").strip()

if st.button("ログイン", type="primary", use_container_width=True):
    master_url = "https://docs.google.com/spreadsheets/d/1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM/export?format=csv&gid=0"
    raw = load_sheet_data(master_url)
    if raw:
        h_cols = [col.strip() for col in raw[0]]
        matched_row = None
        for row in raw[1:]:
            if len(row) < 6: continue
            row_dict = dict(zip(h_cols, row))
            if str(row_dict.get('メールアドレス')).strip() == u_email and str(row_dict.get('パスワード')).strip() == u_pass:
                matched_row = row
                break
        
        if matched_row:
            user_dict = dict(zip(h_cols, matched_row))
            st.session_state.user_name = user_dict.get('担当者名', '')
            st.session_state.user_branch = user_dict.get('拠点', '神戸中央店')
            st.session_state.user_role = str(matched_row[5]).strip()
            st.session_state.login_status = True
            st.switch_page("views/staff_page.py")
        else:
            st.error("メールアドレスまたはパスワードが違います。")
