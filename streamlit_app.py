import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="進化するタスクメモ", page_icon="✅")
st.title("✅ 進化するタスクメモ")

# データの読み込み
def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"エラー: {e}")
        return None

df = load_data()

if df is not None:
    # --- ここからが「色を変える」魔法のコード ---
    def color_done(row):
        # もし「done」列がTrue（チェックあり）なら、背景を薄い緑にする
        if str(row['done']).lower() == 'true':
            return ['background-color: #d4edda; color: #155724; text-decoration: line-through;'] * len(row)
        return [''] * len(row)

    # 色を適用して表示
    st.subheader("現在のタスク（緑色は完了！）")
    st.dataframe(df.style.apply(color_done, axis=1))
    # ------------------------------------------
else:
    st.write("スプレッドシートを確認してください。")

st.divider()
