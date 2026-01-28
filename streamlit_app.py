import streamlit as st
import pandas as pd

st.set_page_config(page_title="消えないタスクメモ", page_icon="📚")
st.title("📚 消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        # 見出しを読み込まず、データだけ読み込む
        df = pd.read_csv(csv_url)
        
        # 列の名前を「番号」で強制的に付け直す
        # これでスプレッドシートの1行目に何が書いてあっても関係なくなります！
        new_names = ['task', 'date', 'done', 'deadline', 'priority']
        df.columns = new_names[:len(df.columns)]
        
        # データの整理
        df['deadline_dt'] = pd.to_datetime(df['deadline'], errors='coerce')
        df['done_flag'] = df['done'].astype(str).str.lower().isin(['true', 'checked', '1'])
        df = df.dropna(subset=['task'])
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

df = load_data()

if df is not None:
    # 完了済みを隠す設定
    show_completed = st.sidebar.checkbox("完了したタスクも表示する", value=False)
    display_df = df[df['done_flag'] == False].copy() if not show_completed else df.copy()

    # 進捗バー
    done_count = len(df[df['done_flag'] == True])
    total_count = len(df)
    st.write(f"全体の進捗: {done_count} / {total_count}")
    st.progress(done_count / total_count if total_count > 0 else 0)

    # 期限計算
    now = pd.Timestamp.now().normalize()
    display_df['あと何日'] = (display_df['deadline_dt'] - now).dt.days

    # 色をつけるルール
    def color_rows(row):
        style = [''] * len(row)
        if row['done_flag']:
            style = ['background-color: #d4edda; text-decoration: line-through; color: #155724;'] * len(row)
        elif pd.notnull(row['あと何日']) and row['あと何日'] < 0:
            # 期限切れは赤く光る！
            style = ['background-color: #ffcccc; color: #cc0000; font-weight: bold; border: 2px solid red;'] * len(row)
        elif pd.notnull(row['あと何日']) and 0 <= row['あと何日'] <= 3:
            style = ['background-color: #fff3cd; color: #856404; font-weight: bold;'] * len(row)
        return style

    st.subheader("現在のタスク")
    # 表示する列を指定（ここもKeyErrorが出ないように慎重に選んでいます）
    cols = [c for c in ['task', 'date', 'deadline', 'あと何日', 'priority'] if c in display_df.columns]
    st.dataframe(display_df[cols].style.apply(color_rows, axis=1))

else:
    st.write("スプレッドシートを確認してください。")
