import streamlit as st
import pandas as pd

st.set_page_config(page_taitle = "消えないタスクメモ" , page_icon="📚")
st.title("📚絶対消えないタスクメモ")

def load_data():
    try:
        raw_url = st.secrets["GSHEET_URL"]
        base_url = raw_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"

        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"まだデータがないか、設定ミスかも！:{e}")
        return pd.DataFrame(columns=['task','date'])

df = load_data() 

st.subheader("現在のタスク")
if df.empty:
    st.info("スプレッドシートの二枚目に何か書いてみて！")
else:
    st.dataframe(df, use_container_width=True)
    
st.divider()
st.write("### 使い方")
st.write("1.PCでスプレッドシートの二行目に文字を入れる")
st.write("2.スマホでこの画面を更新する")

if st.button("最新の状態にする"):
    st.rerun()
