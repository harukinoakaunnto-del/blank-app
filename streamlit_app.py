import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ページの設定
st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        df = pd.read_csv(csv_url)
        
        # タスク名が空の行を削除
        df = df.dropna(subset=['task'])
        
        # 日付データの変換（エラーがあっても無視して変換する設定）
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['done_flag'] = df['done'].astype(str).str.lower() == 'true'
        
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

if df is not None:
    # 完了済みを表示するかどうかのスイッチ
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

    # 現在の時刻を取得
    now = pd.Timestamp.now().normalize()
    
    # 残り日数の計算（期限 - 今日）
    display_df['あと何日'] = (display_df['deadline'] - now).dt.days
    
    # 重要度と期限で並び替え
    display_df = display_df.sort_values(by=['priority', 'deadline'])

    # --- 💡 赤く光る（色をつける）ギミックのルール ---
    def color_rows(row):
        style = [''] * len(row)
        
        # 1. 完了済み（緑）
        if row['done_flag']:
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        
        # 2. 期限切れ（赤く光る！）
        elif row['あと何日'] < 0:
            style = ['background-color: #ffcccc; color: #cc0000; font-weight: bold; border: 2px solid red;'] * len(row)
            
        # 3. 期限間近（3日以内は黄色）
        elif 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
            
        return style

    st.subheader("現在のタスク")
    
    # 表示する列の整理
    view_columns = ['task', 'date', 'deadline', 'あと何日', 'priority', 'done']
    
    if not display_df.empty:
        st.dataframe(display_df[view_columns].style.apply(color_rows, axis=1))
    else:
        st.info("やるべきことは全部終わりました！")

else:
    st.write("スプレッドシートの準備をしてね。")

st.divider()
