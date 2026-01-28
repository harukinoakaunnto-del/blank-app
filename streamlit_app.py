import streamlit as st
import pandas as pd

# 1. ページの設定
st.set_page_config(page_title="タスクメモ", page_icon="📚")
st.title("📚 タスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        df = pd.read_csv(csv_url)
        # 日付とチェックの状態を整理
        df['deadline'] = pd.to_datetime(df['deadline'])
        df['done_flag'] = df['done'].astype(str).str.lower() == 'true'
        # タスク名が空の行は削除
        df = df.dropna(subset=['task'])
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

if df is not None:
    # --- サイドバーで「完了済みを表示するか」選べるようにする ---
    show_completed = st.sidebar.checkbox("完了したタスクも表示する", value=False)

    # フィルタリング（ここが「削除（非表示）」の魔法！）
    if not show_completed:
        # チェックが入っていないものだけを残す
        display_df = df[df['done_flag'] == False].copy()
    else:
        display_df = df.copy()

    # --- 進捗バー ---
    done_count = len(df[df['done_flag'] == True])
    total_count = len(df)
    progress = done_count / total_count if total_count > 0 else 0
    st.write(f"全体の進捗: {done_count} / {total_count}")
    st.progress(progress)

    # --- 検索・計算・並び替え ---
    search_term = st.text_input("タスクを検索🔍", "")
    if search_term:
        display_df = display_df[display_df['task'].str.contains(search_term, na=False)]

    display_df['あと何日'] = (display_df['deadline'] - pd.Timestamp.now()).dt.days + 1
    display_df = display_df.sort_values(by=['priority', 'deadline'])

    # 表示用の色設定
    def color_rows(row):
        style = [''] * len(row)
        if row['done_flag']:
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        elif 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
        return style

    st.subheader("現在のタスク")
    if not display_df.empty:
        st.dataframe(display_df[['task', 'date', 'あと何日', 'priority', 'done']].style.apply(color_rows, axis=1))
    else:
        st.info("完了していないタスクはありません！お見事！")

else:
    st.write("スプレッドシートの準備をしてね。")

st.divider()
