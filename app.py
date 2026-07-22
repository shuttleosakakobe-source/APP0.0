import streamlit as st

st.set_page_config(page_title="業務管理アプリ", layout="wide")

# 各ページの定義
login_page = st.Page("views/login_page.py", title="ログイン", icon="🔑", default=True)
staff_page = st.Page("views/staff_page.py", title="スタッフメニュー", icon="🏠")
report_page = st.Page("views/report_page.py", title="帳票作成センター", icon="📋")

# ナビゲーションの実行 (position="hidden" でサイドバーの標準メニューを隠す)
pg = st.navigation([login_page, staff_page, report_page], position="hidden")
pg.run()
