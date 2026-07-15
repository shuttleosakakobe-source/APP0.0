# views/chief_page.py
import streamlit as st

st.title("🎖️ チーフ 業務メニュー")
st.write(f"お疲れ様です、**{st.session_state.user_name}** さん（所属: {st.session_state.user_branch}）")
st.info("※ここはロール「1 (チーフ)」のユーザー専用画面です。")

# 今後、チーフ向けの担当スタッフの確認や、日報確認などをここに実装していきます
