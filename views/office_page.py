# views/office_page.py
import streamlit as st

st.title("💼 業務担当 メニュー")
st.write(f"お疲れ様です、**{st.session_state.user_name}** さん（所属: {st.session_state.user_branch}）")
st.info("※ここはロール「3 (業務担当)」のユーザー専用画面です。")

# 今後、事務手続き用の確認画面や、全拠点データの集計機能などをここに実装していきます
