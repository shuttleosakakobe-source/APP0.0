import streamlit as st
import os
import base64
import html
import urllib.request
import csv
import io

st.markdown("<style>header {visibility: hidden; height: 0px !important;}</style>", unsafe_allow_html=True)

# 共通データ読み込み関数
def load_sheet_data(custom_url):
    try:
        response = urllib.request.urlopen(custom_url, timeout=10)
        content = response.read().decode('utf-8')
        f = io.StringIO(content)
        reader = csv.reader(f)
        return list(reader)
    except Exception as e:
        return None

# --- 神戸中央店用の各種データ取得関数 ---
@st.cache_data(ttl=60)
def get_kobe_campaign_info():
    sheet_id = "1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM"
    gid = "121045239"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    rows = load_sheet_data(url)
    campaign_name = "キャンペーン入力"
    form_url = "#"
    
    if rows:
        if len(rows) >= 2 and len(rows[1]) >= 5:
            val_e2 = rows[1][4].strip()
            if val_e2:
                campaign_name = val_e2

        for row in rows:
            if len(row) >= 2 and row[0].strip() == "神戸中央店":
                form_url = row[1].strip()
                break
                
    return campaign_name, form_url

@st.cache_data(ttl=60)
def get_kobe_user_maintenance_url(user_name):
    sheet_id = "1-1zvVWOfHsXFWdUoAZwOUnxo1BgSdKMG6GubpRTVqeM"
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    rows = load_sheet_data(url)
    if rows and len(rows) >= 2:
        header = [col.strip() for col in rows[0]]
        try:
            name_idx = header.index("担当者名")
        except ValueError:
            name_idx = 1
            
        for row in rows[1:]:
            if len(row) > name_idx:
                sheet_name_val = row[name_idx].strip()
                
                # 💡 あいまい検索対応：
                # 例：「肥爪」さんがログインしており、シート上に「⑤メンテナンス担当者(肥爪)」と書かれていれば一致と見なす
                if user_name in sheet_name_val or sheet_name_val in user_name:
                    if len(row) >= 5:
                        return row[4].strip()
    return "#"

# 画像をBase64変換
def _get_base64_img(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_img_html(file_name, emoji, width="100%"):
    data = _get_base64_img(file_name)
    if data:
        img_code = f'data:image/png;base64,{data}'
        return f'<img src="{img_code}" style="width:{width}; aspect-ratio:1/1; object-fit:contain; border-radius:15px; display: block; margin: 0 auto;">'
    return f'<div style="width:{width}; aspect-ratio:1/1; background:#f0f2f6; border-radius:15px; display:flex; align-items:center; justify-content:center; font-size:40px; margin: 0 auto;">{emoji}</div>'

# --- 画面表示処理 ---
if not st.session_state.get("login_status", False):
    st.warning("ログインしてください。")
    st.switch_page("app.py")
else:
    user_name = st.session_state.user_name
    user_branch = st.session_state.user_branch

    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem !important; max-width: 500px; }
        .button-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 15px 0; }
        .btn-item { text-align: center; text-decoration: none; display: block; color: black !important; }
        .btn-text { font-size: 12px; font-weight: bold; line-height: 1.2; text-align: center; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.write(f"👤 **{user_name} さん** ({user_branch})")
    
    if os.path.exists("1.png"): 
        st.image("1.png", use_container_width=True)

    # 🏢 拠点分岐 (神戸中央店)
    if user_branch == "神戸中央店":
        st.write("### 🏢 メニュー（神戸中央店）")

        # 1. メンテナンス入力
        maint_input_url = "https://docs.google.com/forms/d/e/1FAIpQLSc4E3L_UJkVxMMSTOYgcw3SJyoBixHoJfhe0WC-x1wbK6lsHw/viewform"
        
        # 2. メンテナンス確認
        maint_confirm_url = get_kobe_user_maintenance_url(user_name)
        
        # 3. キャンペーン情報
        campaign_name, campaign_url = get_kobe_campaign_info()

        # 画像からHTMLを生成
        b1 = get_img_html("3.png", "📄")
        b2 = get_img_html("4.png", "📋")
        b4 = get_img_html("5.png", "🧽")

        grid_html = f'''
            <div class="button-grid">
                <a class="btn-item" href="{maint_input_url}" target="_blank">
                    {b1}<p class="btn-text" style="margin-top:6px;">メンテナンス<br>入力</p>
                </a>
                <a class="btn-item" href="{maint_confirm_url}" target="_blank">
                    {b2}<p class="btn-text" style="margin-top:6px;">メンテナンス<br>確認</p>
                </a>
                <a class="btn-item" href="{campaign_url}" target="_blank">
                    {b4}<p class="btn-text" style="margin-top:6px;">{campaign_name}</p>
                </a>
            </div>
        '''
        st.markdown(grid_html, unsafe_allow_html=True)
    else:
        st.info(f"{user_branch}用の画面は現在準備中です。")

    # ログアウトボタン
    st.write("---")
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.login_status = False
        st.switch_page("app.py")
