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
    u_email = st.text_input("メールアドレス", key="login_email").strip()
    u_pass = st.text_input("パスワード", type="password", key="login_pass").strip()
    
    if st.button("ログイン", type="primary", use_container_width=True):
        master_url = "https://docs.google.com/spreadsheets/d/1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM/export?format=csv&gid=0"
        raw = load_sheet_data(master_url)
        if raw:
            h_cols = [col.strip() for col in raw[0]]
            
            # メールアドレスとパスワードが合致する行を探す
            # ※ヘッダー名に依存せず位置で確実に判定するため、生の行(list)でループします
            matched_row = None
            for row in raw[1:]:
                # 行の長さが足りているかチェック
                if len(row) < 6:
                    continue
                
                # スプレッドシート側の列構成に合わせて確認：
                # (例: メールアドレス列、パスワード列のインデックスと照合)
                # ここでは dict に変換して、キーから確実に取得します
                row_dict = dict(zip(h_cols, row))
                
                if str(row_dict.get('メールアドレス')).strip() == u_email and str(row_dict.get('パスワード')).strip() == u_pass:
                    matched_row = row
                    break
            
            if matched_row:
                # 一致した行を辞書化
                user_dict = dict(zip(h_cols, matched_row))
                
                # 各自の情報をセッションに保存
                st.session_state.user_name = user_dict.get('担当者名', '')
                st.session_state.user_branch = user_dict.get('拠点', '神戸中央店')
                st.session_state.user_code = user_dict.get('担当者コード', '')
                st.session_state.user_email = u_email
                
                # ⭐ 権限は F列 (インデックス5 / A=0, B=1, C=2, D=3, E=4, F=5)
                if len(matched_row) >= 6:
                    st.session_state.user_role = str(matched_row[5]).strip() # F列を直接指定
                else:
                    st.session_state.user_role = "2" # 取得できなければデフォルト一般スタッフ
                
                st.session_state.login_status = True
                st.success(f"ログイン成功: {st.session_state.user_name} さん")
                st.rerun()
            else:
                st.error("メールアドレスまたはパスワードが違います。")
        else:
            st.error("マスターデータの読み込みに失敗しました。")
