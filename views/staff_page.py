# views/staff_page.py
import streamlit as st

st.title("👤 スタッフ マイページ")
st.write(f"お疲れ様です、**{st.session_state.user_name}** さん（所属: {st.session_state.user_branch}）")
st.info("※ここはロール「2 (一般スタッフ)」のユーザー向けの画面です。")

# 今後、日々の活動報告や個人スケジュール、勤怠打刻などをここに書いていきます
