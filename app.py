import streamlit as st
import os
import urllib.request
import csv
import io
import json

# --- ページ設定 ---
st.set_page_config(
    page_title="ダスキンシャトル 業務アプリ",
    page_icon="icon.png", 
    layout="centered"
)

# 共通データ読み込み関数
def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return None

# セッションの初期化
if 'login_status' not in st.session_state: st.session_state.login_status = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_role' not in st.session_state: st.session_state.user_role = ""
if 'user_branch' not in st.session_state: st.session_state.user_branch = ""
if 'user_code' not in st.session_state: st.session_state.user_code = ""
if 'user_email' not in st.session_state: st.session_state.user_email = ""

# --- ログイン状態に応じたルーティング ---
if st.session_state.login_status:
    # ログイン成功時は、views内のスタッフ画面を呼び出す
    if st.session_state.user_role == "2":
        # 一般スタッフ画面へ遷移
        st.switch_page("views/staff.py")
    else:
        st.warning("一般スタッフ（ロール2）以外の画面は現在準備中です。")
        if st.button("ログアウト"):
            st.session_state.login_status = False
            st.rerun()
else:
    # 🔑 未ログイン時のログイン画面表示
    st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)
    
    if os.path.exists("1.png"): 
        st.image("1.png", use_container_width=True)
        
    st.write("### 🔑 ログイン")
    # ✉️ 担当者コードから「メールアドレス」に変更
    u_email = st.text_input("メールアドレス", key="login_email").strip()
    u_pass = st.text_input("パスワード", type="password", key="login_pass").strip()
    
    if st.button("ログイン", type="primary", use_container_width=True):
        master_url = "https://docs.google.com/spreadsheets/d/1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM/export?format=csv&gid=0"
        raw = load_sheet_data(master_url)
        if raw:
            h_cols = [col.strip() for col in raw[0]]
            rows = [dict(zip(h_cols, r)) for r in raw[1:]]
            
            # ✉️ 「メールアドレス」と「パスワード」でユーザーを検索
            user = next((
                r for r in rows 
                if str(r.get('メールアドレス')).strip() == u_email 
                and str(r.get('パスワード')).strip() == u_pass
            ), None)
            
            if user:
                vals = list(user.values())
                st.session_state.user_name = user.get('担当者名')
                st.session_state.user_branch = user.get('拠点', '神戸中央店')  # 拠点情報を取得（なければデフォルト神戸）
                st.session_state.user_role = str(vals[6]).strip() if len(vals) >= 7 else "2"
                st.session_state.user_code = user.get('担当者コード', '')  # ログイン後に必要ならコードも取得
                st.session_state.user_email = u_email
                st.session_state.login_status = True
                
                st.success(f"ログイン成功: {st.session_state.user_name} さん")
                st.rerun()
            else:
                st.error("メールアドレスまたはパスワードが違います。")
        else:
            st.error("マスターデータの読み込みに失敗しました。")
