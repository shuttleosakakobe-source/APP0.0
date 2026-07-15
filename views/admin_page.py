# views/admin_page.py
import streamlit as st

st.title("🛠️ 管理者・チーフ 業務メニュー")
st.write(f"ようこそ、**{st.session_state.user_name}** さん（所属: {st.session_state.user_branch}）")
st.info("※ここはロール「0 (管理者)」または「1 (チーフ)」のユーザーだけがアクセスできる画面です。")

# 今後、管理用の打刻確認やデータ編集などをここに書いていきます
