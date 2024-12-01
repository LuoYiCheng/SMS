import json
import bcrypt


# 初始化用戶數據（僅需執行一次以加密密碼）
def initialize_users():
    users_db = {
        "lohas": {
            "password": bcrypt.hashpw(
                "lohas202412".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "role": "admin",
        },
        "user001": {
            "password": bcrypt.hashpw(
                "user001202412".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "role": "employee001",
        },
        "user002": {
            "password": bcrypt.hashpw(
                "user002202412".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "role": "employee002",
        },
    }
    with open(r"data/users_db.json", "w", encoding="utf-8") as file:
        json.dump(users_db, file, indent=4, ensure_ascii=False)


initialize_users()
