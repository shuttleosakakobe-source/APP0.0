import streamlit as st

# ページの定義（ファイルのパス、画面タイトル、メニュー上のアイコンなど）
login_page = st.Page("views/login.py", title="ログイン", icon="🔒")
staff_page = st.Page("views/staff_page.py", title="スタッフメニュー", icon="👤")
report_page = st.Page("views/report_page.py", title="情報カード報告書", icon="📝")

# ナビゲーションの実行
# position="hidden" にすることでサイドバーのメニュー一覧を隠し、
# ボタン（st.switch_page）による画面遷移のみでコントロールできるようにします。
st.navigation([login_page, staff_page, report_page], position="hidden").run()
