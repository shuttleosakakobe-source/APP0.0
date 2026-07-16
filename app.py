import streamlit as st

# ページの定義（パスをviews/配下に統一）
# ログイン画面もviews/login.pyに移動している前提です
login_page = st.Page("views/login.py", title="ログイン", icon="🔒")
staff_page = st.Page("views/staff_page.py", title="スタッフメニュー", icon="👤")
report_page = st.Page("views/report_page.py", title="情報カード報告書", icon="📝")

# ナビゲーションの実行
st.navigation([login_page, staff_page, report_page], position="hidden").run()
