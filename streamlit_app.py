import streamlit as st
import pandas as pd

st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        # 見出しを無視して読み込み、新しく名前を割り当てる
        df = pd.read_csv(csv_url, header=0)
        
        # 列の名前を強制的に上書き（左から順に：タスク, 日付, 完了, 期限, 重要度）
        # スプレッドシートのA, B, C, D, E列の順番に合わせています
        expected_cols = ['task', 'date', 'done', 'deadline', 'priority']
        
        # 読み込んだデータの列数に合わせて名前を付ける
        df.columns = expected_cols[:len(df.columns)]
        
        # 必要な列が足りない場合の補完
        for c in expected_cols:
            if c not in df.columns:
                df[c] = ""

        # データ変換
        df['deadline_dt'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['done_flag'] = df['done'].astype(str).str.lower().isin(['true', 'checked', '1'])
        df = df.dropna(subset=['task'])
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

if df is not None:
    show_completed = st.sidebar.checkbox("完了したタスクも表示する", value=False)
    display_df = df[df['done_flag'] == False].copy() if not show_completed else df.copy()

    # 進捗バー
    done_count = len(df[df['done_flag'] == True])
    total_count = len(df)
    st.write(f"全体の進捗: {done_count} / {total_count}")
    st.progress(done_count / total_count if total_count > 0 else 0)

    # 検索
    search_term = st.text_input("タスクを検索🔍", "")
    if search_term:
        display_df = display_df[display_df['task'].astype(str).str.contains(search_term, na=False)]

    # 期限計算
    now = pd.Timestamp.now().normalize()
    display_df['あと何日'] = (display_df['deadline_dt'] - now).dt.days
    
    # 並び替え
    display_df['priority_num'] = pd.to_numeric(display_df['priority'], errors='coerce').fillna(99)
    display_df = display_df.sort_values(by=['priority_num', 'deadline_dt'])

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
    # 表示する列（名前を固定しているので安心！）
    cols_to_show = ['task', 'date', 'deadline', 'あと何日', 'priority', 'done']
    st.dataframe(display_df[cols_to_show].style.apply(color_rows, axis=1))

else:
    st.write("スプレッドシートを確認してください。")
