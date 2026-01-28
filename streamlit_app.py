import streamlit as st
import pandas as pd

# 1. ページの設定
st.set_page_config(page_title="Task memo", page_icon="📝")
st.title("📝 Task memo")

# 2. データの読み込み
def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

# 3. 表示（ここを修正！）
if df is not None:
    st.subheader("タスク一覧")
    
    # use_container_width=True で横幅いっぱいに広げ、
    # column_config で文字が途切れないように設定します
    st.dataframe(
        df, 
        use_container_width=True, 
        column_config={
            "task": st.column_config.TextColumn("task", width="large"),
        }
    )
else:
    st.write("スプレッドシートのURLを確認してください。")

st.divider()
