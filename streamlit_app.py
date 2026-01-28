import streamlit as st
import pandas as pd
from datetime import datetime

# ページの設定
st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        df = pd.read_csv(csv_url)
        # 日付データを計算できるように変換
        df['deadline'] = pd.to_datetime(df['deadline'])
        return df
    except Exception as e:
        st.error(f"設定を確認してね！: {e}")
        return None

df = load_data()

if df is not None:
    # --- 4. 進捗バー ---
    done_count = len(df[df['done'].astype(str).str.lower() == 'true'])
    total_count = len(df)
    progress = done_count / total_count if total_count > 0 else 0
    st.write(f"全体の進捗: {done_count} / {total_count}")
    st.progress(progress)

    # --- 3. 検索機能 ---
    search_term = st.text_input("タスクを検索🔍", "")
    if search_term:
        df = df[df['task'].str.contains(search_term, na=False)]

    # --- 1 & 2. 計算と並び替え ---
    # 残り日数を計算
    df['あと何日'] = (df['deadline'] - pd.Timestamp.now()).dt.days + 1
    # 重要度(priority)で並び替え
    df = df.sort_values(by=['priority', 'deadline'])

    # 色をつけるルール
    def color_rows(row):
        style = [''] * len(row)
        # チェックあり(完了)は緑
        if str(row['done']).lower() == 'true':
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        # 期限が3日以内なら警告色（黄色）
        elif 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
        return style

    st.subheader("現在のタスク（重要度＆期限順）")
    # 不要な列を隠して表示
    display_df = df[['task', 'date', 'あと何日', 'priority', 'done']]
    st.dataframe(display_df.style.apply(color_rows, axis=1))

else:
    st.write("スプレッドシートの準備をしてね。")

st.divider()
