import streamlit as st
import pandas as pd

# 1. ページの設定
st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        df = pd.read_csv(csv_url)
        
        # --- 🛡️ KeyError対策：列名を強制的に上書き ---
        # スプレッドシートの左から順に名前を固定します
        # A:task, B:date, C:done, D:deadline, E:priority
        new_cols = ['task', 'date', 'done', 'deadline', 'priority']
        df.columns = new_cols[:len(df.columns)]
        
        # 足りない列がある場合の補完
        for c in new_cols:
            if c not in df.columns:
                df[c] = ""

        # 日付とチェックの状態を整理
        df['deadline_dt'] = pd.to_datetime(df['deadline'], errors='coerce')
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

    # フィルタリング
    if not show_completed:
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

    # 残り日数の計算（今日の日付を取得）
    now = pd.Timestamp.now().normalize()
    display_df['あと何日'] = (display_df['deadline_dt'] - now).dt.days
    
    # 重要度（数字）で並び替え
    display_df['priority'] = pd.to_numeric(display_df['priority'], errors='coerce').fillna(99)
    display_df = display_df.sort_values(by=['priority', 'deadline_dt'])

    # --- 🎨 色設定（赤く光るギミック！） ---
    def color_rows(row):
        style = [''] * len(row)
        if row['done_flag']:
            # 完了：緑
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        elif pd.notnull(row['あと何日']) and row['あと何日'] < 0:
            # 期限切れ：赤く光る（太字＋赤背景）
            style = ['background-color: #ffcccc; color: #cc0000; font-weight: bold; border: 2px solid red;'] * len(row)
        elif pd.notnull(row['あと何日']) and 0 <= row['あと何日'] <= 3:
            # 3日以内：警告（黄色）
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
        return style

    st.subheader("現在のタスク")
    if not display_df.empty:
        # 表示する列（名前を固定したので安心）
        view_cols = ['task', 'date', 'deadline', 'あと何日', 'priority', 'done']
        st.dataframe(display_df[view_cols].style.apply(color_rows, axis=1))
    else:
        st.info("完了していないタスクはありません！お見事！")

else:
    st.write("スプレッドシートの準備をしてね。")

st.divider()
