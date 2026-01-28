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
        
        # --- 🛡️ ここで列の名前をチェックしてエラーを防ぐ ---
        # 列名の前後の空白を消す
        df.columns = df.columns.str.strip()
        
        # 必要な列がなければ空で作っておく（KeyError対策）
        cols = ['task', 'done', 'deadline', 'priority', 'date']
        for c in cols:
            if c not in df.columns:
                df[c] = "" 
        
        # データ変換
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['done_flag'] = df['done'].astype(str).str.lower() == 'true'
        df = df.dropna(subset=['task'])
        return df
    except Exception as e:
        st.error(f"読み込みエラーが発生しました: {e}")
        return None

df = load_data()

if df is not None:
    show_completed = st.sidebar.checkbox("完了したタスクも表示する", value=False)

    if not show_completed:
        display_df = df[df['done_flag'] == False].copy()
    else:
        display_df = df.copy()

    # 進捗バー
    done_count = len(df[df['done_flag'] == True])
    total_count = len(df)
    st.write(f"全体の進捗: {done_count} / {total_count}")
    st.progress(done_count / total_count if total_count > 0 else 0)

    # 検索
    search_term = st.text_input("タスクを検索🔍", "")
    if search_term:
        display_df = display_df[display_df['task'].astype(str).str.contains(search_term, na=False)]

    # 残り日数の計算
    now = pd.Timestamp.now().normalize()
    display_df['あと何日'] = (display_df['deadline'] - now).dt.days
    
    # 並び替え（priorityが空だとエラーになるので文字に変換して処理）
    display_df['priority'] = pd.to_numeric(display_df['priority'], errors='coerce').fillna(99)
    display_df = display_df.sort_values(by=['priority', 'deadline'])

    # 色をつけるルール
    def color_rows(row):
        style = [''] * len(row)
        if row['done_flag']:
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        elif pd.notnull(row['あと何日']) and row['あと何日'] < 0:
            style = ['background-color: #ffcccc; color: #cc0000; font-weight: bold; border: 2px solid red;'] * len(row)
        elif pd.notnull(row['あと何日']) and 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
        return style

    st.subheader("現在のタスク")
    view_columns = ['task', 'date', 'deadline', 'あと何日', 'priority', 'done']
    
    # 表示する列が実際に存在するものだけに絞る
    actual_cols = [c for c in view_columns if c in display_df.columns]
    
    if not display_df.empty:
        st.dataframe(display_df[actual_cols].style.apply(color_rows, axis=1))
    else:
        st.info("やるべきことは全部終わりました！")
else:
    st.write("スプレッドシートの準備をしてね。")
