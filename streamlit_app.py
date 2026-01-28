import streamlit as st
import pandas as pd

# 1. ページの設定（サイトの名前を Task memo に変更！）
st.set_page_config(page_title="Task memo", page_icon="📝")
st.title("📝 Task memo")

# 2. データの読み込み
def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        # 読み込むときに余計な加工をせず、そのまま読み込む（エラー回避）
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

# 3. 表示
if df is not None:
    st.subheader("タスク一覧")
    # スプレッドシートの中身をまるごと表示
    st.dataframe(df)
else:
    st.write("スプレッドシートのURLを確認してください。")

st.divider()
