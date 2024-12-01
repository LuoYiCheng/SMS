import streamlit as st
from utils.AccountManage import load_users, verify_password

# 網頁配置
st.set_page_config(
    page_title="SMS管理系統",
    page_icon=":wrench:",
    layout="wide",
    initial_sidebar_state="auto",
)


# 用戶數據庫
users_db = load_users()

# 初始化 session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# 登入界面
st.title("🔑權限登入")

username = st.text_input("用戶名")
password = st.text_input("密碼", type="password")

if st.button("登入"):
    if username in users_db:
        stored_password = users_db[username]["password"]
        if verify_password(password, stored_password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users_db[username]["role"]
            st.success(f"登入成功🥳 歡迎 {username}，請點擊左方功能頁面使用本服務！")
        else:
            st.session_state.logged_in = False
            st.session_state.role = None
            st.error("登入失敗，密碼錯誤！")
    else:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.error("帳號不存在！")
