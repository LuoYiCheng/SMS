import streamlit as st
import json
import os
from utils.AccountManage import (
    hash_password,
)  # 假設您在 utils.AccountManage 中實現了 hash_password 函數

# 設定 JSON 檔案的路徑
SECRET_PATH = "data/users_db.json"

# 確保 JSON 檔案存在
if not os.path.exists(SECRET_PATH):
    with open(SECRET_PATH, "w", encoding="utf-8") as file:
        json.dump({}, file, indent=4, ensure_ascii=False)

# 檢查是否有管理員權限
if st.session_state.get("role") != "admin":
    st.error("您沒有權限訪問此頁面。")
    st.stop()

# 顯示現有的用戶列表
with open(SECRET_PATH, "r", encoding="utf-8") as file:
    users_db = json.load(file)

st.subheader("現有帳號")
if users_db:
    for username, details in users_db.items():
        st.write(f"- **{username}** ({details['role']})")
else:
    st.write("目前尚無帳號。")

# 新增用戶表單
st.subheader("新增帳號")
new_username = st.text_input("新帳號名稱")
new_password = st.text_input("密碼", type="password")
new_role = st.selectbox("角色", ["employee", "admin"])

if st.button("新增帳號"):
    if new_username in users_db:
        st.error("此帳號已存在！")
    elif not new_username or not new_password:
        st.error("帳號或密碼不能為空！")
    else:
        hashed_password = hash_password(new_password)
        users_db[new_username] = {
            "password": hashed_password.decode("utf-8"),
            "role": new_role,
        }
        with open(SECRET_PATH, "w", encoding="utf-8") as file:
            json.dump(users_db, file, indent=4, ensure_ascii=False)
        st.success(f"帳號 `{new_username}` 已新增！")

# 刪除用戶
st.subheader("刪除帳號")
delete_username = st.selectbox("選擇帳號", list(users_db.keys()))

if st.button("刪除帳號"):
    if delete_username:
        users_db.pop(delete_username)
        with open(SECRET_PATH, "w", encoding="utf-8") as file:
            json.dump(users_db, file, indent=4, ensure_ascii=False)
        st.success(f"帳號 `{delete_username}` 已刪除！")
    else:
        st.error("請選擇一個帳號！")

# 修改用戶角色
st.subheader("修改帳號角色")
edit_username = st.selectbox("選擇要修改角色的帳號", list(users_db.keys()))
if edit_username:
    current_role = users_db[edit_username]["role"]
    new_role = st.selectbox(
        "新角色",
        ["employee", "admin"],
        index=["employee", "admin"].index(current_role),
    )

    if st.button("修改角色"):
        if current_role == new_role:
            st.warning("新角色與當前角色相同，無需修改。")
        else:
            users_db[edit_username]["role"] = new_role
            with open(SECRET_PATH, "w", encoding="utf-8") as file:
                json.dump(users_db, file, indent=4, ensure_ascii=False)
            st.success(f"帳號 `{edit_username}` 的角色已修改為 `{new_role}`！")
