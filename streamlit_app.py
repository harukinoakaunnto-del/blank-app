import streamlit as st
import pandas as pd

# 1. ページの設定（タイトルとアイコンは元のまま！）
st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

# 2. データを読み込む関数
def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"まだデータがないか、設定ミスかも！: {e}")
        return None

df = load_data()

# 3. データの表示（チェックが入っていたら色をつける設定）
if df is not None:
    # 色をつけるためのルール（done列がTRUEなら緑色にする）
    def color_done(row):
        if 'done' in row and str(row['done']).lower() == 'true':
            # 背景を薄い緑にして、文字に打ち消し線を引く
            return ['background-color: #d4edda; color: #155724; text-decoration: line-through;'] * len(row)
        return [''] * len(row)

    st.subheader("現在のタスク")
    # 色を適用して表示
    st.dataframe(df.style.apply(color_done, axis=1))
else:
    st.write("スプレッドシートを確認してください。")

# 4. 区切り線
st.divider()
