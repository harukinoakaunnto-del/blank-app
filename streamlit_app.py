import streamlit as st
import pandas as pd

# 1. ページの設定
st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

# 2. データの読み込み
def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        # 読み込むときに、列の名前を気にせず「一番上の行」をタイトルとして読み込む
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

# 3. 表示
if df is not None:
    st.subheader("現在のタスク一覧")
    # そのままスプレッドシートの内容を全部出す！（これが一番エラーになりません）
    st.dataframe(df)
else:
    st.write("スプレッドシートが見つからないか、URLが間違っているかもしれません。")

st.divider()
