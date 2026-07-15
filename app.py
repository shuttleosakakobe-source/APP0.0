# app.py
import streamlit as st
import re
from utils import load_sheet_data

# 1. ページ全体の初期設定
st.set_page_config(
    page_title="シャトル 業務アプリ (新)",
    page_icon="🚌", 
    layout="centered"
)

# メールアドレスの簡易フォーマットチェック
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# 2. セッション情報の初期化
if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_branch" not in st.session_state:
    st.session_state.user_branch = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "2"  # デフォルトは一般スタッフ

# --- 🚪 ログアウト処理 ---
def logout():
    st.session_state.login_status = False
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.user_branch = None
    st.session_state.user_role = "2"
    st.rerun()

# --- 🔐 ログイン画面の表示関数 ---
def show_login_screen():
    st.write("### 🔑 ログイン")
    
    u_email = st.text_input("メールアドレス", placeholder="example@duskin.com").strip()
    u_pass = st.text_input("パスワード", type="password").strip()
    
    if st.button("ログイン", type="primary", use_container_width=True):
        if not u_email or not u_pass:
            st.warning("メールアドレスとパスワードを入力してください。")
            return
        
        if not is_valid_email(u_email):
            st.error("正しいメールアドレスの形式で入力してください。")
            return
            
        with st.spinner("認証中..."):
            # スプレッドシートのGID=0（マスター情報）を読み込み
            raw_data = load_sheet_data(gid="0")
            
            if raw_data:
                header = [col.strip() for col in raw_data[0]]
                rows = [dict(zip(header, r)) for r in raw_data[1:]]
                
                # 入力されたメールアドレスとパスワードでユーザーを検索
                user = next(
                    (r for r in rows if str(r.get('メールアドレス')).strip().lower() == u_email.lower() 
                     and str(r.get('パスワード')).strip() == u_pass), 
                    None
                )
                
                if user:
                    # ログイン成功時のセッション保存
                    st.session_state.user_name = user.get('担当者名')
                    st.session_state.user_email = u_email
                    st.session_state.user_branch = user.get('拠点', '未設定')
                    st.session_state.user_url = user.get('URL', '')
                    st.session_state.user_role = str(user.get('権限ロール', '2')).strip()
                    st.session_state.login_status = True
                    
                    st.success("ログインに成功しました！")
                    st.rerun()
                else:
                    st.error("メールアドレスまたはパスワードが正しくありません。")
            else:
                st.error("ユーザーマスタデータの取得に失敗しました。")

# --- 3. ルーティング & ナビゲーション制御 ---
if not st.session_state.login_status:
    # ログインしていないならログイン画面を表示
    show_login_screen()
else:
    # ログイン済みの場合は、権限ロールに応じたページのみをナビゲーションに登録する
    pages = []
    role = st.session_state.user_role

    if role in ["0", "1"]:
        # 管理者(0)・チーフ(1)用ページ
        admin_page = st.Page("views/admin_page.py", title="⚙️ 管理メニュー", icon="⚙️")
        pages.append(admin_page)
    else:
        # 一般スタッフ(2)用ページ
        staff_page = st.Page("views/staff_page.py", title="👤 マイページ", icon="👤")
        pages.append(staff_page)

    # 共通のログアウト
    logout_page = st.Page(logout, title="🚪 ログアウト", icon="🚪")
    pages.append(logout_page)

    # ナビゲーションの実行
    pg = st.navigation(pages)
    pg.run()
