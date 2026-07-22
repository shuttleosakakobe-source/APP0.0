import streamlit as st
import os
import urllib.request
import csv
import io

# ヘッダー非表示・余白調整のスタイル設定
st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. ログインチェック
# ----------------------------------------------------
if not st.session_state.get("login_status", False):
    st.warning("ログインが必要です。ログイン画面に移動します。")
    st.switch_page("views/login.py")

user_name = st.session_state.get("user_name", "担当者")
user_branch = st.session_state.get("user_branch", "店舗")

# ----------------------------------------------------
# 2. データ取得用の補助関数
# ----------------------------------------------------
def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        return None

def fetch_data():
    """検索ボタン押下時に実行されるコールバック関数"""
    st.session_state["search_executed"] = True

# ----------------------------------------------------
# 3. 画面レイアウト・フォーム構成
# ----------------------------------------------------
st.title("📝 ３店共通情報カード（報告）")
st.write(f"担当者: **{user_name}** ({user_branch})")

st.markdown("---")

# 💡 st.form 内でフォーム送信用ボタン（st.form_submit_button）を使用することでエラーを防止
with st.form(key="report_search_form"):
    st.subheader("🔍 検索・情報入力フォーム")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("顧客名・対象者名", placeholder="例: 山田 太郎").strip()
    with col2:
        card_category = st.selectbox(
            "カード種別",
            ["ケアサービス紹介", "メンテナンス", "クレーム・ご意見", "その他"]
        )
    
    details = st.text_area("詳細内容・報告事項", placeholder="具体的な内容を入力してください...", height=120)
    
    # ⭕ エラー箇所を修正：st.button ではなく st.form_submit_button を使用
    submitted = st.form_submit_button(
        label="検索 / データの読み込み",
        on_click=fetch_data,
        type="primary",
        use_container_width=True
    )

# ----------------------------------------------------
# 4. フォーム送信後の処理
# ----------------------------------------------------
if submitted:
    if not customer_name:
        st.warning("顧客名を入力してください。")
    else:
        with st.spinner("データを処理中..."):
            # 送信成功時のデータ保存
            st.session_state.last_submitted_data = {
                "customer_name": customer_name,
                "category": card_category,
                "details": details,
                "user_name": user_name,
                "user_branch": user_branch
            }
            st.success("情報を正常に送信・取得しました！")

# 検索結果や過去履歴の表示エリア
if st.session_state.get("last_submitted_data"):
    st.markdown("---")
    st.subheader("📋 入力中の報告カード内容")
    data = st.session_state.last_submitted_data
    
    st.info(f"""
    - **担当店舗/氏名:** {data['user_branch']} / {data['user_name']}
    - **顧客名:** {data['customer_name']}
    - **種別:** {data['category']}
    - **詳細内容:** {data['details']}
    """)

st.markdown("---")

# 戻るボタン
if st.button("⬅️ メニュー画面に戻る", use_container_width=True):
    st.switch_page("views/staff_page.py")
