# views/admin_page.py
import streamlit as st

st.title("⚙️ 最高管理者 メニュー")
st.write(f"ようこそ、**{st.session_state.user_name}** さん（所属: {st.session_state.user_branch}）")
st.info("※ここはロール「0 (管理者)」の最高権限ユーザー専用画面です。")

# マスタデータの編集や、アプリ全体のシステム設定などをここに実装していきます
