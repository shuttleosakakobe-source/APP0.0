import streamlit as st

st.set_page_config(page_title="業務管理アプリ", layout="wide")

# 画像のツリー構造に基づいた正確なファイルパス
login_page = st.Page("views/login.py", title="ログイン", icon="🔑", default=True)
staff_page = st.Page("views/staff_page.py", title="スタッフメニュー", icon="🏠")
report_page = st.Page("views/report_page.py", title="帳票作成センター", icon="📋")

# ナビゲーションの実行
pg = st.navigation([login_page, staff_page, report_page], position="hidden")
pg.run()
