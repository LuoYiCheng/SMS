import json
import bcrypt

SECRET_PATH = r"data/users_db.json"


# 從 JSON 文件讀取用戶數據
def load_users():
    with open(SECRET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# 加密密碼
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


# 驗證密碼
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# 新增用戶並加密密碼
def add_user(username, password, role):
    hashed_password = hash_password(password)  # 將密碼加密
    with open(SECRET_PATH, "r+", encoding="utf-8") as file:
        users_db = json.load(file)
        users_db[username] = {"password": hashed_password.decode("utf-8"), "role": role}
        file.seek(0)
        json.dump(users_db, file, indent=4, ensure_ascii=False)
        file.truncate()


def authenticate_user(username, password):
    with open(SECRET_PATH, "r", encoding="utf-8") as file:
        users_db = json.load(file)
    if username in users_db:
        stored_password = users_db[username]["password"]
        if verify_password(password, stored_password.encode("utf-8")):
            return users_db[username]["role"]  # 返回用戶角色
    return None  # 驗證失敗
