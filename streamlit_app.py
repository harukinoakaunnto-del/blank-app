import streamlit as st
import pandas as pd

# 1. ページの設定（タイトルとアイコン）
st.set_page_config(page_title="絶対に消えないタスクメモ", page_icon="📚")
st.title("📚 絶対に消えないタスクメモ")

# 2. データを読み込む関数の定義
def load_data():
    try:
        # シークレットからURLを取得
        raw_url = st.secrets["GSHEET_URL"]
        # URLをCSV書き出し用に変換
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        # データを読み込んで返す
        return pd.read_csv(csv_url)
    except Exception as e:
        # エラーが起きた場合は画面に表示する
        st.error(f"まだデータがないか、設定ミスかも！: {e}")
        return None

# 3. データの表示
df = load_data()

st.subheader("現在のタスク")
if df is not None:
    st.dataframe(df)
else:
    st.write("スプレッドシートを確認してください。")

# 4. 区切り線
st.divider()
