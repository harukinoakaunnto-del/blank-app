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
        df = pd.read_csv(csv_url)
        
        # --- 🛡️ KeyError対策：列名を強制的に固定 ---
        # スプレッドシートの左から順：A:task, B:date, C:done, D:deadline, E:priority
        new_cols = ['task', 'date', 'done', 'deadline', 'priority']
        df.columns = new_cols[:len(df.columns)]
        
        # データの整理
        df['deadline_dt'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['done_flag'] = df['done'].astype(str).str.lower().isin(['true', 'checked', '1'])
        df = df.dropna(subset=['task'])
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

# 3. 表示
if df is not None:
    # --- 完了したタスクを非表示にする（チェックが入っていないものだけ抽出） ---
    display_df = df[df['done_flag'] == False].copy()

    # 現在の時刻を取得
    now = pd.Timestamp.now().normalize()
    # 期限までの日数を計算
    display_df['あと何日'] = (display_df['deadline_dt'] - now).dt.days

    # --- 🎨 色をつけるギミック ---
    def color_rows(row):
        style = [''] * len(row)
        # 期限切れ（赤く光る！）
        if pd.notnull(row['deadline_dt']) and row['deadline_dt'] < now:
            style = ['background-color: #ffcccc; color: #cc0000; font-weight: bold;'] * len(row)
        # 3日以内（黄色）
        elif pd.notnull(row['あと何日']) and 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404;'] * len(row)
        return style

    st.subheader("タスク一覧")
    
    # 実際に存在する列だけを表示（エラー回避）
    show_cols = [c for c in ['task', 'date', 'deadline', 'あと何日', 'priority'] if c in display_df.columns]
    
    st.dataframe(
        display_df[show_cols].style.apply(color_rows, axis=1),
        use_container_width=True
    )
    
    if display_df.empty:
        st.info("完了していないタスクはありません！✨")
else:
    st.write("スプレッドシートを確認してください。")

st.divider()
